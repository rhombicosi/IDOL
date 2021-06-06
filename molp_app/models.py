from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):
    NEOS = 'NEOS'
    CBC = 'CBC'
    SOLVERS = (
        (NEOS, 'NEOS'),
        (CBC, 'CBC'),
    )
    title = models.CharField(max_length=100)
    xml = models.FileField(upload_to='problems/xmls/', verbose_name='input file')
    solver = models.CharField(max_length=10, choices=SOLVERS, default=CBC)

    # NEOS fields
    jobNumber = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    # CBC fields
    chebyshev = models.FileField(upload_to='problems/chebyshev/', blank=True)

    # common fields
    result = models.FileField(upload_to='problems/solutions/', blank=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.result.delete()
        self.chebyshev.delete()
        super().delete(*args, **kwargs)


class ProblemParameters(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="parameters", null=True)
    numberOfObjectives = models.IntegerField(null=True, blank=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True)

    def __str__(self):
        return self.problem.title

    def delete(self, *args, **kwargs):
        self.weights.delete()
        self.reference.delete()
        super().delete(*args, **kwargs)


# class SingleObjectiveProblem(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="single", null=True)
#     singlelp = models.FileField(upload_to='problems/single/', verbose_name='single objective')
#
#     def delete(self, *args, **kwargs):
#         self.singlelp.delete()
#         super().delete(*args, **kwargs)


class UserProblem(models.Model):

    NEOS = 'NEOS'
    CBC = 'CBC'
    SOLVERS = (
        (NEOS, 'NEOS'),
        (CBC, 'CBC')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problems", null=True)
    title = models.CharField(max_length=100)
    xml = models.FileField(upload_to='problems/xmls/', verbose_name='input file')
    solver = models.CharField(max_length=10, choices=SOLVERS, default=CBC)

    # NEOS fields
    jobNumber = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    # CBC fields
    chebyshev = models.FileField(upload_to='problems/chebyshev/', blank=True)
    txt = models.FileField(upload_to='problems/txt/', blank=True)

    # common fields
    result = models.FileField(upload_to='problems/solutions/', blank=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.result.delete()
        self.chebyshev.delete()
        super().delete(*args, **kwargs)


class UserProblemParameters(models.Model):
    problem = models.ForeignKey(UserProblem, on_delete=models.CASCADE, related_name="parameters", null=True)
    numberOfObjectives = models.IntegerField(null=True, blank=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True)

    def __str__(self):
        return self.problem.title

    def delete(self, *args, **kwargs):
        self.weights.delete()
        self.reference.delete()
        super().delete(*args, **kwargs)
