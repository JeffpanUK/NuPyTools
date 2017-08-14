import os
import time
import re
import codecs
from lxml import etree

class LDBReader(object):

    def __init__(self,logger,puncs):
        self.logger = logger
        self.puncs = puncs

    def processBlk(self,blk):
        newBlk=[]
        for line in blk:
            if "".join(line[:14]) == '<LD_SE_SYNTAX>':
                #this block will crash lxml parsing, and no use in evaluation, so we ignore it
                pass
            else:
                newBlk.append(line)
        xml = "\n".join(newBlk)
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml,parser=parser)


        phrases = []
        words = []
        spts = []
        phrase=[]
        for w in root.iterfind('WordRecord'):
            isPhrase = False
            isWord = False
            for t in w:
                if t.tag == 'LD_W_ORTH':
                    try:
                        text =  t.text.strip()
                    except:
                        text = " "
                    text = re.sub(u"\u263ccomma\u263c","",text)
                    text = re.sub("[ \\-]","",text)
                    if len(text) > 0:
                        newtext = []
                        for c in text:
                            if c not in self.puncs:
                                newtext.append(c)
                        text = "".join(newtext)

                elif t.tag == 'LD_W_TYPE':
                    wtype = t.text.strip()
                    if wtype == 'WORD_PHRASE':
                        isPhrase = True
                        break
                    elif wtype == 'WORD_DCT' or wtype == 'WORD_CROSSTOKEN':
                        isWord = True
                        word = text
                        phrase.append(word)

                elif t.tag == 'LD_W_PHON':
                    spt = t.text.strip()

            if isPhrase:
                if len(phrase) != 0:
                    phrases.append("".join(phrase))
                    phrase =[]
            elif isWord:
                if word != "":
                    words.append(word)
                    sptA = re.split("-",spt)
                    spts.extend(sptA)
        if len(phrase) != 0:
            phrases.append("".join(phrase))
            phrase =[]

        #print "WORD  :%s" % ("  ".join(words))
        #print "PHRASE:%s" % ("  ".join(phrases))
        #print "SPT   :%s" % ("-".join(spts))
        return (phrases, words, spts)

    def processLDBFile(self,ldbFile):
        f = open(ldbFile,'r')
        blk=f.readlines()
        f.close()
        sent = self.processBlk(blk)
        return sent

    def process(self,folder):
        if not os.path.isdir(folder):
            self.logger.error("LDB Folder:%s is invalid" % folder)
            return
        else:
            self.logger.info("Processing LDB Folder:%s" % folder)

        flist = os.listdir(folder)

        #filter all ldb files
        ldblist = []
        for fn in flist:
            fnA = re.split("\\.",fn)
            if fnA[-1] != 'ldb':
                continue
            else:
                ldblist.append(os.path.join(folder,fn))

        #sort files by suffix in file name
        ldblist = sorted(ldblist,key=lambda fn:int(re.split("[._]",fn)[-2]))

        sents = []
        count = 0
        total = len(ldblist)
        for fn in ldblist:
            count+=1
            self.logger.debug("File:%s, Status:%0.2f(%d/%d)" % (fn,float(count)/total,count,total))
            sent = self.processLDBFile(fn)
            sents.append(sent)
        return sents

    def processRootFolder(self, folder):
        if not os.path.isdir(folder):
            self.logger.error("ROOT Folder:%s is invalid" % folder)
            return
        else:
            self.logger.info("Processing ROOT Folder:%s, Only files in sub folders will be processed" % folder)

        flist = os.listdir(folder)

        subs = []
        for f in flist:
            if not os.path.isdir(os.path.join(folder, f)):
                continue
            subs.append(os.path.join(folder, f))

        allSents = []
        for sfolder in subs:
            sents = self.process(sfolder)
            allSents.extend(sents)

        self.logger.info("Total sents:%d" % len(allSents))
        return allSents
