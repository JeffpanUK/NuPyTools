#-*-coding:utf-8-*-
#!\usr\bin\env py3
import os,sys
import codecs
import re
import shutil

class ldb2lab(object):
  """docstring for ldb2lab"""
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    if not os.path.exists(options['output']):
      os.mkdir(options['output'])
    

  def loadldbs(self):
    fs = os.listdir(self.options['ldbs'])
    for f in fs:
      self.logger.info("Process: %s"%f)
      count = 0
      find_sil = False
      sil_record = []
      fn = os.path.join(self.options['ldbs'], f)
      with codecs.open(fn,'r','utf-8') as fi:
        for line in fi:
          line = line.strip()
          if r"<LD_W_PHON>" in line:
            count += len(re.findall("[0-9]", line))
            find_sil = True
          elif find_sil and r"<LD_W_SILDUR>" in line:
            find_sil = False
            sil_record.append((count, re.search('[0-9]+', line).group(0)))
      with codecs.open(os.path.join(self.options['output'], f[:-3]+'txt'), 'w','utf-8') as fo:
        for item in sil_record:
          if item[1] == "0":
            continue
          fo.write("%s\t%s\n"%(item[0], item[1]))

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ldb2lab')
  parser.add_argument("--version", action="version", version="ldb2lab 1.0")
  parser.add_argument(type=str, action="store", dest="ldbs", default="", help='input ldb data directory')
  parser.add_argument("-o", "--output", action="store", dest="output", default="labs", help='output directory')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ldb2lab.txt', 'w')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = ldb2lab(options, logger)
  appInst.loadldbs()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))