from dataclasses import dataclass, field
from typing import Optional, List
from bmsutil import *
import re


@dataclass
class BMSData:
    raw: bytes = b''
    md5: str = 'd41d8cd98f00b204e9800998ecf8427e'
    encoding: str = 'ascii'
    value: str = ''
    title: Optional[str] = None
    subtitle: Optional[str] = None
    artist: Optional[str] = None
    subartist: Optional[str] = None
    genre: Optional[str] = None
    player: Optional[str] = None
    playlevel: Optional[int] = None
    stagefile: Optional[str] = None
    banner: Optional[str] = None
    wav: List[str] = field(default_factory=lambda: [])
    bmp: List[str] = field(default_factory=lambda: [])


def BMSData2JSON(dat):
    ret = {}
    ret['md5'] = dat.md5
    ret['encoding'] = dat.encoding
    ret['title'] = dat.title
    ret['subtitle'] = dat.subtitle
    ret['artist'] = dat.artist
    ret['subartist'] = dat.subartist
    ret['wav'] = dat.wav
    ret['bmp'] = dat.bmp
    return ret


class UnknownEncodingError(Exception):
    """Encoding of BMS file is not known"""
    pass


def AutoDecode(raw):
    EncodingList = ['ascii', 'cp932', 'shift_jisx0213', 'utf-8', 'cp949']
    for e in EncodingList:
        try:
            return (e, raw.decode(e))
        except UnicodeDecodeError:
            pass

    raise UnknownEncodingError


def parse(h):
    def parseWithHeader(f):
        def newfunc(dat, line):
            m = re.match(h, line, flags=re.IGNORECASE)
            if m is None:
                return False
            body = line[len(m[0]):]
            f(dat, body, *m.groups())
            return True
        return newfunc
    return parseWithHeader


@parse('#TITLE\\s')
def parseTitle(dat, body):
    dat.title = body.strip()


@parse('#SUBTITLE\\s')
def parseSubtitle(dat, body):
    dat.subtitle = body.strip()


@parse('#ARTIST\\s')
def parseArtist(dat, body):
    dat.artist = body.strip()


@parse('#SUBARTIST\\s')
def parseSubartist(dat, body):
    dat.subartist = body.strip()


@parse('#GENRE\\s')
def parseGenre(dat, body):
    dat.genre = body.strip()


@parse('#PLAYER\\s')
def parsePlayer(dat, body):
    body = body.strip()
    if body == '1':
        dat.player = 'SP'
    elif body in ['2', '3', '4']:
        dat.player = 'DP'
    else:
        dat.player = 'SP'

    return True


@parse('#PLAYLEVEL\\s')
def parsePlaylevel(dat, body):
    try:
        dat.playlevel = int(body.strip())
    except ValueError:
        dat.palylevel = None

    return True


@parse('#STAGEFILE\\s')
def parseStagefile(dat, body):
    dat.stagefile = body.strip()


@parse('#BANNER\\s')
def parseBanner(dat, body):
    dat.banner = body.strip()


@parse('#BACKBMP\\s')
def parseBackbmp(dat, body):
    dat.bmp.append(body.strip())


@parse('#BMP([0-9A-Z]{2})\\s')
def parseBmp(dat, body, code):
    dat.bmp.append(body.strip())


@parse('#WAV([0-9A-Z]{2})\\s')
def parseWav(dat, body, code):
    dat.wav.append(body.strip())


def ParseLine(dat, line):
    parserList = [parseArtist, parseBackbmp, parseBanner, parseBmp, parseGenre, parsePlayer,
                  parsePlaylevel, parseStagefile, parseSubartist, parseSubtitle, parseTitle, parseWav]

    for f in parserList:
        if f(dat, line):
            return True

    return False


def SplitImplicitSubtitle(title):
    if title == '':
        return ('', None)
    sublist = ['--', '～～', '()', '[]', '<>', '""']

    for s, e in sublist:
        if title[-1] == e:
            ind = title[:-1].rfind(s)
            if ind == -1:
                return (title, None)
            else:
                return (title[:ind].strip(), title[ind:].strip())

    return (title, None)


def AfterParse(dat):
    if dat.subtitle is None:
        dat.title, dat.subtitle = SplitImplicitSubtitle(dat.title)
        if dat.title == '':
            dat.title = dat.subtitle
            dat.subtitle = None

    dat.wav = sorted(set(dat.wav))
    dat.bmp = sorted(set(dat.bmp))


def ParseBMSFile(dat):
    for line in re.split('\r\n|\n|\r', dat.value):
        # Indentation support
        line = line.lstrip()

        # value starts with #
        if not line.startswith('#'):
            continue

        ParseLine(dat, line)

    AfterParse(dat)


def LoadBMSFile(fileName):
    assert IsBMSFile(fileName), "Given file is not a bms file"
    dat = BMSData()
    dat.raw = open(fileName, 'rb').read()
    dat.md5 = MD5(fileName)
    dat.encoding, dat.value = AutoDecode(dat.raw)

    ParseBMSFile(dat)

    return dat
