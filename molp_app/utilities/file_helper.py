import time
from pathlib import Path
from gurobipy import *

from django.conf import settings
from django.core.files import File


def read_txt(path, file):
    # data_folder = Path("C:/Users/voka/!PY/django_code/gurobi_samples/")
    data_folder = Path(path)
    # file_to_open = data_folder / "weights.txt"
    file_to_open = data_folder / file
    text_file = open(file_to_open, "r")

    lines = text_file.readlines()

    param_array = []

    for li in lines:
        param_array = [float(val) for val in list(li.split(","))]

    print(param_array)

    text_file.close()

    return param_array


def save_gurobi_files(filename, filepath, extension, model, problem, field):
    # filename = 'chebknap'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # filepath = '/problems/chebyshev/'
    # temp_path = settings.MEDIA_ROOT + filepath + name + timestr + '_temp.lp'
    temp_path = settings.MEDIA_ROOT + filepath + filename + timestr + '_temp.' + extension

    # write model into temporary file with gurobi
    model.write(temp_path)

    # add file to the model
    f = open(temp_path)
    # problem.chebyshev.save(filename + timestr + '.lp', File(f))

    if field == 'chebyshev':
        problem.chebyshev.save(filename + timestr + '.' + extension, File(f))
    elif field == 'result':
        problem.result.save(filename + timestr + '.' + extension, File(f))

    f.close()

    # remove temporary file
    os.remove(temp_path)