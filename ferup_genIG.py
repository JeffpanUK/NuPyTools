#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os
import re
import codecs
"""
Program: ferup_genIG.py
Function: generate IG tree model
Author: Junjie Pan (junjie.pan@nuance.com)
"""

class genIGTR(object):
  '''
  '''
  def __init__(self, options, logger):
    os.system("chcp 65001")
    self.logger = logger
    self.options = options

  def process(self):
    prefix = "{\n\tstring lhplus;\n\tstring char0;\n}\n%% forcing_rules\n"
    suffix = "%% data\nNOMATCH\t=\n"
    if not os.path.exists(self.options['fout']):
      os.mkdir(self.options['fout'])
    else:
      flag = input("%s exists, new model will replace old one. Continue? (y/n)"%self.options['fout'])
      if flag.lower() not in ['y','yes']:
        exit(0)
    f = self.options['default']
    with codecs.open(f, 'r', 'utf-8') as fi:
      for line in fi:
        orth, _hex, lhp = line.strip().split()
        self.logger.info("Process: %s(%s)"%(orth,_hex))
        fn = os.path.join(self.options['fout'], "%s.txt"%_hex)
        with codecs.open(fn, 'w', 'utf-8') as fo:
          fo.write(prefix)
          fo.write("%s\t%s\n"%(lhp, orth))
          fo.write(suffix)


if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup_genIG')
  parser.add_argument("--version", action="version", version="ferup_genIG 1.0")
  parser.add_argument(action="store", dest="default", default="", help='homograph default phone lists')
  parser.add_argument(action="store", dest="fout", default="ig", help='bad word list')
  parser.add_argument("-d", "--dict", action="store", dest="dct", default="", help='dictionary')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup_genIG.txt', 'w', 'utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = genIGTR(options, logger)
  appInst.process()
  allEndTP = time.time()


