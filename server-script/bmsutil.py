import sys
import os
import hashlib
import zipfile
import shutil
import subprocess
from PIL import Image


def MD5(filename):
    """Calculate MD5 value of given file."""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def IsBMSFile(filename):
    """Check whether given file is BMS file, based on filename."""
    name, ext = os.path.splitext(filename)
    return ext.lower() in ['.bms', '.bme', '.bml', '.pms']


def IsZIPFile(filename):
    """Check whether given file is ZIP file, based on filename."""
    name, ext = os.path.splitext(filename)
    return ext.lower() == '.zip'


def ChangeZIPName(filename):
    """Change name of zip file as md5 hash value of it."""

    assert IsZIPFile(filename), "Given file is not a ZIP file."

    # We should know explicit path, for renaming purpose
    filename = os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    newFilename = os.path.join(dirname, 'ZIP_' + MD5(filename) + '.zip')

    os.rename(filename, newFilename)

    return newFilename


def ExtractZIP(filename, targetDir):

    assert IsZIPFile(filename), "Given file is not a ZIP file."
    name, ext = os.path.splitext(filename)

    extractDir = os.path.join(targetDir, os.path.basename(name))

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extractDir)

    return extractDir


def NormalizeWav(filename, destfilename):
    _, ext = os.path.splitext(filename)

    destdir = os.path.abspath(os.path.dirname(destfilename))

    if not os.path.isdir(destdir):
        os.mkdir(destdir)

    shutil.copyfile(filename, os.path.join(
        destdir, '____bms_archive_convert____' + ext))

    subprocess.check_call(['ffmpeg', '-i', '____bms_archive_convert____' + ext, '-aq', '4', '____bms_archive_convert____result____.ogg', '-acodec', 'libvorbis', '-y'], cwd=destdir,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    os.rename(os.path.join(
        destdir, '____bms_archive_convert____result____.ogg'), destfilename)

    os.remove(os.path.join(destdir, '____bms_archive_convert____' + ext))


def NormalizeBmp(filename, destfilename):
    x = Image.open(filename)
    x.save(destfilename, 'png')


def CompressFolder(src, dst):
    zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()


def ListFolder(src):
    ret = {'isdir': True, 'content': {}}
    abs_src = os.path.normpath(os.path.abspath(src))
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.normpath(
                os.path.abspath(os.path.join(dirname, filename)))
            orgdir = absname[len(abs_src)+1:].split(os.sep)

            md5v = MD5(absname)
            size = os.path.getsize(absname)
            ptr = ret
            filetype = subprocess.check_output(['file', '-b', absname])
            filetype = filetype.decode('utf-8')
            for i in orgdir[:-1]:
                if i not in ptr['content']:
                    ptr['content'][i] = {'isdir': True, 'content': {}}
                ptr = ptr['content'][i]

            ptr['content'][orgdir[-1]] = {
                'isdir': False,
                'md5': md5v,
                'size': size,
                'file': filetype,
            }

    return ret
