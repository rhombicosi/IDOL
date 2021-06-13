import errno

from urllib.request import urlopen

import requests
from django.core.files.storage import default_storage
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
        # print(Lines[line])

    # parse multiobjective Gurobi format
    keywords = {'st': ['subject to', 'st', 's.t.'], 'sns': ['max', 'min']}

    # txt = open(dst, 'r')
    # Lines = txt.readlines()

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
        # f = open(settings.MEDIA_ROOT + "/problems/txt/new_objectives_" + str(obj) + "_" + timestr + ".txt", "a")
        if sns == 'max':
            f.write('MAXIMIZE\n')
        else:
            f.write('MINIMIZE\n')
        f.write('Obj' + str(obj) + ':\n')
        f.write(lines[start - 1 + (obj * 2 + 1)])
        f.write('\n')
        # f.close()

    for obj in range(NumOfObj):
        print(obj_temp_files[obj].name)
        obj_temp_files[obj].flush()
        obj_temp_files[obj].seek(0)
        data = open(obj_temp_files[obj].name, 'r')
        for l in data.readlines():
            print(l)

    # create file with constraints and variables
    temp_constr_file = NamedTemporaryFile(mode='wt', suffix=".txt", prefix="new_constrs_" + str(obj) + "_" + timestr)

    for l in range(st_line - 1, len(lines)):
        temp_constr_file.write(lines[l])
    # f.close()

    # opening first file in append mode and second file in read mode
    # cnstr_txt_path = settings.MEDIA_ROOT + "/problems/txt/new_constrs" + "_" + timestr + ".txt"
    # cnstr_txt_path = temp_constr_file.name
    problem_temp_files = []
    for obj in range(NumOfObj):
        # obj_lp_path = settings.MEDIA_ROOT + "/problems/txt/new_problem_" + str(obj) + "_" + timestr + ".lp"
        obj_lp_path = NamedTemporaryFile(mode='wt', suffix='.lp', prefix="new_problem_" + str(obj) + "_" + timestr)
        f1 = open(obj_lp_path.name, 'a+')
        # obj_txt_path = settings.MEDIA_ROOT + "/problems/txt/new_objectives_" + str(obj) + "_" + timestr + ".txt"

        obj_temp_files[obj].seek(0)
        f2 = open(obj_temp_files[obj].name, 'r')

        temp_constr_file.seek(0)
        f3 = open(temp_constr_file.name, 'r')

        # appending the contents of the second file to the first file
        f1.write(f2.read())
        f1.write(f3.read())

        # relocating the cursor of the files at the beginning
        f1.seek(0)
        f2.seek(0)
        f3.seek(0)

        problem_temp_files.append(f1)

        # f1.close()
        f2.close()
        f3.close()

        # remove temporary objective files
        # os.remove(obj_txt_path)

    # f.flush()
    # f.seek(0)
    # data = open(f.name, 'r')
    # for l in data.readlines():
    #     print(l)

    # for obj in range(NumOfObj):
    #     print(problem_temp_files[obj].name)
    #     problem_temp_files[obj].flush()
    #     problem_temp_files[obj].seek(0)
    #     data = open(problem_temp_files[obj].name, 'r')
    #     for l in data.readlines():
    #         print(l)

    # # remove temporary constraints file
    # os.remove(cnstr_txt_path)

    return timestr, NumOfObj, problem_temp_files


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