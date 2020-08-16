from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from molp_app.models import UserProblem


@login_required
def user_problem(request, pk):
    if request.method == 'POST':
        problem = UserProblem.objects.get(pk=pk)

    return render(request, 'user_problem.html')
