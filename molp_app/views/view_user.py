import time
import sys

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect

from ..forms import ProblemForm
from ..models import UserProblem


# registered user
@login_required
def user_problems(request):
    return render(request, 'user_problems.html')


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
    return render(request, 'upload_problem.html', {
        'form': form
    })


@login_required
def submit_user_problem(request, pk):

    if request.method == 'POST':
        problem = UserProblem.objects.get(pk=pk)
        problem.status = None
        slvr = problem.solver

        if slvr == 'Gurobi':
            print('Gurobi solver is chosen')
        if slvr == 'NEOS':
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

    return render(request, 'user_problems.html')


@login_required
def status_user_problem(request, pk):

    if request.method == 'POST':

        problem = UserProblem.objects.get(pk=pk)

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

    return render(request, 'user_problems.html')


@login_required
def read_user_result(request, pk):

    problem = UserProblem.objects.get(pk=pk)
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
    return render(request, 'user_problems.html')


@login_required
def delete_user_problem(request, pk):
    if request.method == 'POST':
        book = UserProblem.objects.get(pk=pk)
        book.delete()
    return redirect('user_problems')

