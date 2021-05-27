from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from molp_app.models import UserProblem
from molp_app.utilities.file_helper import *
from molp_app.utilities.parse_gurobi_multi_lp import *

import os
from shutil import copyfile

from mip import *
import re
import time
import numpy as np


@login_required
def submit_user_cbc_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    slvr = problem.solver

    if request.method == 'POST':

        timestr, NumOfObj = parse_gurobi(problem)

        f = {}
        weights = []
        ystar = {}
        models = {}
        rho = 0.001

        for obj in range(NumOfObj):

            m = Model(solver_name=CBC)
            models[obj] = m
            obj_lp_path = settings.MEDIA_ROOT + "/problems/txt/new_problem_" + str(obj) + "_" + timestr + ".lp"

            print(obj_lp_path)
            m.read(obj_lp_path)
            print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))

            m.max_gap = 0.25
            status = m.optimize(max_seconds=100)
            if status == OptimizationStatus.OPTIMAL:
                print('optimal solution cost {} found'.format(m.objective_value))
                ystar[obj] = m.objective_value
            elif status == OptimizationStatus.FEASIBLE:
                print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
                ystar[obj] = m.objective_value
            elif status == OptimizationStatus.NO_SOLUTION_FOUND:
                print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
                ystar[obj] = m.objective_bound

            os.remove(obj_lp_path)

        # chebyshev scalarization
        ch = Model(sense=MINIMIZE, solver_name=CBC)
        m = models[0]
        print(ystar)
        for v in m.vars:
            ch.add_var(name=v.name, var_type=v.var_type)

        for c in m.constrs:
            ch.add_constr(c.expr, c.name)

        ch.add_var(name='s', var_type=CONTINUOUS)
        ch.objective = ch.vars['s']

        for i in range(NumOfObj):
            ch.add_var(name='f{}'.format(i + 1), var_type=CONTINUOUS)
            f[i] = ch.vars['f{}'.format(i + 1)]
            weights = np.full(NumOfObj, 1 / NumOfObj)

        for i in range(NumOfObj):
            ch.add_constr(
                weights[i] * (ystar[i] - f[i]) + xsum(rho * (ystar[i] - f[i]) for i in range(NumOfObj)) <= ch.vars['s'],
                'sum{}'.format(i + 1))

        for obj in range(NumOfObj):

            m = models[obj]
            o = m.objective
            ch.add_constr(f[obj] - o == 0, 'f_constr_' + str(obj))

        # ch.write(settings.MEDIA_ROOT + "/problems/chebyshev/chebyshev_" + timestr + ".lp")

        save_gurobi_files('chebknap', '/problems/chebyshev/', 'lp', 'chebyshev', problem, ch)

        problems = UserProblem.objects.filter(user=request.user)
        problems_neos = problems.filter(solver="NEOS")
        problems_gurobi = problems.filter(solver="Gurobi")
        problems_cbc = problems.filter(solver="CBC")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'problems_cbc': problems_cbc,
        'solver': slvr,
    })
