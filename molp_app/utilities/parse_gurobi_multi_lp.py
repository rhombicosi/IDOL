import errno

import requests
from mip import *
import numpy as np

import os
from shutil import copyfile

from django.conf import settings

from datetime import datetime

from django.core.files.temp import NamedTemporaryFile
from django.core import files
from django.core.files import File

def read_url(url):
    in_memory_file = requests.get(url, stream=True)
    some_temp_file = NamedTemporaryFile()

    for block in in_memory_file.iter_content(1024*8):
        if not block:
            break

        some_temp_file.write(block)

    return some_temp_file


# working with cloud storage
def parse_gurobi_url(problem):

    lpurl = problem.xml.url

    lp_temp_file = read_url(lpurl)

    extension = '.txt'
    pre, ext = lpurl.split('/')[-1].split('.')
    dst = pre + extension

    lp_temp_file.flush()
    problem.txt = files.File(lp_temp_file, name=dst)
    problem.save()

    # get txt file with multiobjective problem
    txturl = problem.txt.url
    txt_temp_file = read_url(txturl)
    txt_temp_file.flush()
    txt_temp_file.seek(0)
    lines = txt_temp_file.readlines()

    txt_temp_file.close()

    for line in range(len(lines)):
        lines[line] = lines[line].decode("utf-8")

    # parse multiobjective Gurobi format
    keywords = {'st': ['subject to', 'st', 's.t.'], 'sns': ['max', 'min']}

    count = 0
    st_line = 0
    sns_line = 0
    sns = ''

    # find objectives and constraints in txt file
    # Strips the newline character
    for line in lines:
        count += 1
        # line = line.decode("utf-8")
        for w in keywords['st']:
            if w == line.strip().casefold():
                st_line = count
                print(st_line)
                print("Line{}: {}".format(count, line.strip()))
        for w in keywords['sns']:
            if line.strip().casefold().startswith(w):
                sns = w
                sns_line = count
                print(sns)
                print(sns_line)
                print("Line{}: {}".format(count, line.strip()))

    # create files for each objective
    start = sns_line + 1
    end = st_line

    NumOfObj = (end - start) // 2

    timestr = datetime.now()
    timestr = str(timestr.microsecond)

    obj_temp_files = []
    for obj in range(NumOfObj):
        f = NamedTemporaryFile(mode='wt', suffix=".txt", prefix="new_objectives_" + str(obj) + "_" + timestr)
        obj_temp_files.append(f)

        if sns == 'max':
            f.write('MAXIMIZE\n')
        else:
            f.write('MINIMIZE\n')
        f.write('Obj' + str(obj) + ':\n')
        f.write(lines[start - 1 + (obj * 2 + 1)])
        f.write('\n')

    # create file with constraints and variables
    temp_constr_file = NamedTemporaryFile(mode='wt', suffix=".txt", prefix="new_constrs_" + str(obj) + "_" + timestr)

    for l in range(st_line - 1, len(lines)):
        temp_constr_file.write(lines[l])
    # f.close()

    # opening first file in append mode and second file in read mode
    problem_temp_files = []
    for obj in range(NumOfObj):

        obj_lp_path = NamedTemporaryFile(mode='wt', suffix='.lp', prefix="new_problem_" + str(obj) + "_" + timestr)
        problem_temp_files.append(obj_lp_path)
        # obj_lp_path.flush()
        f1 = open(obj_lp_path.name, 'a+')

        obj_temp_files[obj].flush()
        obj_temp_files[obj].seek(0)
        f2 = open(obj_temp_files[obj].name, 'r')

        temp_constr_file.flush()
        temp_constr_file.seek(0)
        f3 = open(temp_constr_file.name, 'r')

        # appending the contents of the second file to the first file
        # f2.flush()
        f1.write(f2.read())
        # f3.flush()
        f1.write(f3.read())

    return timestr, NumOfObj, problem_temp_files


