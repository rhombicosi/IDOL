import os
import requests
import uuid
import json
from zipfile import ZipFile

from django.core.files.base import File
from django.core import serializers
from django.shortcuts import render, redirect

from ..utilities.scalarization import submit_cbc
from ..forms import ProblemForm, ParametersForm
from ..models import Problem, ProblemParameters


# Anonymous user
def problem_list(request):
    context = get_context()

    return render(request, 'problem_list.html', context)


def upload_problem_parameters(request):

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        parameters_form = ParametersForm(request.POST, request.FILES)

        if problem_form.is_valid() and parameters_form.is_valid():

            lp = problem_form.cleaned_data["lp"]
            lp.name = f'{lp.name.split(".")[0]}_{uuid.uuid4()}.lp'
            p = Problem(lp=lp)
            p.save()

            params = ProblemParameters()

            if parameters_form.cleaned_data["weights"]:
                w = parameters_form.cleaned_data["weights"]
                params.weights = w
                params.save()
            
            if parameters_form.cleaned_data["reference"]:
                ref = parameters_form.cleaned_data["reference"]
                params.reference = ref
                params.save()

            if parameters_form.cleaned_data["weights"] or parameters_form.cleaned_data["reference"]:
                p.parameters.add(params)

            context = get_context()

            return render(request, 'problem_list.html', context)
    else:
        problem_form = ProblemForm()
        parameters_form = ParametersForm()

    return render(request, 'upload_problem.html', {
        'problem_form': problem_form,
        'parameters_form': parameters_form,
    })


def submit_problem(request, pk):
    problem = Problem.objects.get(pk=pk)

    p = serializers.serialize('json', [problem])
    p = json.loads(p)
    p_id = p[0]['pk']

    if request.method == 'POST':
        submit_cbc.delay(p_id, 0)

    context = get_context()
    context.update({'problem_id': p_id})

    return render(request, 'problem_list.html', context)


def delete_problem(request, pk):
    problem = Problem.objects.get(pk=pk)

    if request.method == 'POST':
        
        for params in problem.parameters.all():
            params.delete()

        problem.delete()

    context = get_context()

    return render(request, 'problem_list.html', context)


def update_problem(request, pk):

    if request.method == 'POST':
        form = ParametersForm(request.POST, request.FILES)
        problem = Problem.objects.get(pk=pk)

        if problem.parameters.first():
            params = problem.parameters.first()
        else:
            params = ProblemParameters()

        if form.is_valid():
            if form.cleaned_data["weights"]:
                if problem.parameters:
                    for param in problem.parameters.all():
                        param.delete_weights()

                w = form.cleaned_data["weights"]
                params.weights = w

                if problem.parameters.first():
                    problem.parameters.update(weights=w)

            if form.cleaned_data["reference"]:
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
    problems = Problem.objects.order_by('id')

    context = {
        'problems': problems
    }

    return context
