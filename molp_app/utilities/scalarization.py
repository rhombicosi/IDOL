from mip import *
import numpy as np
import boto3
import requests
from datetime import datetime

from celery import shared_task
from celery.result import AsyncResult

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from molp_app.models import ProblemChebyshev, UserProblemChebyshev, Problem, UserProblem

s3 = boto3.resource('s3')


def read_url(url):
    in_memory_file = requests.get(url, stream=True)
    url_temp_file = NamedTemporaryFile()

    for block in in_memory_file.iter_content(1024*8):
        if not block:
            break

        url_temp_file.write(block)

    return url_temp_file


# working with cloud storage
# parse gurobi style multiobjective lp
# produce problem models for each objective
def parse_gurobi_url(problem):

    lp_temp_file = read_url(problem.lp.url)
    lp_temp_file.flush()
    lp_temp_file.seek(0)
    lines = lp_temp_file.readlines()
    lp_temp_file.close()

    for line in range(len(lines)):
        lines[line] = lines[line].decode("utf-8")

    keywords = {'st': ['subject to', 'st', 's.t.'], 'sns': ['max', 'min']}

    count = 0
    st_line = 0
    sns_line = 0
    sns = ''

    # find objectives and constraints in txt file
    # strip the newline character
    for line in lines:
        count += 1
        # line = line.decode("utf-8")
        for w in keywords['st']:
            if w == line.strip().casefold():
                st_line = count
                print(st_line)
                print("Line{}: {}".format(count, line.strip()))
        for w in keywords['sns']:
            if line.strip().casefold().startswith(w):
                sns = w
                sns_line = count
                print(sns)
                print("Line{}: {}".format(count, line.strip()))

    # create files for each objective
    start = sns_line + 1
    end = st_line

    num_of_obj = (end - start) // 2

    timestr = str(datetime.now().microsecond)

    obj_temp_files = []
    for obj in range(num_of_obj):
        ff = NamedTemporaryFile(mode='wt', suffix=".txt", prefix="new_objectives_" + str(obj) + "_" + timestr)
        obj_temp_files.append(ff)

        if sns == 'max':
            ff.write('MAXIMIZE\n')
        else:
            ff.write('MINIMIZE\n')
        ff.write('Obj' + str(obj) + ':\n')
        ff.write(lines[start - 1 + (obj * 2 + 1)])
        ff.write('\n')

    # create file with constraints and variables
    constr_temp_file = NamedTemporaryFile(mode='wt', suffix=".txt", prefix="new_constrs_" + str(obj) + "_" + timestr)

    for line in range(st_line - 1, len(lines)):
        constr_temp_file.write(lines[line])

    # create file for each single objective problem
    problem_temp_files = []
    models = {}

    for obj in range(num_of_obj):

        problem_lp_path = NamedTemporaryFile(mode='wt', suffix='.lp',
            prefix="new_problem_" + str(obj) + "_" + timestr)
        problem_temp_files.append(problem_lp_path)
        f1 = open(problem_lp_path.name, 'a+')

        obj_temp_files[obj].flush()
        obj_temp_files[obj].seek(0)
        f2 = open(obj_temp_files[obj].name, 'r')

        constr_temp_file.flush()
        constr_temp_file.seek(0)
        f3 = open(constr_temp_file.name, 'r')

        # appending the contents of the second file to the first file
        f1.write(f2.read())
        f1.write(f3.read())
        # temp file fix with f1 flush
        f1.flush()

        # create a model for each objective
        m = Model(solver_name=CBC)
        models[obj] = m

        problem_temp_files[obj].flush()
        problem_temp_files[obj].seek(0)

        problem_lp_path = problem_temp_files[obj].name
        print(problem_lp_path)

        m.read(problem_lp_path)
        print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))

    return timestr, num_of_obj, models


# parse txt files with weights and reference points
def parse_parameters_url(problem, param):

    param_field = getattr(problem.parameters.all()[0], param)
    param_temp_file = read_url(param_field.url)

    param_temp_file.flush()
    param_temp_file.seek(0)
    lines = param_temp_file.readlines()
    param_temp_file.close()

    params = {}
    for line in range(len(lines)):
        lines[line] = lines[line].decode("utf-8")
        params[line] = lines[line]

    for k, w in params.items():
        params[k] = [float(item) for item in w.split()]

    return params


# calculate reference if it is not provided
def calculate_reference(num_of_obj, models, maxgap, maxtime):
    ystar = {}
    epsilon = 0.1

    for obj in range(num_of_obj):
        m = models[obj]

        # optimization with CBC
        m.max_gap = maxgap
        status = m.optimize(max_seconds=float(maxtime))

        if status == OptimizationStatus.OPTIMAL:
            print('optimal solution cost {} found'.format(m.objective_value))
            ystar[obj] = m.objective_value + epsilon
        elif status == OptimizationStatus.FEASIBLE:
            print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
            ystar[obj] = m.objective_value + epsilon
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
            ystar[obj] = m.objective_bound
    
    return ystar

