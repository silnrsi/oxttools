
import codecs
import unicodedata

class Hunspell(object) :

    def __init__(self, name) :
        self.name = name
        self.words = []
        self.affix = ""

    def addword(self, word) :
        if len(word) :
            dat = unicodedata.normalize('NFC', word) 
            self.words.append(dat)

    def mergeaffix(self, fname) :
        if fname is not None :
            with open(fname) as fd :
                self.affix = "\n".join(fd.readlines())

    def getaff(self) :
        return """
SET UTF-8
""" + self.affix

    def getdic(self) :
        res = "{}\n".format(len(self.words))
        res += "\n".join(sorted(self.words))
        return res

