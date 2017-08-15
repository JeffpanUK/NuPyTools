#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: ferup_corpus_formatter
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-08-15 10:12:35
 ============================
'''

class genWS(object):
  """docstring for genWS"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    if not os.path.exists(self.options['output']):
      os.mkdir(self.options['output'])


  def process(self):
    fs = os.listdir(self.options['corpus'])
    sentence_count = {}
    for f in fs:
      scount = 0
      wcount = 0
      fn = os.path.join(self.options['corpus'], f)
      fon = os.path.join(self.options['output'], f)
      self.logger.info("Process: %s"%f)
      with open(fn, 'r', encoding="utf-8") as fi, open(fon, 'w', encoding='utf-8') as fo:       
        fo.write("#!repeat:5 ratio:1.0\n#example of handcrafted corpus\n#first line is mode line\n#repeat:4 means all sentences in this file would be repated 4 times after split(split of train & test)\n#ratio:0.9 means 90\% data would be chosen as training, remain part is testing.\n#every line starts with # would be ignored. and #! would be transperted as modeline\n#every line starts with ! would be chosed in both training & testing") 
        for line in fi:
          scount += 1
          wcount += len(line.split())
          fo.write("!%s"%line)
        sentence_count[f] = (scount, wcount)
    with open(self.options['log'], 'w', encoding='utf-8') as flog:
      self.logger.info("Genrating Sentences Statistics...")
      snum = sum(list(map(lambda x: x[0], sentence_count.values())))
      wnum = sum(list(map(lambda x: x[1], sentence_count.values())))
      flog.write("==========================\nTotal Sentences: %d\n"%(snum))
      flog.write("Total Lexical Words: %d\n==========================\n"%(wnum))
      sentence_count = sorted(sentence_count.items(), key = lambda x: x[1][0], reverse=True) 
      for item in sentence_count:
        align_space = int("%d"%(40-len(item[0])))
        flog.write("%s:%s(%s)\n"%(item[0], str(item[1][0]).rjust(align_space), item[1][1]))


if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup_corpus_formatter')
  parser.add_argument("--version", action="version", version="ferup_corpus_formatter 1.0")
  parser.add_argument(type=str, action="store", dest="corpus", default="", help='input raw data')
  parser.add_argument("-o", "--output", action="store", dest="output", default="", help='output files')
  parser.add_argument("-l", "--log", action="store", dest="log", default="ws.sts", help='output files')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup_corpus_formatter.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = genWS(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))