def submit_cbc(problem):
    print("Task run!!!")

    timestr, NumOfObj, problem_temp_files = parse_gurobi_url(problem)

    f = {}
    weights = []
    ystar = {}
    models = {}
    rho = 0.001

    for obj in range(NumOfObj):

        m = Model(solver_name=CBC)
        models[obj] = m

        obj_lp_path = problem_temp_files[obj].name

        print(obj_lp_path)
        problem_temp_files[obj].flush()
        m.read(obj_lp_path)
        print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))

        m.max_gap = 0.25
        status = m.optimize(max_seconds=90)

        if status == OptimizationStatus.OPTIMAL:
            print('optimal solution cost {} found'.format(m.objective_value))
            ystar[obj] = m.objective_value
        elif status == OptimizationStatus.FEASIBLE:
            print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
            ystar[obj] = m.objective_value
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
            ystar[obj] = m.objective_bound

    # chebyshev scalarization
    ch = Model(sense=MINIMIZE, solver_name=CBC)
    m = models[0]
    print(ystar)
    for v in m.vars:
        ch.add_var(name=v.name, var_type=v.var_type)

    for c in m.constrs:
        ch.add_constr(c.expr, c.name)

    ch.add_var(name='s', var_type=CONTINUOUS)
    ch.objective = ch.vars['s']

    for i in range(NumOfObj):
        ch.add_var(name='f{}'.format(i + 1), var_type=CONTINUOUS)
        f[i] = ch.vars['f{}'.format(i + 1)]
        weights = np.full(NumOfObj, 1 / NumOfObj)

    for i in range(NumOfObj):
        ch.add_constr(
            weights[i] * (ystar[i] - f[i]) + xsum(rho * (ystar[i] - f[i]) for i in range(NumOfObj)) <= ch.vars['s'],
            'sum{}'.format(i + 1))

    for obj in range(NumOfObj):

        m = models[obj]
        o = m.objective
        ch.add_constr(f[obj] - o == 0, 'f_constr_' + str(obj))

    temp_chebyshev = NamedTemporaryFile(mode='wt', suffix='.lp', prefix="chebyshev_" + timestr)
    ch.write(temp_chebyshev.name)

    # local
    dst = temp_chebyshev.name.split("\\")[-1]
    # heroku
    # dst = temp_chebyshev.name.split("/")[-1]
    print(temp_chebyshev.name)
    temp_chebyshev.flush()

    f = NamedTemporaryFile()
    temp_chebyshev.seek(0)
    data = open(temp_chebyshev.name, 'r')
    for li in data.readlines():
        f.write(bytes(li, 'utf-8'))
    f.flush()
    problem.chebyshev = File(f, name=dst)
    problem.save()


# working with files locally
def parse_gurobi(problem):
    lppath = settings.MEDIA_ROOT + '/problems/xmls/'

    # print(lppath)
    lpfile = os.path.basename(problem.xml.path)

    # parse Gurobi multi lp format
    extension = '.txt'

    pre, ext = os.path.splitext(lpfile)

    print(f'{pre} {ext}')

    src = lppath + lpfile

    print(src)

    # Creating a txt folder in media directory
    new_dir_path = os.path.join(settings.MEDIA_ROOT + '/problems/', 'txt')
    try:
        os.makedirs(new_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # directory already exists
            pass
        else:
            print(e)

    dst = settings.MEDIA_ROOT + '/problems/txt/' + pre + extension

    copyfile(src, dst)

    keywords = {'st': ['subject to', 'st', 's.t.'], 'sns': ['max', 'min']}

    # Using readlines()
    txt = open(dst, 'r')
    Lines = txt.readlines()

    count = 0
    st_line = 0
    sns_line = 0
    sns = ''

    # find objectives and constraints in txt file
    # Strips the newline character
    for line in Lines:
        count += 1

        for w in keywords['st']:
            if w == line.strip().casefold():
                st_line = count
                print(st_line)
                print("Line{}: {}".format(count, line.strip()))
        for w in keywords['sns']:
            if line.strip().casefold().startswith(w):
                sns = w
                sns_line = count
                print(sns)
                print(sns_line)
                print("Line{}: {}".format(count, line.strip()))

    # create files for each objective
    start = sns_line + 1
    end = st_line

    NumOfObj = (end - start) // 2

    timestr = datetime.now()
    timestr = str(timestr.microsecond)

    for obj in range(NumOfObj):
        f = open(settings.MEDIA_ROOT + "/problems/txt/new_objectives_" + str(obj) + "_" + timestr + ".txt", "a")
        if sns == 'max':
            f.write('MAXIMIZE\n')
        else:
            f.write('MINIMIZE\n')
        f.write('Obj' + str(obj) + ':\n')
        f.write(Lines[start - 1 + (obj * 2 + 1)])
        f.write('\n')
        f.close()

    # create file with constraints and variables
    f = open(settings.MEDIA_ROOT + "/problems/txt/new_constrs" + "_" + timestr + ".txt", "a")

    for l in range(st_line - 1, len(Lines)):
        f.write(Lines[l])
    f.close()

    # opening first file in append mode and second file in read mode
    cnstr_txt_path = settings.MEDIA_ROOT + "/problems/txt/new_constrs" + "_" + timestr + ".txt"
    for obj in range(NumOfObj):
        obj_lp_path = settings.MEDIA_ROOT + "/problems/txt/new_problem_" + str(obj) + "_" + timestr + ".lp"
        f1 = open(obj_lp_path, 'a+')
        obj_txt_path = settings.MEDIA_ROOT + "/problems/txt/new_objectives_" + str(obj) + "_" + timestr + ".txt"
        f2 = open(obj_txt_path, 'r')

        f3 = open(cnstr_txt_path, 'r')

        # appending the contents of the second file to the first file
        f1.write(f2.read())
        f1.write(f3.read())

        # relocating the cursor of the files at the beginning
        f1.seek(0)
        f2.seek(0)
        f3.seek(0)

        f1.close()
        f2.close()
        f3.close()

        # remove temporary objective files
        os.remove(obj_txt_path)

    # remove temporary constraints file
    os.remove(cnstr_txt_path)

    return timestr, NumOfObj