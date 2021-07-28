import time
import sys
import uuid
import json

from celery.result import AsyncResult
from django.http import HttpResponse

from django.core.files.base import ContentFile, File
from django_q.tasks import async_task

from django.core import serializers
from django.db import transaction

from ..utilities.scalarization import submit_cbc

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect

from ..forms import ProblemForm, ParametersForm
from ..models import Problem, ProblemParameters, UserProblemChebyshev, ProblemChebyshev

# from gurobipy import os
import os
import requests
from zipfile import ZipFile


# Anonymous user
def problem_list(request):
    context = get_context()

    return render(request, 'problem_list.html', context)


# def upload_problem(request):
#
#     if request.method == 'POST':
#         form = ProblemForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#
#             return redirect('problem_list')
#     else:
#         form = ProblemForm()
#     return render(request, 'upload_problem.html', {
#         'form': form
#     })


def upload_problem_parameters(request):

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        parameters_form = ParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():

            xml = problem_form.cleaned_data["xml"]
            solver = problem_form.cleaned_data["solver"]

            xml.name = f'{xml.name.split(".")[0]}_{uuid.uuid4()}.lp'
            print(xml.name)
            p = Problem(xml=xml, solver=solver)
            p.save()

            params = ProblemParameters()

            if parameters_form.cleaned_data["weights"]:
                w = parameters_form.cleaned_data["weights"]
                params.weights = w
                params.save()
            # else:
            #     save_files('weights', '/problems/parameters/weights', 'txt', 'weights', params, None, '0.5, 0.5')
            if parameters_form.cleaned_data["reference"]:
                ref = parameters_form.cleaned_data["reference"]
                params.reference = ref
                params.save()

            if parameters_form.cleaned_data["weights"] or parameters_form.cleaned_data["reference"]:
                # params.save()
                p.parameters.add(params)

            context = get_context()
            context.update({'solver': solver})

            return render(request, 'problem_list.html', context)
    else:
        problem_form = ProblemForm()
        parameters_form = ParametersForm()

    return render(request, 'upload_problem.html', {
        'problem_form': problem_form,
        'parameters_form': parameters_form,
    })


# deprecated
def submit_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    if request.method == 'POST':
        problem.status = None

        neos = xmlrpclib.ServerProxy("https://neos-server.org:3333")

        try:
            alive = neos.ping()
        except IOError as e:
            sys.stderr.write("I/O error(%d): %s\n" % (e.errno, e.strerror))
            sys.exit(1)

        if alive != "NeosServer is alive\n":
            sys.stderr.write("Could not make connection to NEOS Server\n")
            sys.exit(1)

        xml = ""
        try:
            xmlfile = open(problem.xml.path, "r")
            buffer = 1
            while buffer:
                buffer = xmlfile.read()
                xml += buffer
            xmlfile.close()
        except IOError as e:
            sys.stderr.write("I/O error(%d): %s\n" % (e.errno, e.strerror))
            sys.exit(1)

        (jobNumber, password) = neos.submitJob(xml)

        Problem.objects.filter(pk=pk).update(jobNumber=jobNumber, password=password)

        sys.stdout.write("Job number = %d\nJob password = %s\n" % (jobNumber, password))
        # if jobNumber == 0:
        #     sys.stderr.write("NEOS Server error: %s\n" % password)
        #     sys.exit(1)
        # else:
        #     offset = 0
        #     status = ""
        #     while status != "Done":
        #         time.sleep(1)
        #         (msg, offset) = neos.getIntermediateResults(jobNumber, password, offset)
        #         sys.stdout.write(msg.data.decode())
        #         status = neos.getJobStatus(jobNumber, password)
        #     msg = neos.getFinalResults(jobNumber, password)
        #     sys.stdout.write(msg.data.decode())

        print('problem submitted %s' % xmlfile.name)

    context = get_context()
    context.update({'solver': solver})

    return render(request, 'problem_list.html', context)


def submit_cbc_problem(request, pk):
    problem = Problem.objects.get(pk=pk)

    slvr = problem.solver

    if request.method == 'POST':
        async_task(submit_cbc, problem, 0)

    context = get_context()
    context.update({'solver': slvr})
    return render(request, 'problem_list.html', context)


def submit_cbc_problem_celery(request, pk):
    problem = Problem.objects.get(pk=pk)
    slvr = problem.solver

    p = serializers.serialize('json', [problem])
    p = json.loads(p)
    p_id = p[0]['pk']
    print(p_id)

    if request.method == 'POST':
        transaction.on_commit(lambda: submit_cbc.delay(p_id, 0))
        # print(task.status)
        # print(task.id)

    context = get_context()
    context.update({'solver': slvr,
                    'problem_id': p_id},)
    return render(request, 'problem_list.html', context)


