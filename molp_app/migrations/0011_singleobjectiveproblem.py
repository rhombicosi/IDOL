# Generated by Django 3.1 on 2020-08-25 23:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('molp_app', '0010_problem_chebyshev'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleObjectiveProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singlelp', models.FileField(upload_to='problems/single/', verbose_name='single objective')),
                ('problem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='single', to='molp_app.problem')),
            ],
        ),
    ]
