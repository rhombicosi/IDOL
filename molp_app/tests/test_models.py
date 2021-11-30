from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Problem, ProblemParameters, ProblemChebyshev, UserProblem, UserProblemParameters, UserProblemChebyshev

class TestModels(TestCase):

    def setUp(self):

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')
        self.ch_byte = open('examples/Chebyshev_1_1_portfel_projektów_bicrit.lp','rb')   
        
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.w = SimpleUploadedFile(self.w_byte.name, self.w_byte.read())
        self.y = SimpleUploadedFile(self.y_byte.name, self.y_byte.read())
        self.ch = SimpleUploadedFile(self.ch_byte.name, self.ch_byte.read())

        self.problem = Problem.objects.create(lp=self.lp)
    
    def test_problem_model_delete(self):
        problem = Problem.objects.get(pk=self.problem.pk)
        problem.delete()

        self.assertFalse(Problem.objects.filter(pk=self.problem.pk).exists())

    def test_problem_weights_model_delete(self):
        ProblemParameters.objects.create(problem=self.problem, weights=self.w)

        problem = Problem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete_weights()
        
        self.assertFalse(ProblemParameters.objects.filter(problem=problem).exists())

    def test_problem_reference_model_delete(self):
        ProblemParameters.objects.create(problem=self.problem, reference=self.y)

        problem = Problem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete_reference()
        
        self.assertFalse(ProblemParameters.objects.filter(problem=problem).exists())

    def test_problem_parameters_model_delete(self):
        ProblemParameters.objects.create(problem=self.problem, weights=self.w)
        ProblemParameters.objects.create(problem=self.problem, reference=self.y)

        problem = Problem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete()
        
        self.assertFalse(ProblemParameters.objects.filter(problem=problem).exists())

    def test_problem_chebyshev_model_delete(self):
        ProblemChebyshev.objects.create(problem=self.problem, chebyshev=self.ch)

        problem = Problem.objects.get(pk=self.problem.pk)
                
        problem.chebyshev.first().delete()
        
        self.assertFalse(ProblemChebyshev.objects.filter(problem=problem).exists())


class TestUserModels(TestCase):

    def setUp(self):

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')
        self.ch_byte = open('examples/Chebyshev_1_1_portfel_projektów_bicrit.lp','rb')   
        
        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.w = SimpleUploadedFile(self.w_byte.name, self.w_byte.read())
        self.y = SimpleUploadedFile(self.y_byte.name, self.y_byte.read())
        self.ch = SimpleUploadedFile(self.ch_byte.name, self.ch_byte.read())

        self.problem = UserProblem.objects.create(lp=self.lp)
    
    def test_user_problem_model_delete(self):
        problem = UserProblem.objects.get(pk=self.problem.pk)
        problem.delete()

        self.assertFalse(UserProblem.objects.filter(pk=self.problem.pk).exists())

    def test_user_problem_weights_model_delete(self):
        UserProblemParameters.objects.create(problem=self.problem, weights=self.w)

        problem = UserProblem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete_weights()
        
        self.assertFalse(UserProblemParameters.objects.filter(problem=problem).exists())

    def test_user_problem_reference_model_delete(self):
        UserProblemParameters.objects.create(problem=self.problem, reference=self.y)

        problem = UserProblem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete_reference()
        
        self.assertFalse(UserProblemParameters.objects.filter(problem=problem).exists())

    def test_user_problem_parameters_model_delete(self):
        UserProblemParameters.objects.create(problem=self.problem, weights=self.w)
        UserProblemParameters.objects.create(problem=self.problem, reference=self.y)

        problem = UserProblem.objects.get(pk=self.problem.pk)
        for param in problem.parameters.all():
            param.delete()
        
        self.assertFalse(UserProblemParameters.objects.filter(problem=problem).exists())

    def test_user_problem_chebyshev_model_delete(self):
        UserProblemChebyshev.objects.create(problem=self.problem, chebyshev=self.ch)

        problem = UserProblem.objects.get(pk=self.problem.pk)
                
        problem.chebyshev.first().delete()
        
        self.assertFalse(UserProblemChebyshev.objects.filter(problem=problem).exists())

