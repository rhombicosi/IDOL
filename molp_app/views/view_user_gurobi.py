from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render

from molp_app.models import UserProblem, UserProblemParameters

import gurobipy as gbp
from gurobipy import *
import numpy as np
import time

from django.conf import settings


@login_required
def submit_user_gurobi_problem(request, pk):

    if request.method == 'POST':
        problem = UserProblem.objects.get(pk=pk)
        lpfile = problem.xml.path

        model = read(lpfile)

        # get # of objectives
        NumOfObj = model.getAttr(GRB.Attr.NumObj)
        print('Number of objectives: ', NumOfObj)

        # get # of variables
        NumOfVars = model.numVars
        print('Number of variables: ', NumOfVars)

        # get sense
        sense = model.ModelSense
        if sense == -1:
            print('Model sense is MAXIMIZE')
        elif sense == 0:
            print('Model sense is MINIMIZE')
        else:
            print('Sense is not recognized')

        # get vars and constrs as Gurobi Var and Constr objects
        dvars = model.getVars()
        constrs = model.getConstrs()
        numOfConstrs = len(constrs)

        print("number of constraints {}".format(numOfConstrs))

        for c in constrs:
            print('constraint {} sense is {}, rhs is {}'.format(c.ConstrName, c.Sense, c.RHS))

        # get objectives params
        objParams = []
        for i in range(NumOfObj):
            model.Params.ObjNumber = i
            objParams.append(model.getAttr('ObjN', dvars))
        print('Objectives coefficients: ', objParams)

        # get objectives weights
        objWeights = []
        for i in range(NumOfObj):
            model.Params.ObjNumber = i
            objWeights.append(model.getAttr('ObjNWeight'))
        print('Objectives weights: ', objWeights)

        # get constraints parameters
        A = model.getA()
        AA = A.toarray()

        print(A.toarray())

        # RHS
        B = model.getAttr('RHS')

        print('RHS', B)

        # Create chebyshev model
        mo = gbp.Model('chebknap')

        # new variables
        Elem = {} # initial problem variables
        Fun = {} # new variables for each objective
        S = {} # new objective variable

        ItemSet = range(NumOfObj, len(dvars) + NumOfObj)
        ObjSet = range(NumOfObj)
        SSet = range(0, 1)

        ystar = []
        for i in range(NumOfObj):
            ystar.append(sum(objParams[i]))
        ystar
        lmbd = objWeights
        rho = 0.001

        Fun.update(mo.addVars(ObjSet, vtype=GRB.CONTINUOUS, name='f'))
        Elem.update(mo.addVars(ItemSet, vtype=GRB.BINARY, name='El'))

        # # name_0 = 'chebknap_0'
        # # # mo.write(settings.STATIC_TMP + '/' + name_0 + '.lp')
        # # mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_0 + '.lp')

        # convert objectives to constraints
        for i in range(NumOfObj):
            mo.addConstr(-Fun[i] + sum(Elem[k] * objParams[i][k - NumOfObj] for k in ItemSet) == 0, name='ObjC' + str(i))

        # add initial constraints
        i = 0
        for c in constrs:
            mo.addConstr(sum(Elem[k] * AA[i][k - NumOfObj] for k in ItemSet), c.Sense, c.RHS, c.ConstrName)
            i += 1

        # add artificial variable s
        # S.update(mo.addVars(SSet, vtype=GRB.CONTINUOUS, name='s'))
        S = mo.addVars(SSet, vtype=GRB.CONTINUOUS, name='s')
        mo.update()

        print('S[0]: {}'.format(S[0]))

        # add chebyshev constraints
        sum_term = 0
        for i in range(NumOfObj):
            sum_term += rho*(ystar[i] - Fun[i])
            print('sum term {} is {}'.format(i, sum_term))

        weight_term = []
        for i in range(NumOfObj):
            weight_term.append(lmbd[i]*(ystar[i] - Fun[i]))

        print('weight terms')
        for i in weight_term:
            print(i)

        mo.addConstrs(
            (S[0] - weight_term[i] - sum_term >= 0
             for i in range(NumOfObj)), name='CH')

        mo.setObjective(S[0], GRB.MINIMIZE)

        name = 'chebknap'
        timestr = time.strftime("%Y%m%d-%H%M%S")
        temp_path = settings.MEDIA_ROOT + '/problems/chebyshev/' + name + timestr + '_temp.lp'

        # write model into temporary file with gurobi
        mo.write(temp_path)

        # add file to the model
        f = open(temp_path)
        problem.chebyshev.save(name + timestr + '.lp', File(f))
        f.close()

        # remove temporary file
        os.remove(temp_path)

        mo.optimize()

        # write solution
        sol_name = 'solution'
        sol_timestr = time.strftime("%Y%m%d-%H%M%S")
        sol_temp_path = settings.MEDIA_ROOT + '/problems/solutions/' + sol_name + sol_timestr + '_temp.sol'

        mo.write(sol_temp_path)

        # add file to the model
        f_sol = open(sol_temp_path)
        problem.result.save(sol_name + sol_timestr + '.sol', File(f_sol))
        f_sol.close()

        # remove temporary file
        os.remove(sol_temp_path)

        if problem.result:
            print('if result url {}'.format(problem.result.url))

        for v in mo.getVars():
            print('{} {}'.format(v.varName, v.x))

    return render(request, 'user_problems.html')


