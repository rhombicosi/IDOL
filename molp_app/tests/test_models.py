from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Problem, ProblemParameters, ProblemChebyshev

class TestModels(TestCase):

    def setUp(self):

        self.lp_file = open('examples/portfel_projektów_bicrit.lp','r') 
        self.w_file = open('examples/portfel_projektów_bicrit_weights.txt','r')  
        self.y_file = open('examples/portfel_projektów_bicrit_reference.txt','r')

        self.lp_byte = open('examples/portfel_projektów_bicrit.lp','rb') 
        self.w_byte = open('examples/portfel_projektów_bicrit_weights.txt','rb')  
        self.y_byte = open('examples/portfel_projektów_bicrit_reference.txt','rb')
        self.ch_byte = open('examples/Chebyshev_1_1_portfel_projektów_bicrit.lp','rb')   
        

        self.lp = SimpleUploadedFile(self.lp_byte.name, self.lp_byte.read())
        self.problem = Problem.objects.create(lp=self.lp)