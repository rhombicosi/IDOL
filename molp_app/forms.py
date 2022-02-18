from django import forms
from .models import Problem, ProblemParameters, UserProblem, UserProblemParameters


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('lp',)


class ParametersForm(forms.ModelForm):
    class Meta:
        model = ProblemParameters
        fields = ('weights', 'reference')


class MaxgapForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('maxgap', 'maxtime')


class UserProblemForm(forms.ModelForm):
    class Meta:
        model = UserProblem
        fields = ('lp',)


class UserParametersForm(forms.ModelForm):
    class Meta:
        model = UserProblemParameters
        fields = ('weights', 'reference')


class UserMaxgapForm(forms.ModelForm):
    class Meta:
        model = UserProblem
        fields = ('maxgap', 'maxtime')

