from mip import *
import numpy as np

import os
from shutil import copyfile

from django.conf import settings

from datetime import datetime


def parse_gurobi(problem):
    lppath = settings.MEDIA_ROOT + '/problems/xmls/'
    lpfile = os.path.basename(problem.xml.path)

    # parse Gurobi multi lp format
    extension = '.txt'

    pre, ext = os.path.splitext(lpfile)

    print(f'{pre} {ext}')

    src = lppath + lpfile

    print(src)
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