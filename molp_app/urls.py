from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, path, include
from .views import view_common, view_anonymous, view_user, view_user_gurobi, view_user_problem_gurobi, \
    view_anonymous_gurobi

urlpatterns = [
    re_path(r'^$', view_common.home, name='home'),
    re_path(r'^problems/$', view_anonymous.problem_list, name='problem_list'),
    re_path(r'^problems/upload/$', view_anonymous.upload_problem_parameters, name='upload_problem_parameters'),
    path('problems/submit/<int:pk>/', view_anonymous.submit_problem, name='submit_problem'),
    path('problems/submit_gurobi/<int:pk>/', view_anonymous_gurobi.submit_gurobi_problem, name='submit_gurobi_problem'),
    path('problems/status/<int:pk>/', view_anonymous.status_problem, name='status_problem'),
    path('problems/result/<int:pk>/', view_anonymous.read_result, name='read_result'),
    path('problems/delete/<int:pk>/', view_anonymous.delete_problem, name='delete_problem'),
    path('signup/', view_common.signup, name='signup'),
    re_path(r'^user_problems/$', view_user.user_problems, name='user_problems'),
    re_path(r'^user_problems/upload/$', view_user.upload_user_problem_parameters, name='upload_user_problem_parameters'),
    path('user_problems/submit_user/<int:pk>/', view_user.submit_user_problem, name='submit_user_problem'),
    path('user_problems/submit_user_gurobi/<int:pk>/', view_user_gurobi.submit_user_gurobi_problem, name='submit_user_gurobi_problem'),
    path('user_problems/status_user/<int:pk>/', view_user.status_user_problem, name='status_user_problem'),
    path('user_problems/result_user/<int:pk>/', view_user.read_user_result, name='read_user_result'),
    path('user_problems/delete_user/<int:pk>/', view_user.delete_user_problem, name='delete_user_problem'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('problem/<int:pk>/', view_user_problem_gurobi.user_problem, name='user_problem'),
    path('problem/update_user/<int:pk>/', view_user.update_user_problem, name='update_user_problem'),
    path('problem/update/<int:pk>/', view_anonymous.update_problem, name='update_problem'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


