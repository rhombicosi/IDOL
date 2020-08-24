import time
import sys

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile

from .view_user_gurobi import create_user_gurobi_problem
from molp_app.utilities.file_helper import read_txt, save_gurobi_files

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect

from molp_app.forms import ProblemForm, ParametersForm
from molp_app.models import UserProblem, UserProblemParameters

from gurobipy import os


# registered user
@login_required
def user_problems(request):
    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
    })


@login_required
def upload_user_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        print()
        if form.is_valid():
            # form.save()
            t = form.cleaned_data["title"]
            xml = form.cleaned_data["xml"]
            slvr = form.cleaned_data["solver"]
            p = UserProblem(title=t, xml=xml, solver=slvr)
            p.save()
            request.user.problems.add(p)
            return redirect('user_problems')
    else:
        form = ProblemForm()
    return render(request, 'upload_user_problem.html', {
        'form': form
    })


@login_required
def upload_user_problem_parameters(request):

    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        parameters_form = ParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():
            t = problem_form.cleaned_data["title"]
            xml = problem_form.cleaned_data["xml"]
            solver = problem_form.cleaned_data["solver"]
            p = UserProblem(title=t, xml=xml, solver=solver)
            p.save()

            params = UserProblemParameters()

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

            request.user.problems.add(p)
            return render(request, 'user_problems.html', {
                'problems': problems,
                'problems_neos': problems_neos,
                'problems_gurobi': problems_gurobi,
                'solver': solver
            })
    else:
        problem_form = ProblemForm()
        parameters_form = ParametersForm()

    return render(request, 'upload_user_problem.html', {
        'problem_form': problem_form,
        'parameters_form': parameters_form,
    })


@login_required
def submit_user_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    solver = problem.solver

    if request.method == 'POST':

        problem.status = None

        print('NEOS solver is chosen')
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

        UserProblem.objects.filter(pk=pk).update(jobNumber=jobNumber, password=password)

        sys.stdout.write("Job number = %d\nJob password = %s\n" % (jobNumber, password))

        print('problem submitted %s' % xmlfile.name)

    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver
    })


@login_required
def status_user_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
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
            UserProblem.objects.filter(pk=pk).update(status=status)
            sys.stdout.write("Job number = %d\nJob password = %s\n" % (jobNumber, password))
            sys.stdout.write("status = %s\n" % status)

    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver,
    })


@login_required
def read_user_result(request, pk):

    problem = UserProblem.objects.get(pk=pk)
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

    print('NEOS result {}'.format(problem.result.url))

    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver,
    })


@login_required
def delete_user_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    solver = problem.solver

    if request.method == 'POST':
        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_gurobi = problems.filter(solver="Gurobi")

    return render(request, 'user_problems.html', {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_gurobi': problems_gurobi,
        'solver': solver
    })


@login_required
def update_user_problem(request, pk):
    if request.method == 'POST':
        form = ParametersForm(request.POST, request.FILES)
        problem = UserProblem.objects.get(pk=pk)
        params = UserProblemParameters()
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

            # create new problem only if new weights file is uploaded
            if params.weights:
                w_path = settings.MEDIA_ROOT + '/problems/parameters/weights/'
                w_name = os.path.basename(params.weights.path)
                weights = read_txt(w_path, w_name)

                new_p = create_user_gurobi_problem(request, pk, weights)
                new_p.parameters.add(params)

            # TODO: update problem reference

            return redirect('user_problems')
    else:
        form = ParametersForm()
    return render(request, 'update_user_problem.html', {
        'form': form
    })
