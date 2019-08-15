import os
import sys
import traceback
import zipfile
import re
import hashlib
import json


from bmsutil import *
from config import *
from bmsparser import BMS


def GuessKey(keyList):

    def RemoveImplicitSubtitle(title):
        if title == '':
            return title
        sublist = ['--', '～～', '()', '[]', '<>', '""']

        for s, e in sublist:
            if title[-1] == e:
                ind = title[:-1].rfind(s)
                if ind == -1:
                    return title.strip()
                else:
                    return title[:ind].strip()

        return title.strip()

    keyList = list(map(RemoveImplicitSubtitle, keyList))

    keyList.sort(key=len)

    if(all(x.startswith(keyList[0]) for x in keyList)):
        return keyList[0]

    return "N/A_" + keyList[0]


def ExtractZIPData(zipName):
    zipName = ChangeZIPName(zipName)
    zipCode, ext = os.path.splitext(os.path.basename(zipName))

    zipJSON = {}
    zipJSON['code'] = zipCode
    zipJSON['bms'] = []

    extractDir = ExtractZIP(zipName, EXTRACT_FOLDER_NAME)

    for fileName in os.listdir(extractDir):
        fileName = os.path.join(extractDir, fileName)
        if IsBMSFile(fileName):
            bms = BMS(fileName)

            bmsJSON = {}

            bmsJSON['title'] = bms.getTitle()
            bmsJSON['md5'] = bms.getMD5()
            bmsJSON['artist'] = bms.getArtist()

            zipJSON['bms'].append(bmsJSON)

    for key in ['title', 'artist']:
        keyList = list(map(lambda s: s[key], zipJSON['bms']))
        zipJSON[key] = GuessKey(keyList)

    jsonFilename = os.path.join(JSON_FOLDER_NAME, zipCode + '.json')

    with open(jsonFilename, 'w') as jsonFile:
        jsonFile.write(json.dumps(zipJSON, sort_keys=True, indent=4))
        jsonFile.write('\n')

    os.rename(zipName, os.path.join(ZIP_FOLDER_NAME, zipCode + '.zip'))

    print('OK! [{0}] {1}'.format(zipJSON['artist'], zipJSON['title']))


def GenerateDefaultDir():
    for dirname in [
            ZIP_FOLDER_NAME,
            EXTRACT_FOLDER_NAME,
            JSON_FOLDER_NAME,
            NEW_FOLDER_NAME]:
        if os.path.exists(dirname):
            assert os.path.isdir(dirname), 'File "' + \
                dirname + '" is not a directory.'
        else:
            os.mkdir(dirname)


def LoadNewBMS():
    for fileName in os.listdir(NEW_FOLDER_NAME):
        fileName = os.path.join(NEW_FOLDER_NAME, fileName)
        if IsZIPFile(fileName):
            try:
                ExtractZIPData(fileName)
            except Exception:
                traceback.print_exc()


def CreateJSON():

    BMS2ZIP = {}
    ZIP2BMS = {}

    for fileName in os.listdir(JSON_FOLDER_NAME):
        fileName = os.path.join(JSON_FOLDER_NAME, fileName)
        with open(fileName, 'r') as f:
            jsonData = json.loads(f.read())

        zipCode = jsonData['code']
        ZIP2BMS[zipCode] = jsonData

        for bms in jsonData['bms']:
            bmsHash = 'BMS_' + bms['md5']

            if bmsHash not in BMS2ZIP:
                BMS2ZIP[bmsHash] = []

            BMS2ZIP[bmsHash].append(zipCode)

    with open('BMS2ZIP.json', 'w') as f:
        jstr = json.dumps(BMS2ZIP, sort_keys=True, indent=4)
        f.write(jstr + '\n')

    with open('BMS2ZIP.mini.json', 'w') as f:
        jstr = json.dumps(BMS2ZIP, ensure_ascii=False, separators=(',', ':'))
        f.write(jstr + '\n')

    with open('ZIP2BMS.json', 'w') as f:
        jstr = json.dumps(ZIP2BMS, sort_keys=True, indent=4)
        f.write(jstr + '\n')

    with open('ZIP2BMS.mini.json', 'w') as f:
        jstr = json.dumps(ZIP2BMS, ensure_ascii=False, separators=(',', ':'))
        f.write(jstr + '\n')


def main():
    """Main Logic"""

    GenerateDefaultDir()
    LoadNewBMS()
    CreateJSON()


if __name__ == '__main__':
    main()
