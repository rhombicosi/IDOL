from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import view_common, view_anonymous, view_user

urlpatterns = [
    path('', view_common.home, name='home'),
    path('signup/', view_common.signup, name='signup'),

    path('problems/', view_anonymous.problem_list, name='problem_list'),
    path('problems/upload/', view_anonymous.upload_problem_parameters, name='upload_problem_parameters'),
    path('problems/update/<int:pk>/', view_anonymous.update_problem, name='update_problem'),
    path('problems/submit/<int:pk>/', view_anonymous.submit_problem, name='submit_problem'),
    path('problems/download/<int:pk>/', view_anonymous.download_zip, name='download_zip'),
    path('problems/delete/<int:pk>/', view_anonymous.delete_problem, name='delete_problem'),

    path('user_problems/', view_user.user_problem_list, name='user_problem_list'),
    path('user_problems/upload/', view_user.upload_user_problem_parameters, name='upload_user_problem_parameters'),
    path('user_problems/update/<int:pk>/', view_user.update_user_problem, name='update_user_problem'),
    path('user_problems/submit/<int:pk>/', view_user.submit_user_problem, name='submit_user_problem'),
    path('user_problems/download/<int:pk>/', view_user.user_download_zip, name='user_download_zip'),
    path('user_problems/delete/<int:pk>/', view_user.delete_user_problem, name='delete_user_problem'),
    
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
