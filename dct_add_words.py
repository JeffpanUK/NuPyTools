#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: dct_add_words.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-08-28 10:48:02
 ============================
'''

class AddWord(object):
  """docstring for AddWord"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    self.new_words = set([])
    self.load_new_words()

  def load_new_words(self):
    self.logger.info("Loading new word list...")
    with open(self.options['wlist'], 'r', encoding='utf-8') as wlist:
      for line in wlist:
        self.new_words.add(line[0])

  def process(self):
    old_dct = open(self.options['dct'], 'r', encoding='utf-8')
    new_dct = open(self.options['dct']+'new', 'w', encoding='utf-8')
    ref_dct = open(self.options['ref'], 'r', encoding='utf-8')
    all_words = []
    for line in old_dct:
      new_dct.write(line)
      line = line.strip().split('|')[0]
      all_words.append(line)
    ref_words = {}
    for line in ref_dct:
      line = line.strip().split('|')
      ref_words[line[0]] = '|'.join(line[1:])
    ref_dct.close()

    new_words = list(self.new_words)
    for w in new_words:
      if w not in all_words and w in ref_words.keys():
        new_dct.write('%s|%s\n'%(w, ref_words[w]))
      elif w not in all_words and w not in ref_words.keys():
        new_dct.write("%s|||pi51|basic_ws_mnc|||Ag\\Ng\\j\\nr|mwh|||no|SHC||||4\n"%w)


if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='add_words')
  parser.add_argument("--version", action="version", version="add_words 1.0")
  parser.add_argument("-r", "--ref", action="store", dest="ref", default=r"D:\repos\clc\clc_sh_dev\lingware-data\dct\mnx\dct.u08", help='ref dct files')
  parser.add_argument("-d", "--dct", action="store", dest="dct", default=r"D:\repos\clc\clc_sh_dev\lingware-data\dct\shx\mod_dct.u08", help='target dct files')
  parser.add_argument("-w", "--wlist", action="store", dest="wlist", default=r"D:\repos\clc\clc_sh_dev\tests\rtestarea\TESTFILES\SHC\regression\char_dic_data.txt", help='word list files')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-add_words.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = AddWord(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))



