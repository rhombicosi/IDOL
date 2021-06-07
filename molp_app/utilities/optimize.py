from mip import *
import argparse
import django
django.setup()

from molp_app.utilities.file_helper import save_files
import molp_app.utilities.constants as constants
from molp_app.models import Problem


parser = argparse.ArgumentParser()
parser.add_argument("-pk", "--problemkey", help="problem key", type=int)
parser.add_argument("-i", "--ifile", help="input file")
parser.add_argument("-o", "--ofile", help="output file")
args = parser.parse_args()


def main(argv):
    inputfile = ''
    outputfile = ''
    problemkey = ''
    try:
        if args.ifile:
            inputfile = args.ifile
        if args.ofile:
            outputfile = args.ofile
        if args.problemkey:
            problemkey = args.problemkey
    except argparse.ArgumentError:
        print(argparse.ArgumentError('Incorrect argument'))

    print('Input file is {}'.format(inputfile))
    print('Output file is {}'.format(outputfile))
    print('Problem key is {}'.format(problemkey))

    # model = read(inputfile)
    model = Model(solver_name=CBC)
    model.read(inputfile)
    # model.Params.TIME_LIMIT = constants.TIMELIMIT
    # model.optimize()
    model.optimize(max_seconds=100)
    problem = Problem.objects.get(pk=problemkey)

    # save solution into .sol file
    save_files('solution', '/problems/solutions/', 'sol', 'result', problem, model)


if __name__ == "__main__":
    # main(sys.argv[1:])
    main(args)
