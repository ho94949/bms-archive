import bmsutil
import bmsdata
import os
import shutil
from config import *
import json

def MakePackage(zipName, normalizedName, minifiedName, infoFile):

    ErrorList = []

    basename, _ = os.path.splitext(os.path.basename(zipName))

    originalDir = os.path.join(EXTRACT_FOLDER_NAME, basename)
    normalizeDir = os.path.join(NORMALIZE_EXTRACT_FOLDER_NAME, basename)
    minifyDir = os.path.join(MINIFY_EXTRACT_FOLDER_NAME, basename)

    for d in [originalDir, normalizeDir, minifyDir]:
        if not os.path.isdir(d):
            os.mkdir(d)

    extractDir = bmsutil.ExtractZIP(zipName, EXTRACT_FOLDER_NAME)

    BMSList = []

    for f in os.listdir(extractDir):
        f = os.path.join(extractDir, f)
        if bmsutil.IsBMSFile(f):
            ext = 'bms'
            if f[-3:] == 'pms':
                ext = 'pms'
            BMSList.append((ext, bmsdata.LoadBMSFile(f)))

    assert len(BMSList) > 0, "Empty BMS file not allowed"

    WAVList = set()
    BMPList = set()
    StageList = set()

    for e, b in BMSList:

        fname = b.md5 + '.' + e
        with open(os.path.join(normalizeDir, fname), 'wb') as f:
            f.write(b.raw)

        with open(os.path.join(minifyDir, fname), 'wb') as f:
            f.write(b.raw)

        WAVList = WAVList | set(b.wav)
        BMPList = BMPList | set(b.bmp)
        if b.banner is not None:
            StageList.add(b.banner)
        if b.stagefile is not None:
            StageList.add(b.stagefile)

    for f in WAVList:
        if f == '':
            continue
        ff = os.path.join(extractDir, f)
        name, ext = os.path.splitext(ff)
        fileSearchOrder = [ff, name + '.wav', name + '.ogg']

        for q in fileSearchOrder:
            if os.path.exists(q) and not os.path.isdir(q):
                namef, _ = os.path.splitext(f)
                bmsutil.NormalizeWav(q, os.path.join(
                    normalizeDir, namef + '.ogg'))
                shutil.copy(os.path.join(normalizeDir, namef+'.ogg'),
                            os.path.join(minifyDir, namef+'.ogg'))
                break
        else:
            ErrorList.append('WAV File not found: ' + f)

    for f in BMPList:
        if f == '':
            continue
        ff = os.path.join(extractDir, f)
        if os.path.exists(ff) and not os.path.isdir(ff):
            shutil.copy(ff, os.path.join(normalizeDir, f))
        else:
            ErrorList.append('BMP file not found: ' + f)

    for f in StageList:
        if f == '':
            continue
        ff = os.path.join(extractDir, f)
        if os.path.exists(ff) and not os.path.isdir(ff):
            shutil.copy(ff, os.path.join(normalizeDir, f))
            shutil.copy(ff, os.path.join(minifyDir, f))
        else:
            ErrorList.append('BMP file not found: ' + f)

    bmsutil.CompressFolder(normalizeDir, normalizedName)
    bmsutil.CompressFolder(minifyDir, minifiedName)

    shutil.rmtree(extractDir)
    shutil.rmtree(normalizeDir)
    shutil.rmtree(minifyDir)

    bmsinfo = {'bms': []}

    TitleList = []
    ArtistList = []
    for e, b in BMSList:
        if b.title:
            TitleList.append(b.title)
        if b.artist:
            ArtistList.append(b.artist)

        bi = {'title': b.title, 'subtitle': b.subtitle, 'artist': b.artist, 'subartist': b.subartist, 'md5': b.md5}
        bmsinfo['bms'].append(bi)

    try:
        Title = TitleList[0]
        if any(Title != t for t in TitleList):
            Title = None
    except IndexError:
        Title = None

    if Title is None:
        ErrorList.append('Title not set')

    try:
        Artist = min(ArtistList, key=len)
        if any(not a.startswith(Artist) for a in ArtistList):
            Artist = None
    except ValueError:
        Artist = None

    if Artist is None:
        ErrorList.append('Artist not set')

    bmsinfo['title'] = Title
    bmsinfo['trtist'] = Artist

    with open(infoFile, 'w') as f:
        f.write(json.dumps(bmsinfo,ensure_ascii=False))
        f.write('\n')
    
    print('OK!', Title, Artist)

    return ErrorList