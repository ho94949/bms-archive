import os
import sys
import traceback
import zipfile
import re
import hashlib
import json
import shutil

import bmspackage

from bmsutil import *
from config import *
from bmsparser import BMS
from bmsdata import *

def GenerateDefaultDir():
    for dirname in [
            ZIP_FOLDER_NAME,
            EXTRACT_FOLDER_NAME,
            JSON_FOLDER_NAME,
            NEW_FOLDER_NAME,
            NORMALIZE_EXTRACT_FOLDER_NAME,
            MINIFY_EXTRACT_FOLDER_NAME,
            NORMALIZE_FOLDER_NAME,
            MINIFY_FOLDER_NAME,
            JSON_EXTRACT_FOLDER_NAME,
    ]:
        if os.path.exists(dirname):
            assert os.path.isdir(dirname), 'File "' + \
                dirname + '" is not a directory.'
        else:
            os.mkdir(dirname)

JSON_CURRENT_VER = 2

def LoadJSON(f):
    ed = ExtractZIP(f, JSON_EXTRACT_FOLDER_NAME)

    lf = ListFolder(ed)
    lf.pop('isdir', None)
    lf['bms'] = []

    for k in lf['content']:
        if IsBMSFile(k):
            bd = LoadBMSFile(os.path.join(ed, k))
            jf = BMSData2JSON(bd)
            jf.pop('bmp', None)
            jf.pop('wav', None)
            lf['bms'].append(jf)
            
    lf['ver'] = JSON_CURRENT_VER

    shutil.rmtree(ed)
    return lf


def ReloadJSON(force=False):

    for z in sorted(os.listdir(NORMALIZE_FOLDER_NAME)):
        print('Making JSON for ' + z)
        name, ext = os.path.splitext(z)
        if ext != '.zip':
            continue

        dat = {}

        jsonFile = os.path.join(JSON_FOLDER_NAME, name + '.json')
        try:
            with open(jsonFile, 'r') as f:
                dat = json.loads(f.read())
        except Exception:
            pass


        if (not force) and ('ver' in dat and dat['ver'] == JSON_CURRENT_VER):
            continue

        try:
            dat = LoadJSON(os.path.join(NORMALIZE_FOLDER_NAME, z))
            with open(jsonFile, 'w') as f:
                f.write(json.dumps(dat, ensure_ascii=False,
                                    sort_keys=True, indent=2))
                f.write('\n')
        except Exception:
            print('\n')
            print('===')
            print('Error on making JSON on ' + z)
            traceback.print_exc()
            print('===')
            print('\n')


def LoadNewBMS():
    flist = os.listdir(ZIP_FOLDER_NAME) + \
        os.listdir(NORMALIZE_FOLDER_NAME) + os.listdir(MINIFY_FOLDER_NAME)
    ff = list(map(lambda s: int(os.path.splitext(s)[0]), flist))
    if ff == []:
        counter = 0
    else:
        counter = max(ff)
    print('Starting from: %d' % (counter+1))

    for fileName in os.listdir(NEW_FOLDER_NAME):
        fileName = os.path.join(NEW_FOLDER_NAME, fileName)
        if IsZIPFile(fileName):
            try:
                counter += 1
                destfile = os.path.join(ZIP_FOLDER_NAME, '%06d.zip' % counter)
                normalfile = os.path.join(
                    NORMALIZE_FOLDER_NAME, '%06d.zip' % counter)
                minifile = os.path.join(
                    MINIFY_FOLDER_NAME, '%06d.zip' % counter)
                infofile = os.path.join(
                    JSON_FOLDER_NAME, '%06d.json' % counter)
                res = bmspackage.MakePackage(
                    fileName, normalfile, minifile, infofile)
                if res:
                    sys.stderr.write('Error on %06d\n' % counter)
                    sys.stderr.flush()

                    print('\n')
                    print('===')
                    print('Error on %06d' % counter)
                    for i in res:
                        print(i)
                    print('===')
                    print('\n')

                os.rename(fileName, destfile)
            except Exception:
                print('\n')
                print('===')
                print('Critical Error on %06d' % counter)
                traceback.print_exc()
                print('===')
                print('\n')


def main():
    GenerateDefaultDir()
    LoadNewBMS()
    #ReloadJSON()


if __name__ == '__main__':
    main()
