from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):
    title = models.CharField(max_length=100)
    xml = models.FileField(upload_to='problems/xmls/')

    jobNumber = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    result = models.FileField(upload_to='problems/solutions/', blank=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.result.delete()
        super().delete(*args, **kwargs)


class UserProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problems", null=True)
    title = models.CharField(max_length=100)
    xml = models.FileField(upload_to='problems/xmls/')

    jobNumber = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    result = models.FileField(upload_to='problems/solutions/', blank=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.xml.delete()
        self.result.delete()
        super().delete(*args, **kwargs)
