#-*- coding:utf-8 -*-
#/usr/bin/env py3
import os
import re
import codecs
import xlwt

class CountLabel(object):
  """docstring for CountLabel"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    self.dict = {}

  def hex2char(self, _hex):
    return chr(int("0x"+_hex, 16))

  def char2hex(self, char):
    return hex(ord(char))[2:].upper()

  def process(self):
    fs = os.listdir(self.options['labeled_data'])
    for f in fs:
      fn = os.path.join(self.options['labeled_data'], f)
      tmp = {}
      with codecs.open(fn, 'r', 'utf-8') as fi:
        self.logger.info("Loading %s"%f)
        for line in fi:
          if "=>" in line:
            tg = line.strip().split(',')[-1]
            if tg not in tmp.keys():
              tmp[tg] = 1
            else:
              tmp[tg] += 1
        self.logger.debug(tmp)
        self.logger.debug(f[:4])
        self.logger.debug(self.hex2char(f[:4]))
        self.dict[self.hex2char(f[:4])] = tmp
    with codecs.open(self.options['report'], 'w','utf-8') as fo:
      for item in self.dict.items():
        total = sum(item[1].values())
        fo.write("%s\t%d\n"%(item[0],total))     
        for i in item[1].items():
          fo.write("%s\t %.2f(%d)\n"%(i[0], i[1]/total, i[1]))
        fo.write('----------------\n')
    self.logger.info("complete!")

    wb = xlwt.Workbook()
    sh = wb.add_sheet("poly phone statistics")
    sh.write(0,0,"No")
    sh.write(0,1,"Orthography")
    sh.write(0,2,"Hex Code")
    sh.write(0,3,"Sentences")
    sh.write(0,4,"Details")
    sh.write(0,5,"ME Model")
    for idx, item in enumerate(self.dict.items()):
      total = sum(item[1].values())
      tmp = []
      for i in item[1].items():
        tmp.append("%s\t %.2f(%d)\n"%(i[0], i[1]/total, i[1]))
      tmp = "\n".join(tmp)
      sh.write(idx+1, 0, idx)
      sh.write(idx+1, 1, item[0])
      sh.write(idx+1, 2, self.char2hex(item[0]))
      sh.write(idx+1, 3, total)
      sh.write(idx+1, 4, tmp)
    wb.save("report.xls")  
    self.logger.info("complete!")





if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup-format')
  parser.add_argument("--version", action="version", version="ferup-format 1.0")
  parser.add_argument(type=str, action="store", dest="labeled_data", default="", help='input raw data')
  parser.add_argument(type=str, action="store", dest="report", default="report.txt", help='output file')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup-CountLabel.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = CountLabel(options, logger)
  # appInst.Process()
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))
