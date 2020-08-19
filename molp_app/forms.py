from django import forms
from .models import Problem, UserProblemParameters


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('title', 'xml', 'solver')


class ParametersForm(forms.ModelForm):
    class Meta:
        model = UserProblemParameters
        fields = ('weights', 'reference')
