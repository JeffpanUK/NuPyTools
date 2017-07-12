#-*-coding:utf-8-*-
#!\usr\bin\env py3

import os
import sys
import re
import codecs

class FileInfo(object):
  '''
  statistics of corpus
  '''
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    self.task = options['task']
    self.punc = self.loadPuncs(options['punc'])
    
  def loadPuncs(self, puncf):
    try:
      with codecs.open(puncf, 'r', 'utf-8') as punch:
        punc = set([])
        for line in punch:
          punc.add(line.strip().split()[0])
      punc = list(punc)
      #rp = list(map(lambda x: '\\'+x, punc))
      #rp = '[' + ''.join(rp) + ']'
      rp = "[%s]"%(re.escape("".join(punc)))
      return re.compile(rp)
    except Exception as e:
      self.logger.error(e)
      
  def wordseg(self):
    baseDir = self.options['InDir']
    fs = os.listdir(baseDir)
    wordRec = set([])
    wordNo = 0
    puncNo = 0
    lineNo = 0
    
    for f in fs:
      tpuncNo = 0
      twordNo = 0
      tlineNo = 0
      tlexc = set([])
      with codecs.open(os.path.join(baseDir, f), 'r', 'utf-8') as fn:
        self.logger.info("Processing: %s"%f)
        for line in fn:
          tlineNo += 1
          line = line.strip()
          tpuncNo += len(re.findall(self.punc, line))       
          words = re.sub(self.punc, ' ',line)
          words = words.split()
          twordNo += len(words)
          tlexc = tlexc.union(set(words))
      puncNo += tpuncNo
      wordNo += twordNo
      lineNo += tlineNo
      wordRec = wordRec.union(tlexc)
      self.logger.info("Line - %d, Words - %d, Lexical - %d, Punctuation - %d"\
                      %(tlineNo, twordNo, len(set(tlexc)), tpuncNo))
  
    self.logger.info("Total Counts")
    self.logger.info("Line - %d, Words - %d, Lexical - %d, Punctuation - %d"\
                      %(lineNo, wordNo, len(wordRec), puncNo))
    self.logger.info("Average words per line: %.2f"%(wordNo/lineNo))
    
    
  def process(self):
    if self.task == 'ws':
      self.wordseg()
    else:
      self.logger.warn("Not Supported Task Type %s." % (self.task))
  
if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup-fileinfo')
  parser.add_argument("--version", action="version", version="ferup-fileinfo 1.0")
  parser.add_argument(type=str, action="store", dest="InDir", default="", help='input raw data directory')
  parser.add_argument("-t", "--task", action="store", dest="task", default="ws", help='pw - prosody word; ws - word segmentation')
  parser.add_argument("-p", "--punc", action="store", dest="punc", type=str, default=r"puncs.list", help='punctuation list file')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup-fileinfo.txt', 'w')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = FileInfo(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))