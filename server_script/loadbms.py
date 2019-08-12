import os
import sys
import traceback
import zipfile
import re
import hashlib
import json


code2hash = {}
hash2code = {}


def md5(fname):
    """Calculate MD5 value of given file"""
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def isBMSFile(fname):
    """Check whether given file is BMS file, based on file name"""
    name, ext = os.path.splitext(fname)
    return ext in ['.bms', '.bme', '.bml', '.pms']


def LoadFiles():
    """Load previously stored ZIP and BMS hash pair map"""
    global code2hash, hash2code
    try:
        with open('ZIP2BMS.json', 'r') as f:
            code2hash = json.load(f)
    except:
        pass
    try:
        with open('BMS2ZIP.json', 'r') as f:
            hash2code = json.load(f)
    except:
        pass


def MatchBMS(code, md5v):
    """Store ZIP and BMS hash pair"""
    md5v = 'BMS_' + md5v
    if code not in code2hash:
        code2hash[code] = []
    if md5v not in hash2code:
        hash2code[md5v] = []
    code2hash[code].append(md5v)
    hash2code[md5v].append(code)


def DumpFiles():
    """Save current ZIP and BMS hash pair map"""
    f = open('ZIP2BMS.json', 'w')
    for k in code2hash:
        code2hash[k] = sorted(code2hash[k])
    f.write(json.dumps(code2hash, indent=4, sort_keys=True))
    f.write('\n')
    f.close()
    f = open('BMS2ZIP.json', 'w')
    for k in hash2code:
        hash2code[k] = sorted(hash2code[k])
    f.write(json.dumps(hash2code, indent=4, sort_keys=True))
    f.write('\n')
    f.close()


def ChangeName(code):
    """Change name of zip file to hash"""
    fname = os.path.join('./zip', code+'.zip')
    md5v = 'ZIP_'+md5(fname)
    os.rename(fname, os.path.join('./zip', md5v+'.zip'))
    return md5v


def ExtractBMSData(code):
    """Extract and find whole bms files in zip"""
    assert re.match('^ZIP_[0-9a-f]{32}$', code)
    with zipfile.ZipFile(os.path.join('./zip', code+'.zip'), 'r') as zip_ref:
        zip_ref.extractall(os.path.join('./extract', code))

    ebms = False

    for i in sorted(os.listdir(os.path.join('./extract', code)))[::-1]:
        fname = os.path.join(os.path.join('./extract', code), i)
        if isBMSFile(fname):
            MatchBMS(code, md5(fname))
            ebms = True

    if not ebms:
        sys.stderr.write('Bms file does not exists for '+fname+'\n')


def main():
    """Main Logic"""
    LoadFiles()
    for i in os.listdir('./zip'):
        name, ext = os.path.splitext(i)
        if ext != ".zip":
            continue
        if not re.match('^[0-9a-f]{16}$', name):
            continue

        try:
            name = ChangeName(name)
            ExtractBMSData(name)
        except Exception:
            sys.stderr.write('Error on: '+name+'!\n')
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write('\n')

    DumpFiles()

if __name__ == '__main__':
    main()
