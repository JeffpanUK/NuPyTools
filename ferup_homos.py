#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os
import re
import codecs
"""
Program: ferup_homos.py
Function: find all homographs in dictionary, and compare with existing lists
Author: Junjie Pan (junjie.pan@nuance.com)
"""

class FilterHomos(object):
  '''
  filter homographs
  '''
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    self.dictline = []
    os.system('chcp 65001')
    
  def loadDct(self):
    words = {}
    rwords = {}
    igs = {}
    count = 0
    with codecs.open(self.options['dct'], 'r', 'utf-8') as dctf:
      for line in dctf:
        line = line.strip().split('|')
        self.dictline.append(line)
        w = line[0]
        lhp = line[3]
        priority = line[16]
        if len(w) == 1 and priority !="" and re.search('[a-zA-Z0-9]', w) is None:
          if w not in words.keys():
            words[w] = [1, priority, lhp]
          elif w in words.keys() and int(priority) < int(words[w][1]):
            words[w] = [1, priority, lhp]
          elif w in words.keys() and lhp!=words[w][2] and int(priority) == int(words[w][1]):
            words[w][0] += 1
            words[w].append(lhp)
            
        if len(w) == 1 and priority != "" and self.isChinese(w):
          if w not in igs.keys():
            igs[w] = [1, priority, lhp, count]
          elif w in igs.keys() and int(priority) < int(igs[w][1]):
            igs[w][0] += 1
            igs[w][1] = priority
            igs[w][2] = lhp
          elif w in igs.keys() and int(priority) == int(igs[w][1]) and lhp != igs[w][2]:
            del igs[w]
          else:
            igs[w][0] +=1
        count += 1
            
            
    for item in words.items():
      if item[1][0] > 1:
        rwords[item[0]] = item[1][2:]

    return rwords, igs
        
  def loadList(self):
    lists = []
    with codecs.open(self.options['wlist'], 'r', 'utf-8') as listf:
      for line in listf:
        w = line.strip().split()[0]
        lists.append(w)
    return lists
  
  def genIGTR(self, igs):
    # prefix = "{\n\tstring pinyin;\n\tstring lchar;\n\tstring lpos;\n\tstring rchar;\n\tstring rword;\n\tstring rrword;\n\tstring rpos;\n}\n%% forcing_rules\n"
    prefix = "{\n\tstring lhplus;\n\tstring char0;\n}\n%% forcing_rules\n"
    # suffix = "%% data\nNOMATCH\t=\t=\t=\t=\t=\t=\n"
    suffix = "%% data\nNOMATCH\t=\n"
    if not os.path.exists("igs"):
      os.mkdir("igs")
    for ig in igs.items():
      if not self.isChinese(ig[0]) or ig[1][0] == 1:
        continue
      self.logger.info("Generate IGTR: %s"%ig[0])
      self.dictline[ig[1][3]][16] = 4
      fn = hex(ord(ig[0]))[2:].upper()
      fn = os.path.join('igs', fn+".txt")
      # if os.path.exists(fn):
        # continue
      with codecs.open(fn, 'w', 'utf-8') as fo:
        fo.write(prefix)
        # fo.write("%s\t*\t*\t*\t*\t*\t*\n"%ig[1][2])
        fo.write("%s\t%s\n"%(ig[1][2], ig[0]))
        fo.write(suffix)
    with codecs.open("dct0711.u08", 'w', 'utf-8') as fo:
      for rd in self.dictline:
        rd = list(map(lambda x:  str(x), rd))
        fo.write("%s\n"%"|".join(rd))
    with codecs.open("list_igtree.txt","w","utf-8") as iglist:
      for ig in igs.keys():
        if not self.isChinese(ig) or igs[ig][0] == 1:
          continue
        orth = ig
        hexo = hex(ord(orth))[2:].upper()
        lhp = igs[ig][2]
        iglist.write("%s\t%s\t%s\n"%(hexo, orth, lhp))
  
  def process(self):
    dct, igs = self.loadDct()
    wlist = dct.keys()
    word = self.loadList()
    badw = set(wlist) - set(word)
    with codecs.open(self.options['outfile'],'w','utf-8') as fo:
      for w in list(badw):
        fo.write("%s: %s\n"%(w,', '.join(dct[w])))
        self.logger.info("unsolved word: %s" % w)
    self.genIGTR(igs)
  
  def isChinese(self, ch):
    hexCH = ord(ch)
    if (hexCH >= 0x3100  and hexCH <= 0x312F) \
      or (hexCH >= 0x3400  and hexCH <= 0x4BDF) \
      or (hexCH >= 0x4e00  and hexCH <= 0x9fff) \
      or (hexCH >= 0xF900  and hexCH <= 0xFA2D) \
      or (hexCH >= 0x20000 and hexCH <= 0x2a6d6)  \
      or (hexCH >= 0x2A700 and hexCH <= 0x2CEAF)  \
      or (hexCH >= 0x2F800 and hexCH <= 0x2FA1D):
      return True
    else:
      return False
  
    
  

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup_homos')
  parser.add_argument("--version", action="version", version="ferup_homos 1.0")
  parser.add_argument(action="store", dest="wlist", default="", help='current homograph lists')
  parser.add_argument(action="store", dest="outfile", default="badword.wlist", help='bad word list')
  parser.add_argument("-d", "--dict", action="store", dest="dct", default="", help='dictionary')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup_homos.txt', 'w', 'utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = FilterHomos(options, logger)
  appInst.process()
  allEndTP = time.time()
