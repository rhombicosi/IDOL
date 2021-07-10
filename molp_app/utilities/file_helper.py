import errno
from pathlib import Path
import os
from datetime import datetime

from io import BytesIO
import zipfile

from django.conf import settings
from django.core.files import File

from molp_app.models import Problem, UserProblem


def read_txt(path, file):

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


def write_txt(filename, content):
    text_file = open(filename, "wt")
    n = text_file.write(content)
    text_file.close()


def save_files(filename, filepath, extension, field, entity, model=None, content=None):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    timestr = datetime.now()
    timestr = str(timestr.microsecond)
    temp_path = settings.MEDIA_ROOT + filepath + filename + timestr + '_temp.' + extension

    # Creating a txt folder in media directory
    new_dir_path = os.path.join(settings.MEDIA_ROOT + '/problems/', 'chebyshev')
    try:
        os.makedirs(new_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # directory already exists
            pass
        else:
            print(e)

    # write model into temporary file with gurobi
    if field == 'chebyshev' or field == 'result' or field == 'xml':
        model.write(temp_path)
    else:
        write_txt(temp_path, content)

    # add file to the model
    f = open(temp_path)
    f_path = filename + timestr + '.' + extension

    if field == 'chebyshev':
        entity.chebyshev.save(f_path, File(f))
    elif field == 'result':
        entity.result.save(filename + timestr + '.' + extension, File(f))
    elif field == 'xml':
        entity.xml.save(filename + timestr + '.' + extension, File(f))
    elif field == 'weights':
        entity.weights.save(filename + timestr + '.' + extension, File(f))
    elif field == 'reference':
        entity.reference.save(filename + timestr + '.' + extension, File(f))

    f.close()

    # remove temporary file
    os.remove(temp_path)
    return settings.MEDIA_ROOT + filepath, f_path


def get_context():
    problems = Problem.objects.all()
    problems_neos = problems.filter(solver="NEOS")
    problems_cbc = problems.filter(solver="CBC")

    context = {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_cbc': problems_cbc,
    }

    return context


def get_user_context(request):
    problems = UserProblem.objects.filter(user=request.user)
    problems_neos = problems.filter(solver="NEOS")
    problems_cbc = problems.filter(solver="CBC")

    user_context = {
        'problems': problems,
        'problems_neos': problems_neos,
        'problems_cbc': problems_cbc,
    }

    return user_context
