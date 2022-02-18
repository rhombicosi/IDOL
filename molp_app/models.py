from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):

    lp = models.FileField(upload_to='problems/lps/', verbose_name='input file')
    zips = models.FileField(upload_to='problems/zips/', verbose_name='zips', blank=True)

    task_id = models.CharField(max_length=50, null=True, blank=True)
    task_status = models.CharField(max_length=50, null=True, blank=True)
    
    zero = 0
    ten = 0.1
    quater = 0.25

    MAXGAPS = [
        (zero, '0%'),
        (ten, '10%'),
        (quater, '25%')
    ]
    
    maxgap = models.FloatField(choices=MAXGAPS, default=ten, verbose_name="Max gap")

    inf = 'inf'
    t30 = '30'
    t60 = '60'
    t300 = '300'
    t600 = '600'
    t1200 = '1200'
    t1800 = '1800'
    t2400 = '2400'
    t3600 = '3600'

    MAXTIMES = [
        (inf, 'Infinity'),
        (t30, '30s'),
        (t60, '1m'),
        (t300, '5m'),
        (t600, '10m'),
        (t1200, '20m'),
        (t1800, '30m'),
        (t2400, '40m'),
        (t3600, '1h'),
    ]

    maxtime = models.CharField(max_length=50, choices=MAXTIMES, default=inf, verbose_name="Max time")

    def delete(self, *args, **kwargs):
        self.lp.delete()
        self.zips.delete()
        super().delete(*args, **kwargs)

    def file_name(self):
        return self.lp.name.split('/')[2][:-40]


class ProblemParameters(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="parameters", null=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True, verbose_name="Y")

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
    lp = models.FileField(upload_to='problems/lps/', verbose_name='input file')
    zips = models.FileField(upload_to='problems/zips/', verbose_name='zips', blank=True)

    task_id = models.CharField(max_length=50, null=True, blank=True)
    task_status = models.CharField(max_length=50, null=True, blank=True)

    zero = 0
    ten = 0.1
    quater = 0.25

    MAXGAPS = [
        (zero, '0%'),
        (ten, '10%'),
        (quater, '25%')
    ]
    
    maxgap = models.FloatField(choices=MAXGAPS, default=ten, verbose_name="Max gap")

    inf = 'inf'
    t30 = '30'
    t60 = '60'
    t300 = '300'
    t600 = '600'
    t1200 = '1200'
    t1800 = '1800'
    t2400 = '2400'
    t3600 = '3600'

    MAXTIMES = [
        (inf, 'Infinity'),
        (t30, '30s'),
        (t60, '1m'),
        (t300, '5m'),
        (t600, '10m'),
        (t1200, '20m'),
        (t1800, '30m'),
        (t2400, '40m'),
        (t3600, '1h'),
    ]

    maxtime = models.CharField(max_length=50, choices=MAXTIMES, default=inf, verbose_name="Max time")

    def delete(self, *args, **kwargs):
        self.lp.delete()
        self.zips.delete()
        super().delete(*args, **kwargs)

    def file_name(self):
        return self.lp.name.split('/')[2][:-40]


class UserProblemParameters(models.Model):
    problem = models.ForeignKey(UserProblem, on_delete=models.CASCADE, related_name="parameters", null=True)
    weights = models.FileField(upload_to='problems/parameters/weights/', blank=True)
    reference = models.FileField(upload_to='problems/parameters/reference/', blank=True, verbose_name="Y")

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
