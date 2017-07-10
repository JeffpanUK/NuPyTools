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
    os.system('chcp 65001')
    
  def loadDct(self):
    words = {}
    rwords = {}
    with codecs.open(self.options['dct'], 'r', 'utf-8') as dctf:
      for line in dctf:
        line = line.strip().split('|')
        w = line[0]
        lhp = line[3]
        priority = line[16]
        if len(w) == 1 and priority !="" and re.search('[a-zA-Z0-9]', w) is None:
          if w not in words.keys():
            words[w] = [1, priority, lhp]
          elif w in words and int(priority) < int(words[w][1]):
            words[w] = [1, priority, lhp]
          elif w in words and lhp!=words[w][2] and int(priority) == int(words[w][1]):
            words[w][0] += 1
            words[w].append(lhp)
    for item in words.items():
      if item[1][0] > 1:
        print(item)
        rwords[item[0]] = item[1][2:]
    return rwords
        
  def loadList(self):
    lists = []
    with codecs.open(self.options['wlist'], 'r', 'utf-8') as listf:
      for line in listf:
        w = line.strip().split()[0]
        lists.append(w)
    return lists
  
  
  def process(self):
    dct = self.loadDct()
    print(dct)
    wlist = dct.keys()
    word = self.loadList()
    print(word)
    input(" ")
    badw = set(wlist) - set(word)
    with codecs.open(self.options['outfile'],'w','utf-8') as fo:
      for w in list(badw):
        fo.write("%s: %s\n"%(w,', '.join(dct[w])))
        print(w)
  
    
  

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
  file_handler = logging.FileHandler('LOG-ferup_homos.txt', 'w')
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
