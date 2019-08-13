import re


from bmsutil import *


class BMS:
    class UnknownEncodingError(Exception):
        """Encoding of BMS file is not known"""
        pass

    @classmethod
    def AutoDecode(cls, raw):
        EncodingList = ['shift-jis', 'utf-8', 'cp949']
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

        # We apply every possible parser, run while one of them returns true.
        parserList = [ParseTitle, ParseArtist]
        for f in parserList:
            if f(line):
                return True
        return False

    def __parseBMSFile(self):

        self.__title = 'N/A'
        self.__artist = 'N/A'

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
