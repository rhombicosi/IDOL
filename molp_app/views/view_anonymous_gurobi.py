# from django.shortcuts import redirect, render
# from molp_app.utilities.file_helper import *
#
# import gurobipy as gbp
# from gurobipy import *
# import time
# import numpy as np
#
# import subprocess
# import os
#
#
# def submit_gurobi_problem(request, pk):
#     problem = Problem.objects.get(pk=pk)
#     solver = problem.solver
#
#     if request.method == 'POST':
#
#         params = problem.parameters.all()
#         lpfile = problem.xml.path
#
#         model = read(lpfile)
#
#         # get # of objectives
#         NumOfObj = model.getAttr(GRB.Attr.NumObj)
#         print('Number of objectives: ', NumOfObj)
#
#         # get # of variables
#         NumOfVars = model.numVars
#         print('Number of variables: ', NumOfVars)
#
#         # get sense
#         sense = model.ModelSense
#         if sense == -1:
#             print('Model sense is MAXIMIZE')
#         elif sense == 0:
#             print('Model sense is MINIMIZE')
#         else:
#             print('Sense is not recognized')
#
#         # get vars and constrs as Gurobi Var and Constr objects
#         dvars = model.getVars()
#         constrs = model.getConstrs()
#         numOfConstrs = len(constrs)
#
#         print("number of constraints {}".format(numOfConstrs))
#
#         for c in constrs:
#             print('constraint {} sense is {}, rhs is {}'.format(c.ConstrName, c.Sense, c.RHS))
#
#         # get objectives params
#         objParams = []
#         for i in range(NumOfObj):
#             model.Params.ObjNumber = i
#             objParams.append(model.getAttr('ObjN', dvars))
#         print('Objectives coefficients: ', objParams)
#
#         # get weights
#         objWeights = []
#         if params:
#             # get weights from txt file
#             if params[0].weights:
#                 w_path = settings.MEDIA_ROOT + '/problems/parameters/weights/'
#                 w_name = os.path.basename(params[0].weights.path)
#                 weights = read_txt(w_path, w_name)
#
#                 for i in range(len(weights)):
#                     model.Params.ObjNumber = i
#                     objWeights.append(weights[i])
#                 print('Objectives weights from file: ', objWeights)
#         else:
#             # set equal weights programmatically
#             weights = np.full(NumOfObj, 1 / NumOfObj)
#             for i in range(len(weights)):
#                 model.Params.ObjNumber = i
#                 objWeights.append(weights[i])
#             print('Objectives weights assigned by program: ', objWeights)
#
#         # get constraints parameters
#         A = model.getA()
#         AA = A.toarray()
#         print(A.toarray())
#
#         # RHS
#         B = model.getAttr('RHS')
#         print('RHS', B)
#
#         # Create chebyshev model
#         mo = gbp.Model('chebknap')
#
#         # new variables
#         Elem = {} # initial problem variables
#         Fun = {} # new variables for each objective
#         S = {} # new objective variable
#
#         ItemSet = range(NumOfObj, len(dvars) + NumOfObj)
#         ObjSet = range(NumOfObj)
#         SSet = range(0, 1)
#
#         # TODO: obtain a reference point from file or
#         #  calculated as a solution to single objective problems
#         ystar = []
#         for i in range(NumOfObj):
#             ystar.append(sum(objParams[i]))
#         ystar
#         lmbd = objWeights
#         rho = 0.001
#
#         Fun.update(mo.addVars(ObjSet, vtype=GRB.CONTINUOUS, name='f'))
#         Elem.update(mo.addVars(ItemSet, vtype=GRB.BINARY, name='El'))
#
#         # convert objectives to constraints
#         for i in range(NumOfObj):
#             mo.addConstr(-Fun[i] + sum(Elem[k] * objParams[i][k - NumOfObj] for k in ItemSet) == 0, name='ObjC' + str(i))
#
#         # add initial constraints
#         i = 0
#         for c in constrs:
#             mo.addConstr(sum(Elem[k] * AA[i][k - NumOfObj] for k in ItemSet), c.Sense, c.RHS, c.ConstrName)
#             i += 1
#
#         # add artificial variable s
#         # S.update(mo.addVars(SSet, vtype=GRB.CONTINUOUS, name='s'))
#         S = mo.addVars(SSet, vtype=GRB.CONTINUOUS, name='s')
#         mo.update()
#
#         print('S[0]: {}'.format(S[0]))
#
#         # add chebyshev constraints
#         sum_term = 0
#         for i in range(NumOfObj):
#             sum_term += rho*(ystar[i] - Fun[i])
#             print('sum term {} is {}'.format(i, sum_term))
#
#         weight_term = []
#         for i in range(NumOfObj):
#             weight_term.append(lmbd[i]*(ystar[i] - Fun[i]))
#
#         print('weight terms')
#         for i in weight_term:
#             print(i)
#
#         mo.addConstrs(
#             (S[0] - weight_term[i] - sum_term >= 0
#              for i in range(NumOfObj)), name='CH')
#
#         mo.setObjective(S[0], GRB.MINIMIZE)
#
#         # save chebyshev scalarization into .lp file
#         temp_path, f_path = save_files('chebknap', '/problems/chebyshev/', 'lp', 'chebyshev', problem, mo)
#         in_path = temp_path + f_path
#         print(in_path)
#
#         # optimization with subprocess
#         wd = os.getcwd()
#         proj_env = os.environ.copy()
#         proj_env["PATH"] = proj_env["PATH"] + ";" + wd + "\\;"
#         proj_env['PYTHONPATH'] = wd
#
#         key = str(pk)
#         subprocess.Popen(["python", "molp_app\\utilities\\optimize.py", "-i", in_path, "-pk", key], env=proj_env, cwd=wd)
#
#         # for v in mo.getVars():
#         #     print('{} {}'.format(v.varName, v.x))
#
#         context = get_context()
#         context.update({'solver': solver})
#
#         # problems = Problem.objects.all()
#         # problems_neos = problems.filter(solver="NEOS")
#         # problems_gurobi = problems.filter(solver="Gurobi")
#         #
#         # {
#         #     'problems': problems,
#         #     'problems_neos': problems_neos,
#         #     'problems_gurobi': problems_gurobi,
#         #     'solver': solver
#         # }
#
#     return render(request, 'problem_list.html', context)
#
#
# def create_gurobi_problem(pk, weights):
#     problem = Problem.objects.get(pk=pk)
#     lpfile = problem.xml.path
#     lpname = os.path.basename(lpfile)
#
#     model = read(lpfile)
#
#     for i in range(len(weights)):
#         model.Params.ObjNumber = i
#         model.setAttr('ObjNWeight', weights[i])
#         print('weights[{}] is {}'.format(i, weights[i]))
#
#     p = Problem()
#
#     save_files(lpname, '/problems/xmls/', 'lp', 'xml', p, model)
#     timestr = time.strftime("%Y%m%d-%H%M%S")
#     p.title = problem.title + '_' + timestr
#     p.solver = problem.solver
#     p.save()
#
#     return p
#
#
# def generate_single_problems(request, pk):
#     if request.method == 'POST':
#         pass
#
#     problems = Problem.objects.all()
#     problems_neos = problems.filter(solver="NEOS")
#     problems_gurobi = problems.filter(solver="Gurobi")
#
#     return render(request, 'problem_list.html', {
#         'problems': problems,
#         'problems_neos': problems_neos,
#         'problems_gurobi': problems_gurobi
#     })
#
