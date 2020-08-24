from django.contrib import admin
from .models import Problem, ProblemParameters, UserProblem, UserProblemParameters

admin.site.register(Problem)
admin.site.register(ProblemParameters)
admin.site.register(UserProblem)
admin.site.register(UserProblemParameters)