# generates chebyshev scalarization
@shared_task(bind=True)
def submit_cbc(self, pk, user):

    task_id = self.request.id

    if user:
        problem = UserProblem.objects.get(pk=pk)
        problem.task_id = task_id
        problem.save()
    else:
        problem = Problem.objects.get(pk=pk)
        problem.task_id = task_id
        problem.save()
    
    timestr, num_of_obj, models = parse_gurobi_url(problem)

    f = {}
    weights = {}
    ystar = {}
    rho = 0.001

    # chebyshev scalarization
    # set weights and reference
    if problem.parameters.first():
        if problem.parameters.all()[0].weights:
            weights = parse_parameters_url(problem, 'weights')
        else:
            weights[0] = np.full(num_of_obj, 1).tolist()

        if problem.parameters.all()[0].reference:
            ystar = parse_parameters_url(problem, 'reference')
        else:
            ystar[0] = calculate_reference(num_of_obj, models, problem.maxgap, problem.maxtime)
    else:
        weights[0] = np.full(num_of_obj, 1).tolist()
        ystar[0] = calculate_reference(num_of_obj, models, problem.maxgap, problem.maxtime)
    
    # delete previous scalarization results
    if problem.chebyshev:
        for ch in problem.chebyshev.all():
            ch.delete()
    
    # create a model
    for k, w in weights.items():
        for j, r in ystar.items():
            ch = Model(sense=MINIMIZE, solver_name=CBC)
            m = models[0]
            name_chebyshev = "Chebyshev_" + str(k + 1) + '_' + str(j + 1) + '_' + problem.lp.name.split('/')[2]

            for v in m.vars:
                ch.add_var(name=v.name, var_type=v.var_type)

            for c in m.constrs:
                ch.add_constr(c.expr, c.name)

            ch.add_var(name='s', var_type=CONTINUOUS)
            ch.objective = ch.vars['s']

            for i in range(num_of_obj):
                ch.add_var(name='f{}'.format(i + 1), var_type=CONTINUOUS)
                f[i] = ch.vars['f{}'.format(i + 1)]

            for i in range(num_of_obj):
                ch.add_constr(
                    -(weights[k][i] * (ystar[j][i] - f[i]) + xsum(rho * (ystar[j][i] - f[i]) for i in range(num_of_obj))) >= -ch.vars[
                        's'],
                    's{}'.format(i + 1))

            for obj in range(num_of_obj):
                m = models[obj]
                o = m.objective
                ch.add_constr(-(f[obj]-o==0), 'f' + str(obj + 1))

            temp_chebyshev = NamedTemporaryFile(mode='wt', suffix='.lp',
                                                prefix="chebyshev_" + str(problem.id) + "_" + timestr)
            ch.write(temp_chebyshev.name)

            temp_chebyshev.flush()

            ch_bytes = NamedTemporaryFile()
            temp_chebyshev.seek(0)
            data = open(temp_chebyshev.name, 'r')
            for li in data.readlines():
                ch_bytes.write(bytes(li, 'utf-8'))
            ch_bytes.flush()

            if user:
                chebyshev_instance = UserProblemChebyshev(chebyshev=File(ch_bytes, name=name_chebyshev), problem=problem)
                chebyshev_instance.save()
                problem.chebyshev.add(chebyshev_instance)
            else:
                chebyshev_instance = ProblemChebyshev(chebyshev=File(ch_bytes, name=name_chebyshev), problem=problem)
                chebyshev_instance.save()
                problem.chebyshev.add(chebyshev_instance)

            problem.save()


channel_layer = get_channel_layer()


@shared_task
def get_tasks_info():
    problems = Problem.objects.order_by('id')

    tasks_info = []
    for p in problems:
        if p.task_id:
            p.task_status = AsyncResult(p.task_id).status

            if p.task_status == 'PENDING':
                p.task_status = 'Press the "Make Chebyshev" button'

            p.save()
            tasks_info.append({'task_id': p.task_id, 'task_status': p.task_status, 'problem_pk': p.id})

    async_to_sync(channel_layer.group_send)('scalarizations', {'type': 'send_scalarizations', 'text': tasks_info})


@shared_task
def get_user_tasks_info():
    problems = UserProblem.objects.all()

    tasks_info = []
    for p in problems:
        if p.task_id:
            p.task_status = AsyncResult(p.task_id).status

            if p.task_status == 'PENDING':
                p.task_status = 'Press the "Make Chebyshev" button'

            p.save()
            tasks_info.append({'task_id': p.task_id, 'task_status': p.task_status, 'problem_pk': p.id})

    async_to_sync(channel_layer.group_send)('user_scalarizations', {'type': 'send_user_scalarizations', 'text': tasks_info})
