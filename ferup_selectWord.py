#-*-coding:utf-8-*-
#!\usr\bin\env py3

import os
import sys
import re
import codecs
import multiprocessing



class SelectWord(object):
  '''
  select unseen word from corpus according to a given dictionary
  '''
  
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    self.wlist = set([])
    self.dict = self.wordlist(self.options['dict'])
    self.base = self.options['corpus']
    self.fs = os.listdir(self.base)  
    self.puncs = self.loadPuncs(options['punc'])
    self.outfile = options['outfile']
    print('initialization finished.')
    
  def loadPuncs(self, puncf):
    try:
      with codecs.open(puncf, 'r', 'utf-8') as punch:
        punc = set([])
        for line in punch:
          punc.add(line.strip().split()[0])
      punc = list(punc)
      rp = list(map(lambda x: '\\'+x, punc))
      rp = '[' + ''.join(rp) + ']'
      return re.compile(rp)
    except Exception as e:
      self.logger.error(e)
    
  def wordlist(self, dic):
    try:    
      with codecs.open(dic, 'r', 'utf-8') as fd:
        for line in fd:
          f = line.strip().split(r'|')[0]
          self.wlist.add(f)         
    except Exception as e:
      self.logger.error(e)
  
  def writeFile(self, nwords):
    try:
      with codecs.open(self.outfile, 'w', 'utf-8') as fo:
        for w in nwords:
          fo.write('%s\n'%w)
    except Exception as e:
      self.logger.error(e)
    
  def process(self):
    procP = multiprocessing.Pool()
    result_list = set([])
    for f in self.fs:
      f = os.path.join(self.base, f)
      result_list = result_list.union(procP.apply_async(SelectWord.subProcess, args=(f, self.puncs, self.wlist)).get())
   
    procP.close()
    procP.join()
    print(result_list)
    with codecs.open(self.outfile, 'w', 'utf-8') as fo:
      for w in list(result_list):
        print("Find word: %s"%w)
        fo.write("%s\n"%w)


  @classmethod
  def subProcess(cls, f, puncs, wlist):
    print('Processing:%s'%f)
    with codecs.open(f, 'r', 'utf-8') as fn:
      nwlist = set([])
      for line in fn:
        line = re.sub(puncs, ' ',line)
        line = line.strip().split()
        for w in line:
          if re.search('[a-za-z0-9]', w) is None and w not in wlist:
            nwlist.add(w)
    return nwlist
  
  
if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='selectWord')
  parser.add_argument("--version", action="version", version="selectWord 1.0")
  parser.add_argument(action="store", dest="corpus", default="", help='input corpus direcotry')
  parser.add_argument(action="store", dest="outfile", default="newword.wlist", help='new word list')
  parser.add_argument("-d", "--dict", action="store", dest="dict", default="", help='dictionary')
  parser.add_argument("-p", "--punc", action="store", dest="punc", default="puncs.list", help='punctuation lists')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-selectWord.txt', 'w')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = SelectWord(options, logger)
  appInst.process()
  allEndTP = time.time()