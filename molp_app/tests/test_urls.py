from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ..views import view_common, view_anonymous

class TestUrls(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, view_common.home)

    def test_signup_url_resolves(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, view_common.signup)

    def test_problem_list_url_resolves(self):
        url = reverse('problem_list')
        self.assertEquals(resolve(url).func, view_anonymous.problem_list)

    def test_upload_problem_parameters_url_resolves(self):
        url = reverse('upload_problem_parameters')
        self.assertEquals(resolve(url).func, view_anonymous.upload_problem_parameters)

    def test_update_problem_url_resolves(self):
        url = reverse('update_problem', args=[1])
        self.assertEquals(resolve(url).func, view_anonymous.update_problem)

    def test_submit_problem_url_resolves(self):
        url = reverse('submit_problem', args=[1])
        self.assertEquals(resolve(url).func, view_anonymous.submit_problem)

    def test_download_problem_url_resolves(self):
        url = reverse('download_zip', args=[1])
        self.assertEquals(resolve(url).func, view_anonymous.download_zip)
    
    def test_delete_problem_url_resolves(self):
        url = reverse('delete_problem', args=[1])
        self.assertEquals(resolve(url).func, view_anonymous.delete_problem)