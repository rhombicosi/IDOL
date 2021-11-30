from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import UserProblem, UserProblemParameters, UserProblemChebyshev

from celery.contrib.testing.worker import start_worker
from molp_project.celery import app


class TestUserViews(TestCase):

    def setUp(self):

        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

        self.client = Client()
        self.client.login(username='testuser', password='12345')

        self.user_problem_list = reverse('user_problem_list')
        self.upload_user_problem_parameters = reverse('upload_user_problem_parameters')

        self.lp_file = open('examples/portfel_projektów_bicrit.lp','r') 
        self.w_file = open('examples/portfel_projektów_bicrit_weights.txt','r')  
        self.y_file = open('examples/portfel_projektów_bicrit_reference.txt','r')

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')
        self.ch_byte = open('examples/Chebyshev_1_1_portfel_projektów_bicrit.lp','rb')

    def test_user_problem_list_GET(self):

        response = self.client.get(self.user_problem_list)    
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_user_problem_lp_upload(self):      

        response = self.client.post(self.upload_user_problem_parameters, {'lp': self.lp_file})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_user_problem_lp_weights_upload(self):

        response = self.client.post(
            self.upload_user_problem_parameters, 
            {
                'lp': self.lp_file, 
                'weights': self.w_file
            }
        )
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_user_problem_lp_weights_y_upload(self):

        response = self.client.post(
            self.upload_user_problem_parameters, 
            {
                'lp': self.lp_file, 
                'weights': self.w_file,
                'reference': self.y_file
            }
        )
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_user_problem_empty_upload(self):      

        response = self.client.post(self.upload_user_problem_parameters, {})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_user_problem.html')

    def test_delete_user_problem(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = UserProblem.objects.create(lp=self.lp)

        delete_problem = reverse('delete_user_problem', kwargs={'pk': self.problem.pk})

        response = self.client.post(delete_problem)
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(UserProblem.objects.count(), 0)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_update_user_problem_weights(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = UserProblem.objects.create(lp=self.lp)

        update_problem = reverse('update_user_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(update_problem, {'weights': self.w_file})
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.problem.parameters.first().weights, 
            'problems/parameters/weights/portfel_projektów_bicrit_weights.txt')

    def test_update_problem_reference(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = UserProblem.objects.create(lp=self.lp)

        update_problem = reverse('update_user_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(update_problem, {'reference': self.y_file})
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.problem.parameters.first().reference, 
            'problems/parameters/reference/portfel_projektów_bicrit_reference.txt')

    def test_user_download_zip(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = UserProblem.objects.create(lp=self.lp)
        
        self.ch = SimpleUploadedFile(self.ch_byte.name, self.ch_byte.read())
        UserProblemChebyshev.objects.create(problem=self.problem, chebyshev=self.ch)

        download_zip = reverse('user_download_zip', kwargs={'pk': self.problem.pk})
        response = self.client.post(download_zip)
        self.assertEquals(response.status_code, 302)


class TestCeleryUserViews(SimpleTestCase):
    databases = '__all__'
    
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        user = User.objects.create(username='celeryuser')
        user.set_password('12345')
        user.save()

    def setUp(self):

        self.client = Client()
        self.client.login(username='celeryuser', password='12345')

        self.problem_list = reverse('user_problem_list')
        self.upload_problem_parameters = reverse('upload_user_problem_parameters')

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')  

        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.w = SimpleUploadedFile(self.w_byte.name, self.w_byte.read())
        self.y = SimpleUploadedFile(self.y_byte.name, self.y_byte.read())

        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.celery_worker = start_worker(app, perform_ping_check=False)
        self.celery_worker.__enter__()        

    def test_submit_user_problem(self):

        self.problem = UserProblem.objects.create(lp=self.lp)        

        submit_problem = reverse('submit_user_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_submit_user_problem_with_weights(self):

        self.problem = UserProblem.objects.create(lp=self.lp)
        
        UserProblemParameters.objects.create(problem=self.problem, weights=self.w)
        
        submit_problem = reverse('submit_user_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 2)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')

    def test_submit_user_problem_with_reference(self):

        self.problem = UserProblem.objects.create(lp=self.lp)
        
        UserProblemParameters.objects.create(problem=self.problem, reference=self.y)
        
        submit_problem = reverse('submit_user_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_problem_list.html')
