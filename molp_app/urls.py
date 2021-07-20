from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, path, include

import molp_app.views.view_anonymous
import molp_app.views.view_user
from .views import view_common, view_anonymous, view_user

urlpatterns = [
    re_path(r'^$', view_common.home, name='home'),
    re_path(r'^problems/$', view_anonymous.problem_list, name='problem_list'),
    re_path(r'^problems/upload/$', view_anonymous.upload_problem_parameters, name='upload_problem_parameters'),
    path('problems/submit/<int:pk>/', view_anonymous.submit_problem, name='submit_problem'),
    path('problems/submit_cbc/<int:pk>/', molp_app.views.view_anonymous.submit_cbc_problem, name='submit_cbc_problem'),
    path('problems/status/<int:pk>/', view_anonymous.status_problem, name='status_problem'),
    path('problems/result/<int:pk>/', view_anonymous.read_result, name='read_result'),
    path('problems/delete/<int:pk>/', view_anonymous.delete_problem, name='delete_problem'),
    path('signup/', view_common.signup, name='signup'),
    re_path(r'^user_problem_list/$', view_user.user_problem_list, name='user_problem_list'),
    re_path(r'^user_problem_list/upload/$', view_user.upload_user_problem_parameters, name='upload_user_problem_parameters'),
    path('user_problem_list/submit_user/<int:pk>/', view_user.submit_user_problem, name='submit_user_problem'),

    path('user_problem_list/submit_user_cbc/<int:pk>/', molp_app.views.view_user.submit_user_cbc_problem, name='submit_user_cbc_problem'),


    path('user_problem_list/status_user/<int:pk>/', view_user.status_user_problem, name='status_user_problem'),
    path('user_problem_list/result_user/<int:pk>/', view_user.read_user_result, name='read_user_result'),
    path('user_problem_list/delete_user/<int:pk>/', view_user.delete_user_problem, name='delete_user_problem'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('problem/update_user/<int:pk>/', view_user.update_user_problem, name='update_user_problem'),
    path('problem/update/<int:pk>/', view_anonymous.update_problem, name='update_problem'),

    path('problem/download/<int:pk>/', view_anonymous.download_zip, name='download_zip'),
    path('user_problem/download/<int:pk>/', view_user.download_zip, name='download_zip'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


