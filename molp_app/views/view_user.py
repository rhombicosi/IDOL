import os
import requests
import uuid
import json
from zipfile import ZipFile

from django.contrib.auth.decorators import login_required
from django.core.files.base import File
from django.shortcuts import render, redirect
from django.core import serializers

from ..utilities.scalarization import submit_cbc
from ..forms import ProblemForm, ParametersForm, UserProblemForm, UserParametersForm
from ..models import UserProblem, UserProblemParameters


# registered user
@login_required
def user_problem_list(request):
    user_context = get_user_context(request)

    return render(request, 'user_problem_list.html', user_context)


@login_required
def upload_user_problem_parameters(request):
    if request.method == 'POST':
        problem_form = UserProblemForm(request.POST, request.FILES)
        parameters_form = UserParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():

            xml = problem_form.cleaned_data["xml"]
            xml.name = f'{xml.name.split(".")[0]}_{uuid.uuid4()}.lp'
            p = UserProblem(xml=xml)
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

    p = serializers.serialize('json', [problem])
    p = json.loads(p)
    p_id = p[0]['pk']
    print(p_id)

    if request.method == 'POST':
        submit_cbc.delay(p_id, 1)

    user_context = get_user_context(request)
    user_context.update({'problem_id': p_id})
    return render(request, 'user_problem_list.html', user_context)


@login_required
def delete_user_problem(request, pk):
    problem = UserProblem.objects.get(pk=pk)

    if request.method == 'POST':
        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    user_context = get_user_context(request)

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

    user_context = {
        'problems': problems
    }

    return user_context
