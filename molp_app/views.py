import time
import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.files import File

from .forms import ProblemForm
from .models import Problem, UserProblem


def home(request):
    count = User.objects.count()
    return render(request, 'home.html', {
        'count': count
    })

# registration part


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


# problem optimization part
# anonymous user
def delete_problem(request, pk):
    if request.method == 'POST':
        problem = Problem.objects.get(pk=pk)
        problem.delete()
    return redirect('problem_list')


def problem_list(request):
    problems = Problem.objects.all()

    return render(request, 'problem_list.html', {
        'problems': problems
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


def submit_problem(request, pk):
    problems = Problem.objects.all()

    if request.method == 'POST':

        problem = Problem.objects.get(pk=pk)
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

    return render(request, 'problem_list.html', {
        'problems': problems
    })


def status_problem(request, pk):
    problems = Problem.objects.all()

    if request.method == 'POST':

        problem = Problem.objects.get(pk=pk)

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

    return render(request, 'problem_list.html', {
        'problems': problems
    })


def read_result(request, pk):
    problems = Problem.objects.all()

    problem = Problem.objects.get(pk=pk)
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
    return render(request, 'problem_list.html', {
        'problems': problems
    })


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
            p = UserProblem(title=t, xml=xml)
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

