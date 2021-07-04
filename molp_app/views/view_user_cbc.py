from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from molp_app.models import UserProblem
from molp_app.utilities.file_helper import *
from molp_app.utilities.parse_gurobi_multi_lp import *

import os
from shutil import copyfile

from mip import *
import re
import time
import numpy as np
from django_q.tasks import async_task


@login_required
def submit_user_cbc_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    slvr = problem.solver

    if request.method == 'POST':
        async_task(submit_cbc, problem)

        user_context = get_user_context(request)
        user_context.update({'solver': slvr})

    return render(request, 'user_problems.html', user_context)
