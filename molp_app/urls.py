from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, path, include
from . import views

urlpatterns = [
    re_path(r'^$', views.home, name='home'),

    re_path(r'^problems/$', views.problem_list, name='problem_list'),
    re_path(r'^problems/upload/$', views.upload_problem, name='upload_problem'),
    path('problems/submit/<int:pk>/', views.submit_problem, name='submit_problem'),
    path('problems/status/<int:pk>/', views.status_problem, name='status_problem'),
    path('problems/result/<int:pk>/', views.read_result, name='read_result'),
    path('problems/delete/<int:pk>/', views.delete_problem, name='delete_problem'),
    path('signup/', views.signup, name='signup'),
    re_path(r'^user_problems/$', views.user_problems, name='user_problems'),
    re_path(r'^user_problems/upload/$', views.upload_user_problem, name='upload_user_problem'),
    path('user_problems/submit_user/<int:pk>/', views.submit_user_problem, name='submit_user_problem'),
    path('user_problems/status_user/<int:pk>/', views.status_user_problem, name='status_user_problem'),
    path('user_problems/result_user/<int:pk>/', views.read_user_result, name='read_user_result'),
    path('user_problems/delete_user/<int:pk>/', views.delete_user_problem, name='delete_user_problem'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


