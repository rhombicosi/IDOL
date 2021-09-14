from django import forms
from .models import Problem, ProblemParameters, UserProblem, UserProblemParameters


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('xml',)


class ParametersForm(forms.ModelForm):
    class Meta:
        model = ProblemParameters
        fields = ('weights', 'reference')


class UserProblemForm(forms.ModelForm):
    class Meta:
        model = UserProblem
        fields = ('xml',)


class UserParametersForm(forms.ModelForm):
    class Meta:
        model = UserProblemParameters
        fields = ('weights', 'reference')
