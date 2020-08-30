from gurobipy import *
import sys
import getopt
import argparse
import os
import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'molp_project.settings')
from molp_app.utilities.file_helper import save_gurobi_files

django.setup()
print(os.getcwd())
import molp_app.utilities.constants as constants

# infile_path = 'C:/Users/voka/!PY/django_code/molp_project/molp_app/media/problems/chebyshev/chebknap20200827-033731.lp'
# timestr = time.strftime("%Y%m%d-%H%M%S")
# outfile_path = 'C:/Users/voka/!PY/django_code/molp_project/molp_app/media/problems/solutions/sol' + timestr + '.sol'
from molp_app.utilities import file_helper

from molp_app.models import Problem
from django.contrib.auth.models import User

parser = argparse.ArgumentParser()
parser.add_argument("-pk", "--problemkey", help="problem key", type=int)
parser.add_argument("-i", "--ifile", help="input file")
parser.add_argument("-o", "--ofile", help="output file")
args = parser.parse_args()
print(args.problemkey)

def main(argv):
    inputfile = ''
    outputfile = ''
    problemkey = ''
    # try:
    #     # opts, args = getopt.getopt(argv, "hi:o:pk:", ["ifile=", "ofile=", "problemkey="])
    #     args = parser.parse_args()
    # except getopt.GetoptError:
    #     print('optimize.py -i <inputfile> -o <outputfile> -pk <problemkey>')
    #     sys.exit(2)
    # for arg in args:
    #     print("arg: " + arg)
    #     if arg == '-h':
    #         print('optimize.py -i <inputfile> -o <outputfile> -pk <problemkey>')
    #         sys.exit()
    #     elif arg == "-i":
    #         inputfile = arg
    #     elif arg == "-o":
    #         outputfile = arg
    #     elif arg == "-pk":
    #         problemkey = arg
    #         print("problem key arg: " + arg)

    try:
        if args.ifile:
            inputfile = args.ifile
        if args.ofile:
            outputfile = args.ofile
        if args.problemkey:
            problemkey = args.problemkey
    except:


    print('Input file is {}'.format(inputfile))
    print('Output file is {}'.format(outputfile))
    print('Problem key is {}'.format(problemkey))

    model = read(inputfile)
    model.Params.TIME_LIMIT = constants.TIMELIMIT
    model.optimize()
    # model.write(outputfile)

    problem = Problem.objects.get(pk=problemkey)

    # save solution into .sol file
    save_gurobi_files('solution', '/problems/solutions/', 'sol', 'result', problem, model)

if __name__ == "__main__":
    # main(sys.argv[1:])
    main(args)