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
    ]:
        if os.path.exists(dirname):
            assert os.path.isdir(dirname), 'File "' + \
                dirname + '" is not a directory.'
        else:
            os.mkdir(dirname)


def LoadNewBMS():
    flist = os.listdir(ZIP_FOLDER_NAME) + os.listdir(NORMALIZE_FOLDER_NAME) + os.listdir(MINIFY_FOLDER_NAME)
    counter = max(map(lambda s: int(os.path.splitext(s)[0]), flist))
    print('Starting from: %d'%(counter+1))

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
                infofile = os.path.join(JSON_FOLDER_NAME, '%06d.json' % counter)
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
                traceback.print_exc()


def main():
    GenerateDefaultDir()
    LoadNewBMS()


if __name__ == '__main__':
    main()
