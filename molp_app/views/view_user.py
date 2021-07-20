import time
import sys
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile, File
from django_q.tasks import async_task

from molp_app.utilities.scalarization import submit_cbc

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect

from molp_app.forms import ProblemForm, ParametersForm, UserProblemForm, UserParametersForm
from molp_app.models import UserProblem, UserProblemParameters

# from gurobipy import os
import os
import requests
from zipfile import ZipFile


# registered user
@login_required
def user_problem_list(request):
    user_context = get_user_context(request)

    return render(request, 'user_problem_list.html', user_context)


# @login_required
# def upload_user_problem(request):
#     user_context = get_user_context(request)
#
#     if request.method == 'POST':
#         form = ProblemForm(request.POST, request.FILES)
#         print()
#         if form.is_valid():
#             # form.save()
#             t = form.cleaned_data["title"]
#             xml = form.cleaned_data["xml"]
#             slvr = form.cleaned_data["solver"]
#             p = UserProblem(title=t, xml=xml, solver=slvr)
#             p.save()
#             request.user.problems.add(p)
#             return render('user_problem_list.html', user_context)
#     else:
#         form = ProblemForm()
#     return render(request, 'upload_user_problem.html', {
#         'form': form
#     })

@login_required
def upload_user_problem_parameters(request):

    if request.method == 'POST':
        problem_form = UserProblemForm(request.POST, request.FILES)
        parameters_form = UserParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():

            xml = problem_form.cleaned_data["xml"]
            solver = problem_form.cleaned_data["solver"]
            xml.name = f'{xml.name.split(".")[0]}_{uuid.uuid4()}.lp'
            p = UserProblem(xml=xml, solver=solver)
            p.save()

            params = UserProblemParameters()

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

            request.user.problems.add(p)

            user_context = get_user_context(request)
            user_context.update({'solver': solver})

            return render(request, 'user_problem_list.html', user_context)
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

    user_context = get_user_context(request)
    user_context.update({'solver': solver})

    return render(request, 'user_problem_list.html', user_context)


@login_required
def submit_user_cbc_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    slvr = problem.solver

    if request.method == 'POST':
        async_task(submit_cbc, problem, 1)

        user_context = get_user_context(request)
        user_context.update({'solver': slvr})

    return render(request, 'user_problem_list.html', user_context)


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

    user_context = get_user_context(request)
    user_context.update({'solver': solver})

    return render(request, 'user_problem_list.html', user_context)


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

    user_context = get_user_context(request)
    user_context.update({'solver': solver})

    return render(request, 'user_problem_list.html', user_context)


@login_required
def delete_user_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)
    solver = problem.solver

    if request.method == 'POST':
        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    user_context = get_user_context(request)
    user_context.update({'solver': solver})

    return render(request, 'user_problem_list.html', user_context)


@login_required
def update_user_problem(request, pk):

    if request.method == 'POST':
        form = UserParametersForm(request.POST, request.FILES)
        problem = UserProblem.objects.get(pk=pk)
        # params = ProblemParameters()

        # if problem.parameters:
        #     for param in problem.parameters.all():
        #         param.delete()

        if problem.parameters.first():
            params = problem.parameters.first()
        else:
            params = UserProblemParameters()

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
            return redirect('user_problem_list')
    else:
        form = ParametersForm()
    return render(request, 'update_user_problem.html', {
        'form': form
    })


@login_required
def download_zip(request, pk):
    problem = UserProblem.objects.get(pk=pk)
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


@login_required
def get_user_context(request):
    problems = UserProblem.objects.filter(user=request.user)
    print(request.user.id)
    problems_neos = problems.filter(solver="NEOS")
    problems_cbc = problems.filter(solver="CBC")

    user_context = {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_cbc': problems_cbc,
    }

    return user_context