# def get_task_info(request):
#     task_id = request.GET.get('task_id', None)
#
#     if task_id is not None:
#         task = AsyncResult(task_id)
#         data = {
#             'state': task.state,
#             'result': task.result,
#         }
#         return HttpResponse(json.dumps(data), content_type='application/json')
#     else:
#         return HttpResponse('No job id given.')


def status_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    if request.method == 'POST':

        neos = xmlrpclib.ServerProxy("https://neos-server.org:3333")

        alive = neos.ping()
        if alive != "NeosServer is alive\n":
            sys.stderr.write("Could not make connection to NEOS Server\n")
            sys.exit(1)

        (jobNumber, password) = (problem.jobNumber, problem.password)

        if jobNumber is None:
            sys.stderr.write("NEOS Server error: %s\n" % password)
            sys.exit(1)
        else:
            status = ""
            status = neos.getJobStatus(jobNumber, password)
            Problem.objects.filter(pk=pk).update(status=status)
            sys.stdout.write("Job number = %d\nJob password = %s\n" % (jobNumber, password))
            sys.stdout.write("status = %s\n" % status)

    context = get_context()
    context.update({'solver': solver})

    return render(request, 'problem_list.html', context)


def read_result(request, pk):

    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    (jobNumber, password) = (problem.jobNumber, problem.password)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    new_name = 'result_' + timestr + '.txt'

    f = problem.result

    neos = xmlrpclib.ServerProxy("https://neos-server.org:3333")

    alive = neos.ping()

    if alive != "NeosServer is alive\n":
        sys.stderr.write("Could not make connection to NEOS Server\n")
        sys.exit(1)

    if jobNumber is None:
        sys.stderr.write("NEOS Server error: %s\n" % password)
        sys.exit(1)
    else:
        msg = neos.getFinalResults(jobNumber, password)
        sys.stdout.write(msg.data.decode())
        f.save(new_name, ContentFile(msg.data.decode()))

    context = get_context()
    context.update({'solver': solver})

    return render(request, 'problem_list.html', context)


def delete_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    if request.method == 'POST':

        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    context = get_context()
    context.update({'solver': solver})

    return render(request, 'problem_list.html', context)


def update_problem(request, pk):

    if request.method == 'POST':
        form = ParametersForm(request.POST, request.FILES)
        problem = Problem.objects.get(pk=pk)
        # params = ProblemParameters()

        # if problem.parameters:
        #     for param in problem.parameters.all():
        #         param.delete()

        if problem.parameters.first():
            params = problem.parameters.first()
        else:
            params = ProblemParameters()

        if form.is_valid():
            if form.cleaned_data["weights"]:
                print('weights')
                print(form.cleaned_data["weights"])

                if problem.parameters:
                    for param in problem.parameters.all():
                        param.delete_weights()

                w = form.cleaned_data["weights"]
                params.weights = w

                if problem.parameters.first():
                    problem.parameters.update(weights=w)

            if form.cleaned_data["reference"]:
                print('reference')
                print(form.cleaned_data["reference"])
                if problem.parameters:
                    for param in problem.parameters.all():
                        param.delete_reference()

                ref = form.cleaned_data["reference"]
                params.reference = ref

                if problem.parameters.first():
                    problem.parameters.update(reference=ref)

            params.save()

            if not problem.parameters.first():
                problem.parameters.add(params)

            # problem.parameters.add(params)



            print(problem.parameters.all())
            return redirect('problem_list')
    else:
        form = ParametersForm()
    return render(request, 'update_problem.html', {
        'form': form
    })


def download_zip(request, pk):
    problem = Problem.objects.get(pk=pk)
    zfname = 'Chebyshev_' + str(problem.id) + '.zip'
    zf = ZipFile(zfname, 'w')

    if request.method == 'POST':
        for ch in problem.chebyshev.all():
            ch_url = ch.chebyshev.url
            ch_name = ch.chebyshev.name.split('/')[2]
            in_memory_file = requests.get(ch_url, stream=True)
            zf.writestr(ch_name, in_memory_file.text)

    zf.close()

    z = open(zfname, "rb")
    problem.zips = File(z)
    problem.save()
    z.close()
    os.remove(zfname)

    return redirect(problem.zips.url)


def get_context():
    problems = Problem.objects.all()
    problems_neos = problems.filter(solver="NEOS")
    problems_cbc = problems.filter(solver="CBC")

    context = {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_cbc': problems_cbc,
    }

    return context
