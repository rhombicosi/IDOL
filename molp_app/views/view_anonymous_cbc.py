from django.shortcuts import render

from molp_app.utilities.file_helper import *
from molp_app.utilities.parse_gurobi_multi_lp import *

import os

from mip import *
import numpy as np

from django.http import JsonResponse
from django_q.tasks import async_task

from django.core.files import File


def submit_cbc(problem):
    print("Task run!!!")

    generate_chebyshev(problem)

    # timestr, NumOfObj, problem_temp_files = parse_gurobi_url(problem)
    #
    # f = {}
    # weights = []
    # ystar = {}
    # models = {}
    # rho = 0.001
    #
    # for obj in range(NumOfObj):
    #
    #     m = Model(solver_name=CBC)
    #     models[obj] = m
    #     # obj_lp_path = settings.MEDIA_ROOT + "/problems/txt/new_problem_" + str(obj) + "_" + timestr + ".lp"
    #     # obj_lp_path = "problems/txt/new_problem_" + str(obj) + "_" + timestr + ".lp"
    #     obj_lp_path = problem_temp_files[obj].name
    #
    #     print(obj_lp_path)
    #     problem_temp_files[obj].flush()
    #     m.read(obj_lp_path)
    #     print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))
    #
    #     m.max_gap = 0.25
    #     status = m.optimize(max_seconds=90)
    #
    #     if status == OptimizationStatus.OPTIMAL:
    #         print('optimal solution cost {} found'.format(m.objective_value))
    #         ystar[obj] = m.objective_value
    #     elif status == OptimizationStatus.FEASIBLE:
    #         print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
    #         ystar[obj] = m.objective_value
    #     elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    #         print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
    #         ystar[obj] = m.objective_bound
    #
    #     # os.remove(obj_lp_path)
    #
    # # chebyshev scalarization
    # ch = Model(sense=MINIMIZE, solver_name=CBC)
    # m = models[0]
    # print(ystar)
    # for v in m.vars:
    #     ch.add_var(name=v.name, var_type=v.var_type)
    #
    # for c in m.constrs:
    #     ch.add_constr(c.expr, c.name)
    #
    # ch.add_var(name='s', var_type=CONTINUOUS)
    # ch.objective = ch.vars['s']
    #
    # for i in range(NumOfObj):
    #     ch.add_var(name='f{}'.format(i + 1), var_type=CONTINUOUS)
    #     f[i] = ch.vars['f{}'.format(i + 1)]
    #     weights = np.full(NumOfObj, 1 / NumOfObj)
    #
    # for i in range(NumOfObj):
    #     ch.add_constr(
    #         weights[i] * (ystar[i] - f[i]) + xsum(rho * (ystar[i] - f[i]) for i in range(NumOfObj)) <= ch.vars['s'],
    #         'sum{}'.format(i + 1))
    #
    # for obj in range(NumOfObj):
    #
    #     m = models[obj]
    #     o = m.objective
    #     ch.add_constr(f[obj] - o == 0, 'f_constr_' + str(obj))
    #
    # # ch.write(settings.MEDIA_ROOT + "/problems/chebyshev/chebyshev_" + timestr + ".lp")
    #
    # temp_chebyshev = NamedTemporaryFile(mode='wt', suffix='.lp', prefix="chebyshev_" + timestr)
    # ch.write(temp_chebyshev.name)
    #
    #
    # dst = temp_chebyshev.name.split("\\")[-1]
    # print(temp_chebyshev.name)
    # temp_chebyshev.flush()
    #
    # f = NamedTemporaryFile()
    # temp_chebyshev.seek(0)
    # data = open(temp_chebyshev.name, 'r')
    # for li in data.readlines():
    #     f.write(bytes(li, 'utf-8'))
    # f.flush()
    # problem.chebyshev = File(f, name=dst)
    # problem.save()
    # problem.chebyshev = files.File(chebyshev, name=chebyshev.name)
    # problem.save()
    # save_files('chebknap', '/problems/chebyshev/', 'lp', 'chebyshev', problem, ch)

    #     context = get_context()
    #     context.update({'solver': slvr})
    #
    # return render(request, 'user_problems.html', context)


def submit_cbc_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    slvr = problem.solver

    if request.method == 'POST':

        async_task(submit_cbc, problem)

    # return JsonResponse(json_payload)
    context = get_context()
    context.update({'solver': slvr})
    return render(request, 'problem_list.html', context)

