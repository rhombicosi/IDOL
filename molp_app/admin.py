from django.contrib import admin
from .models import Problem, UserProblem, UserProblemParameters


admin.site.register(Problem)
admin.site.register(UserProblem)
admin.site.register(UserProblemParameters)
