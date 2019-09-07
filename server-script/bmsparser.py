import re


from bmsutil import *


class BMS:
    class UnknownEncodingError(Exception):
        """Encoding of BMS file is not known"""
        pass

    @classmethod
    def AutoDecode(cls, raw):
        EncodingList = [
            'shift-jis',
            'cp932',
            'shift_jisx0213',
            'utf-8',
            'cp949']
        for e in EncodingList:
            try:
                ret = raw.decode(e)
                return ret
            except UnicodeDecodeError:
                pass

        raise BMS.UnknownEncodingError

    def __applyData(self, line):

        def ParseTitle(line):
            if not line.upper().startswith('#TITLE'):
                return False

            # Trim header.
            line = line[6:]

            # Do not allow only #TITLE.
            if len(line) == 0:
                return False

            # Tag should be space-separated.
            if not line[0].isspace():
                return False

            # Title is trimmed.
            # We see line by line, and last occurrence is real title.
            self.__title = line.strip()

            return True

        def ParseArtist(line):
            if not line.upper().startswith('#ARTIST'):
                return False

            # Trim header.
            line = line[7:]

            # Do not allow only #ARTIST
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # Artist is trimmed.
            # We see line by line, and last occurence is real artist.
            self.__artist = line.strip()

            return True

        def ParsePlayer(line):
            if not line.upper().startswith('#PLAYER'):
                return False

            # Trim header.
            line = line[7:]

            # Do not allow only #PLAYER
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # Player should be "1" (SP), "2", "3" or "4" (DP)
            rawPlayer = line[0].strip()

            if rawPlayer == '1':
                self.__player = 'SP'
            elif rawPlayer in ['2', '3', '4']:
                self.__player = 'DP'
            else:
                self.__player = None

            return True

        def ParseRank(line):
            if not line.upper().startswith('#RANK'):
                return False

            # Trim header.
            line = line[5:]

            # Do not allow only #RANK
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # Rank should be "0" (VERY HARD), "1" (HARD), "2" (NORMAL), or "3" (EASY)
            rawRank = line[0].strip()

            if rawRank == '0':
                self.__rank = 'VERY HARD'
            elif rawRank == '1':
                self.__rank = 'HARD'
            elif rawRank == '2':
                self.__rank = 'NORMAL'
            elif rawRank == '3':
                self.__rank = 'EASY'
            else:
                self.__rank = None

            return True

        def ParseTotal(line):
            if not line.upper().startswith('#TOTAL'):
                return False

            # Trim header.
            line = line[6:]

            # Do not allow only #TOTAL
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # Total should be represented as float
            rawTotal = line[0].strip()

            try:
                self.__total = float(rawTotal)
            except ValueError:
                self.__total = None

            return True

        def ParseStageFile(line):
            if not line.upper().startswith('#STAGEFILE'):
                return False

            # Trim header.
            line = line[10:]

            # Do not allow only #STAGEFILE
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # front stagefile (holds as set since #RANDOM support)
            self.__image.add(line.strip())

            return True

        def ParseBanner(line):
            if not line.upper().startswith('#BANNER'):
                return False

            # Trim header.
            line = line[7:]

            # Do not allow only #BANNER
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # front banner (holds as set since #RANDOM support)
            self.__image.add(line.strip())

            return True

        def ParseBackBMP(line):
            if not line.upper().startswith('#BACKBMP'):
                return False

            # Trim header.
            line = line[8:]

            # Do not allow only #BACKBMP
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # backbmp consider as bga (holds as set since #RANDOM support)
            self.__bga.add(line.strip())

            return True

        def ParsePlayLevel(line):
            if not line.upper().startswith('#PLAYLEVEL'):
                return False

            # Trim header.
            line = line[10:]

            # Do not allow only #TOTAL
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # PLAYLEVEL should be represented as int
            rawPlayLevel = line[0].strip()

            try:
                self.__playlevel = int(rawPlayLevel)
            except ValueError:
                self.__playlevel = None

            return True

        def ParseDifficulty(line):
            if not line.upper().startswith('#DIFFICULTY'):
                return False

            # Trim header.
            line = line[11:]

            # Do not allow only #RANK
            if len(line) == 0:
                return False

            # Tag should be space-separated
            if not line[0].isspace():
                return False

            # Rank should be "1" (BEGINNER), "2" (NORMAL), "3" (HYPER), "4" (ANOTHER), or "5" (INSANE)
            rawDifficulty = line[0].strip()

            if rawDifficulty == '1':
                self.__difficulty = 'BEGINNER'
            elif rawDifficulty == '2':
                self.__difficulty = 'NORMAL'
            elif rawDifficulty == '3':
                self.__difficulty = 'HYPER'
            elif rawDifficulty == '4':
                self.__difficulty = 'ANOTHER'
            elif rawDifficulty == '5':
                self.__difficulty = 'INSANE'
            else:
                self.__difficulty = None

            return True

        # We apply every possible parser, run while one of them returns true.
        parserList = [ParseTitle, ParseArtist, ParsePlayer, ParseRank,
                      ParseTotal, ParseStageFile, ParseBanner, ParseBackBMP, ParsePlayLevel, ParseDifficulty]
        for f in parserList:
            if f(line):
                return True
        return False

    def __parseBMSFile(self):

        self.__title = None
        self.__artist = None
        self.__player = 'SP'
        self.__rank = None
        self.__playlevel = None
        self.__total = None
        self.__difficulty = None
        self.__image = set()
        self.__bga = set()
        self.__wav = set()

        for line in re.split('\r\n|\n|\r', self.__value):
            # BMS parser should support indentation
            line = line.lstrip()

            # Line without '#' character is not supported.
            if line == '' or line[0] != '#':
                continue

            # Apply bms parsing
            self.__applyData(line)

    def __init__(self, fileName):

        assert IsBMSFile(fileName), "Given file is not a bms file."

        self.__md5 = MD5(fileName)
        self.__raw = open(fileName, "rb").read()
        self.__value = BMS.AutoDecode(self.__raw)

        self.__parseBMSFile()

    def getTitle(self):
        return self.__title

    def getMD5(self):
        return self.__md5

    def getArtist(self):
        return self.__artist
