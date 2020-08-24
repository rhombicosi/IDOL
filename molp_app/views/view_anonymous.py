import time
import sys

from django.core.files.base import ContentFile
from django.conf import settings

from .view_anonymous_gurobi import create_gurobi_problem
from ..utilities.file_helper import read_txt, save_gurobi_files

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect

from ..forms import ProblemForm, ParametersForm
from ..models import Problem, ProblemParameters

from gurobipy import os


# optimization
# anonymous user
def problem_list(request):
    problems = Problem.objects.all()
    problems_neos = Problem.objects.filter(solver="NEOS")
    problems_gurobi = Problem.objects.filter(solver="Gurobi")

    return render(request, 'problem_list.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
    })


def upload_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        print()
        if form.is_valid():
            form.save()
            return redirect('problem_list')
    else:
        form = ProblemForm()
    return render(request, 'upload_problem.html', {
        'form': form
    })


def upload_problem_parameters(request):
    problems = Problem.objects.all()
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        parameters_form = ParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():
            t = problem_form.cleaned_data["title"]
            xml = problem_form.cleaned_data["xml"]
            solver = problem_form.cleaned_data["solver"]
            p = Problem(title=t, xml=xml, solver=solver)
            p.save()

            params = ProblemParameters()

            if parameters_form.cleaned_data["weights"]:
                w = parameters_form.cleaned_data["weights"]
                params.weights = w
            else:
                save_gurobi_files('weights', '/problems/parameters/weights', 'txt', 'weights', params, None, '0.5, 0.5')
            if parameters_form.cleaned_data["reference"]:
                ref = parameters_form.cleaned_data["reference"]
                params.reference = ref
            params.save()
            p.parameters.add(params)

            return render(request, 'problem_list.html', {
                'problems': problems,
                'problems_neos': problems_neos,
                'problems_gurobi': problems_gurobi,
                'solver': solver
            })
    else:
        problem_form = ProblemForm()
        parameters_form = ParametersForm()

    return render(request, 'upload_problem.html', {
        'problem_form': problem_form,
        'parameters_form': parameters_form,
    })


def submit_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    if request.method == 'POST':
        problem.status = None

        neos = xmlrpclib.ServerProxy("https://neos-server.org:3333")

        alive = neos.ping()
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

    problems = Problem.objects.all()
    problems_neos = Problem.objects.filter(solver="NEOS")
    problems_gurobi = Problem.objects.filter(solver="Gurobi")

    return render(request, 'problem_list.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver,
    })


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

    problems = Problem.objects.all()
    problems_neos = Problem.objects.filter(solver="NEOS")
    problems_gurobi = Problem.objects.filter(solver="Gurobi")

    return render(request, 'problem_list.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver
    })


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

    problems = Problem.objects.all()
    problems_neos = Problem.objects.filter(solver="NEOS")
    problems_gurobi = Problem.objects.filter(solver="Gurobi")

    return render(request, 'problem_list.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver,
    })


def delete_problem(request, pk):
    problem = Problem.objects.get(pk=pk)
    solver = problem.solver
    if request.method == 'POST':

        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    problems = Problem.objects.all()
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'problem_list.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver
    })


def update_problem(request, pk):

    if request.method == 'POST':
        form = ParametersForm(request.POST, request.FILES)
        problem = Problem.objects.get(pk=pk)
        params = ProblemParameters()
        print()
        if form.is_valid():
            if form.cleaned_data["weights"]:
                w = form.cleaned_data["weights"]
                params.weights = w
            if form.cleaned_data["reference"]:
                ref = form.cleaned_data["reference"]
                params.reference = ref
            params.save()
            problem.parameters.add(params)

            if params.weights:
                w_path = settings.MEDIA_ROOT + '/problems/parameters/weights/'
                w_name = os.path.basename(params.weights.path)
                weights = read_txt(w_path, w_name)

                new_p = create_gurobi_problem(pk, weights)
                new_p.parameters.add(params)

            return redirect('problem_list')
    else:
        form = ParametersForm()
    return render(request, 'update_problem.html', {
        'form': form
    })
