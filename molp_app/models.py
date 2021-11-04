from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):

    xml = models.FileField(upload_to='problems/xmls/', verbose_name='input file')
    zips = models.FileField(upload_to='problems/zips/', verbose_name='zips', blank=True)

    txt = models.FileField(upload_to='problems/txt/', blank=True)
    task_id = models.CharField(max_length=50, null=True, blank=True)
    task_status = models.CharField(max_length=50, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.txt.delete()
        self.zips.delete()
        super().delete(*args, **kwargs)

    def file_name(self):
        return self.xml.name.split('/')[2][:-40]


class ProblemParameters(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="parameters", null=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True)

    def delete(self, *args, **kwargs):
        self.weights.delete()
        self.reference.delete()
        super().delete(*args, **kwargs)

    def delete_weights(self, *args, **kwargs):
        self.weights.delete()
        super().delete(*args, **kwargs)

    def delete_reference(self, *args, **kwargs):
        self.reference.delete()
        super().delete(*args, **kwargs)


class ProblemChebyshev(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="chebyshev", null=True)
    chebyshev = models.FileField(upload_to='problems/chebyshev/', blank=True)

    def delete(self, *args, **kwargs):
        self.chebyshev.delete()
        super().delete(*args, **kwargs)


class UserProblem(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problems", null=True)
    xml = models.FileField(upload_to='problems/xmls/', verbose_name='input file')
    zips = models.FileField(upload_to='problems/zips/', verbose_name='zips', blank=True)

    txt = models.FileField(upload_to='problems/txt/', blank=True)
    task_id = models.CharField(max_length=50, null=True, blank=True)
    task_status = models.CharField(max_length=50, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.txt.delete()
        self.zips.delete()
        super().delete(*args, **kwargs)

    def file_name(self):
        return self.xml.name.split('/')[2][:-40]


class UserProblemParameters(models.Model):
    problem = models.ForeignKey(UserProblem, on_delete=models.CASCADE, related_name="parameters", null=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True)

    def delete(self, *args, **kwargs):
        self.weights.delete()
        self.reference.delete()
        super().delete(*args, **kwargs)

    def delete_weights(self, *args, **kwargs):
        self.weights.delete()
        super().delete(*args, **kwargs)

    def delete_reference(self, *args, **kwargs):
        self.reference.delete()
        super().delete(*args, **kwargs)


class UserProblemChebyshev(models.Model):
    problem = models.ForeignKey(UserProblem, on_delete=models.CASCADE, related_name="chebyshev", null=True)
    chebyshev = models.FileField(upload_to='problems/chebyshev/', blank=True)

    def delete(self, *args, **kwargs):
        self.chebyshev.delete()
        super().delete(*args, **kwargs)
