from django.shortcuts import render, redirect

from molp_app.utilities.file_helper import *
from molp_app.utilities.parse_gurobi_multi_lp import *

from mip import *
import numpy as np

from django_q.tasks import async_task


def submit_cbc_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    slvr = problem.solver

    if request.method == 'POST':
        async_task(submit_cbc, problem)

    context = get_context()
    context.update({'solver': slvr})
    return render(request, 'problem_list.html', context)

