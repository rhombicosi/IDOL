# Generated by Django 3.1.9 on 2021-07-15 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('molp_app', '0021_problem_zips'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='title',
        ),
        migrations.RemoveField(
            model_name='userproblem',
            name='chebyshev',
        ),
        migrations.RemoveField(
            model_name='userproblem',
            name='title',
        ),
        migrations.CreateModel(
            name='UserProblemChebyshev',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chebyshev', models.FileField(blank=True, upload_to='problems/chebyshev/')),
                ('problem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chebyshev', to='molp_app.userproblem')),
            ],
        ),
    ]
