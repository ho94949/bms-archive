import sys
import os
import hashlib
import zipfile
import shutil
import subprocess


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

    if ext.lower() == '.ogg':
        shutil.copyfile(filename, destfilename)
    else:
        shutil.copyfile(filename, os.path.join(destdir, 'a.wav'))
        subprocess.check_call(['ffmpeg', '-i', 'a.wav', '-acodec', 'flac', 'a.ogg'], cwd=destdir,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.rename(os.path.join(destdir, 'a.ogg'), destfilename)
        os.remove(os.path.join(destdir, 'a.wav'))

def CompressFolder(src, dst):
    zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()
