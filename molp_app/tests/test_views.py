from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Problem, ProblemParameters, ProblemChebyshev

from celery.contrib.testing.worker import start_worker
from molp_project.celery import app

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.problem_list = reverse('problem_list')
        self.upload_problem_parameters = reverse('upload_problem_parameters')

        self.lp_file = open('examples/portfel_projektów_bicrit.lp','r') 
        self.w_file = open('examples/portfel_projektów_bicrit_weights.txt','r')  
        self.y_file = open('examples/portfel_projektów_bicrit_reference.txt','r')

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')
        self.ch_byte = open('examples/Chebyshev_1_1_portfel_projektów_bicrit.lp','rb')   


    def test_problem_list_GET(self):

        response = self.client.get(self.problem_list)    
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_problem_lp_upload(self):      

        response = self.client.post(self.upload_problem_parameters, {'lp': self.lp_file})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')        

    def test_problem_lp_weights_upload(self):

        response = self.client.post(
            self.upload_problem_parameters, 
            {'lp': self.lp_file, 
             'weights': self.w_file
            })
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_problem_lp_weights_y_upload(self):

        response = self.client.post(
            self.upload_problem_parameters, 
            {'lp': self.lp_file, 
             'weights': self.w_file,
             'reference': self.y_file
            })
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_problem_empty_upload(self):      

        response = self.client.post(self.upload_problem_parameters, {})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_problem.html')

    def test_delete_problem(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = Problem.objects.create(lp=self.lp)

        delete_problem = reverse('delete_problem', kwargs={'pk': self.problem.pk})

        response = self.client.post(delete_problem)
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Problem.objects.count(), 0)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_update_problem_weights(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = Problem.objects.create(lp=self.lp)

        update_problem = reverse('update_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(update_problem, {'weights': self.w_file})
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.problem.parameters.first().weights, 
            'problems/parameters/weights/portfel_projektów_bicrit_weights.txt')

    def test_update_problem_reference(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = Problem.objects.create(lp=self.lp)

        update_problem = reverse('update_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(update_problem, {'reference': self.y_file})
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.problem.parameters.first().reference, 
            'problems/parameters/reference/portfel_projektów_bicrit_reference.txt')

    def test_download_zip(self):
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = Problem.objects.create(lp=self.lp)
        
        self.ch = SimpleUploadedFile(self.ch_byte.name, self.ch_byte.read())
        ProblemChebyshev.objects.create(problem=self.problem, chebyshev=self.ch)

        download_zip = reverse('download_zip', kwargs={'pk': self.problem.pk})
        response = self.client.post(download_zip)
        self.assertEquals(response.status_code, 302)


class TestCeleryViews(SimpleTestCase):
    databases = '__all__'
    
    def setUp(self):
        self.client = Client()

        self.problem_list = reverse('problem_list')
        self.upload_problem_parameters = reverse('upload_problem_parameters')

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')  

        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.w = SimpleUploadedFile(self.w_byte.name, self.w_byte.read())
        self.y = SimpleUploadedFile(self.y_byte.name, self.y_byte.read())

        self.problem = Problem.objects.create(lp=self.lp)
        
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.celery_worker = start_worker(app, perform_ping_check=False)
        self.celery_worker.__enter__()

    def test_submit_problem(self):        

        submit_problem = reverse('submit_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_submit_problem_with_weights(self):
        
        ProblemParameters.objects.create(problem=self.problem, weights=self.w)
        
        submit_problem = reverse('submit_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 2)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')

    def test_submit_problem_with_reference(self):
        
        ProblemParameters.objects.create(problem=self.problem, reference=self.y)
        
        submit_problem = reverse('submit_problem', kwargs={'pk': self.problem.pk})
        response = self.client.post(submit_problem)
        
        self.assertEquals(self.problem.chebyshev.count(), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'problem_list.html')
    
    def TearDown(self):
        self.celery_worker.__exit__(None, None, None)        
    