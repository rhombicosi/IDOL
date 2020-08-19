from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from molp_app.models import UserProblem, UserProblemParameters


@login_required
def user_problem(request, pk):
    if request.method == 'GET':
        problem = UserProblem.objects.get(pk=pk)

    return render(request, 'user_problem.html')



# def upload_user_problem(request):
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
#             return redirect('user_problems')
#     else:
#         form = ProblemForm()
#     return render(request, 'upload_problem.html', {
#         'form': form
#     })

