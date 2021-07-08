# Generated by Django 3.1.9 on 2021-06-23 23:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('molp_app', '0016_problem_txt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='chebyshev',
        ),
        migrations.CreateModel(
            name='ProblemChebyshev',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chebyshev', models.FileField(blank=True, upload_to='problems/chebyshev/')),
                ('problem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chebyshev', to='molp_app.problem')),
            ],
        ),
    ]