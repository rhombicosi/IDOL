from django.contrib import admin
from .models import Problem, ProblemParameters, ProblemChebyshev, UserProblem, UserProblemParameters, UserProblemChebyshev

admin.site.register(Problem)
admin.site.register(ProblemParameters)
admin.site.register(ProblemChebyshev)
admin.site.register(UserProblem)
admin.site.register(UserProblemParameters)
admin.site.register(UserProblemChebyshev)
