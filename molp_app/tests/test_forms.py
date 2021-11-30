from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import ProblemForm, ParametersForm, UserProblemForm, UserParametersForm


class TestForms(TestCase):

    def test_problem_form_valid(self):
        lp_file = open('examples/portfel_projektów_bicrit.lp','rb')
                
        file_dict = {'lp': SimpleUploadedFile(lp_file.name, lp_file.read())}
        form = ProblemForm({}, file_dict)
        
        self.assertTrue(form.is_valid())
    
    def test_parameters_form_valid(self):
        w_file = open('examples/portfel_projektów_bicrit_weights.txt','rb')
        y_file = open('examples/portfel_projektów_bicrit_reference.txt','rb')  
                
        file_dict = {'weights': SimpleUploadedFile(w_file.name, w_file.read()),
                     'reference': SimpleUploadedFile(y_file.name, y_file.read())}
        form = ParametersForm({}, file_dict)
        
        self.assertTrue(form.is_valid())

    def test_problem_empty_form_not_valid(self):
        form = ProblemForm({}, {})
        
        self.assertFalse(form.is_valid())

    def test_parameters_empty_form_valid(self):
        form = ParametersForm({}, {})
        
        self.assertTrue(form.is_valid())


class TestUserForms(TestCase):

    def test_user_problem_form_valid(self):
        lp_file = open('examples/portfel_projektów_bicrit.lp','rb')
                
        file_dict = {'lp': SimpleUploadedFile(lp_file.name, lp_file.read())}
        form = UserProblemForm({}, file_dict)
        
        self.assertTrue(form.is_valid())
    
    def test_user_parameters_form_valid(self):
        w_file = open('examples/portfel_projektów_bicrit_weights.txt','rb')
        y_file = open('examples/portfel_projektów_bicrit_reference.txt','rb')  
                
        file_dict = {'weights': SimpleUploadedFile(w_file.name, w_file.read()),
                     'reference': SimpleUploadedFile(y_file.name, y_file.read())}
        form = UserParametersForm({}, file_dict)
        
        self.assertTrue(form.is_valid())

    def test_user_problem_empty_form_not_valid(self):
        form = UserProblemForm({}, {})
        
        self.assertFalse(form.is_valid())

    def test_user_parameters_empty_form_valid(self):
        form = UserParametersForm({}, {})
        
        self.assertTrue(form.is_valid())

