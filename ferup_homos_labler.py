#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os
import re
import codecs
"""
Program: ferup_homos_labeler.py
Function: modify auto file
Author: Junjie Pan (junjie.pan@nuance.com)
"""

class HmogrpyAuto(object):
  '''
  Modify auto file, insert polyphone LHP
  '''
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    self.words = set([])
    self.lhp = ""
    if not os.path.exists(options['outdir']):
      os.mkdir(options['outdir'])
    os.system("chcp 65001")
   
  def loadDct(self, char):
    lhps = set([])
    with codecs.open(self.options['dct'], 'r', 'utf-8') as dctf:
      for line in dctf:
        word = line.strip().split('|')[0]
        if word == char:
          lhps.add(line.strip().split('|')[3])
        self.words.add(word)
      lhps = ",".join(list(lhps))
      lhps = re.sub("\{","[",lhps)
      lhps = re.sub("\}","]",lhps)
    self.lhp="{%s}"%(lhps)

  def hex2char(self, _hex):
    char = chr(int("0x"+_hex, 16))
    self.logger.info("Process: %s"%char)
    return char
    
  def process(self):
    fs = list(filter(lambda x: x[-4:] == "auto", os.listdir(self.options['auto'])))
    pattern = re.compile('[\,\.\;\:\<\>\?\!\'\"\%\(\)\[\]\{\}\-\_\=\+]')
    for f in fs:
      fn = os.path.join(self.options['auto'], f)
      char = self.hex2char(os.path.basename(fn)[:-5])
      self.loadDct(char)
      fo = codecs.open(os.path.join(self.options['outdir'], os.path.basename(fn)),'w','utf-8')
      with codecs.open(fn, 'r', 'utf-8') as fn:
        for line in fn:
          if "AUTO-Lexi" in line:
            line = line.strip().split()
            line = list(map(lambda x: x.split("/"), line))
            pos = list(map(lambda x: x[1], line))
            words = list(map(lambda x: x[0], line))
            head = words[0].split(':')[0]
            words[0] = words[0].split(':')[1]
            for ind, word in enumerate(words):
              clean_word = re.sub(pattern,'',word)
              if char in clean_word and (len(clean_word) == 1 or clean_word not in list(self.words)):
                tmp = []
                for i in word:
                  if i == char:
                    tmp.append("%s%s"%(i, self.lhp))
                  else:
                    tmp.append(i)
                words[ind] = ''.join(tmp)
            fo.write("%s:"%head)
            for w,p in zip(words, pos):
              fo.write("%s/%s  "%(w,p))
            fo.write("\n")
          else:
            fo.write(line)
            
  
if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup_homos_labeler')
  parser.add_argument("--version", action="version", version="ferup_homos_labeler 1.0")
  parser.add_argument(type=str, action="store", dest="auto", default="", help='input auto file')
  parser.add_argument("-o", "--out", action="store", dest="outdir", default="new_auto_file", help='input auto file')
  parser.add_argument("-d", "--dict", action="store", dest="dct", default=r"D:\repos\clc\clc_shanghai\lingware-data\dct\shx\dct.u08", help='dictionary.')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup_homos_labeler.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = HmogrpyAuto(options, logger)
  appInst.process()
  # appInst.formatCheck()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))
