from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.shortcuts import redirect, render

from molp_app.models import UserProblem

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
        SSet = range(1)

        ystar = []
        for i in range(NumOfObj):
            ystar.append(sum(objParams[i]))
        ystar
        lmbd = objWeights
        rho = 0.001

        Fun.update(mo.addVars(ObjSet, vtype=GRB.CONTINUOUS, name='f'))
        Elem.update(mo.addVars(ItemSet, vtype=GRB.BINARY, name='El'))

        name_0 = 'chebknap_0'
        # mo.write(settings.STATIC_TMP + '/' + name_0 + '.lp')
        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_0 + '.lp')

        # convert objectives to constraints
        for i in range(NumOfObj):
            mo.addConstr(-Fun[i] + sum(Elem[k] * objParams[i][k - NumOfObj] for k in ItemSet) == 0, name='ObjC' + str(i))

        # for test purpose
        name_1 = 'chebknap_1'
        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_1 + '.lp')

        # add initial constraints
        for c in constrs:
            mo.addConstr(sum(Elem[k] * AA[0][k - NumOfObj] for k in ItemSet), c.Sense, c.RHS, c.ConstrName)

        # for test purpose
        name_2 = 'chebknap_2'
        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_2 + '.lp')

        # add artificial variable s
        S.update(mo.addVars(SSet, vtype=GRB.CONTINUOUS, name='s'))

        # for test purpose
        name_3 = 'chebknap_3'
        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_3 + '.lp')

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

        # for test purpose
        name_4 = 'chebknap_4'
        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name_4 + '.lp')

        mo.setObjective(S[0], GRB.MINIMIZE)

        name = 'chebknap'
        timestr = time.strftime("%Y%m%d-%H%M%S")

        mo.write(settings.MEDIA_ROOT + '/problems/chebyshev/' + name + timestr + '.lp')

        # Using File
        f = open(settings.MEDIA_ROOT + '/problems/chebyshev/' + name + timestr + '.lp')
        problem.chebyshev.save(name + timestr + '.lp', File(f))

        mo.optimize()

        for v in mo.getVars():
            print('%s %g' % (v.varName, v.x))

    return render(request, 'user_problems.html')
