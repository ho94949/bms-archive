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

def allEqual(ls):
    for v in ls:
        if v != ls[0]:
            return None

    return ls[0] 

def allPrefix(ls):
    ll = min(ls,key=len)

    for v in ls:
        if not v.startswith(ll):
            return None

    return ll

def allImplicitSubtitle(ls):
    nls = list(map(RemoveImplicitSubtitle, ls))

    return allEqual(nls)

def prefixImplicitDifficulty(ls):
    from os.path import commonprefix

    CP = commonprefix(ls).strip()
    if CP == '': return 

    difficultyList = ['Basic', 'Normal', 'Hyper', 'Another']
    difficultyCnt = 0

    for v in ls:
        difficultyName = v[len(CP):].strip()
        if difficultyName in difficultyList:
            difficultyCnt += 1

        if difficultyCnt > 1:
            return CP

    return None

def removeStrangeSabunName(titleList, artistList):
    titleArtistList = zip(titleList, artistList)
    isNotSabun = lambda s: ('OBJ' not in s[1].upper() and s != '')
    
    titleArtistList = list(zip(*filter(isNotSabun, titleArtistList)))
    if len(titleArtistList) == 0: return [[],[]]
    return titleArtistList


def GuessTitle(titleList, artistList):
    if len(titleList) == 0: 
        return "No bms files"

    guessFunc = [allEqual, allPrefix, allImplicitSubtitle, prefixImplicitDifficulty]
    
    for f in guessFunc:
        res = f(titleList)
        if res is not None:
            return res
    
    titleList, artistList = removeStrangeSabunName(titleList, artistList)
    
    if len(titleList) == 0:
        return None

    for f in guessFunc:
        res = f(titleList)
        if res is not None:
            return res

    return None

def GuessArtist(artistList, titleList):
    if len(artistList) == 0:
        return "No bms files"

    guessFunc = [allEqual, allPrefix]

    for f in guessFunc:
        res = f(artistList)
        if res is not None:
            return res

    titleList, artistList = removeStrangeSabunName(titleList, artistList)

    if len(artistList) == 0:
        return None

    for f in guessFunc:
        res = f(artistList)
        if res is not None:
            return res
    
    return None

def GuessTitleArtist(bms):
    titleList = list(map(lambda s:s['title'], bms))
    artistList = list(map(lambda s:s['artist'], bms))

    
    return ( GuessTitle(titleList, artistList), GuessArtist(artistList, titleList))

if __name__ == '__main__':
    import json

    bms = json.loads(open('ZIP2BMS.json').read())
    cnt1, cnt2 = 0,0
    for f in bms:
        v1, v2 = GuessTitleArtist(bms[f]['bms'])
        cnt2 += 1
        if v1 is None or v2 is None:
            print(v1, v2)
            print(f)
            cnt1 += 1 

    print(cnt1,'/',cnt2)