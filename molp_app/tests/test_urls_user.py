from django.contrib.auth.models import User

from django.test import TestCase, Client
from django.urls import reverse, resolve
from ..views import view_user

class TestUserUrls(TestCase):
    def setUp(self):

        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_user_problem_list_url_resolves(self):
        url = reverse('user_problem_list')
        self.assertEquals(resolve(url).func, view_user.user_problem_list)

    def test_upload_user_problem_parameters_url_resolves(self):
        url = reverse('upload_user_problem_parameters')
        self.assertEquals(resolve(url).func, view_user.upload_user_problem_parameters)

    def test_update_user_problem_url_resolves(self):
        url = reverse('update_user_problem', args=[1])
        self.assertEquals(resolve(url).func, view_user.update_user_problem)

    def test_submit_user_problem_url_resolves(self):
        url = reverse('submit_user_problem', args=[1])
        self.assertEquals(resolve(url).func, view_user.submit_user_problem)

    def test_user_download_problem_url_resolves(self):
        url = reverse('user_download_zip', args=[1])
        self.assertEquals(resolve(url).func, view_user.user_download_zip)
    
    def test_delete_user_problem_url_resolves(self):
        url = reverse('delete_user_problem', args=[1])
        self.assertEquals(resolve(url).func, view_user.delete_user_problem)