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

  def loadAcc(self, acc):
    fs = os.path.join(acc, "%s.acc"%(os.path.basename(acc)))
    with codecs.open(fs, 'r', 'utf-8') as fi:
      accuracy = fi.readline().strip()
    return accuracy

  def totalAcc(self):
    fs = os.listdir(self.options['maxent'])
    total = 0
    correct = 0
    for f in fs:
      fn = os.path.join(self.options['maxent'], f, f+"_pyt.rst")
      with codecs.open(fn, 'r','utf-8') as fi:
        for line in fi:
          line = line.strip()
          if line == "":
            continue
          line = line.split()
          if line[1] == line[2]:
            correct += 1
          total += 1
    self.logger.info("Total Polyphone: %d"%(total))
    self.logger.info("Total Correct: %d"%(correct))
    self.logger.info("Total Accuracy: %.4f"%(correct/total))

  def process(self):
    fs = list(map(lambda x: x.upper(), os.listdir(self.options['align_feat'])))
    facc = os.listdir(self.options['acc'])

    for f in fs:
      fn = os.path.join(self.options['align_feat'], f)
      tmp = {}
      with codecs.open(fn, 'r', 'utf-8') as fi:
        self.logger.info("Loading %s"%f)
        for line in fi:
          if line.strip() == "":
            continue
          line = line.strip().split()
          if line[-1] not in tmp.keys():
            tmp[line[-1]] = 1
          else:
            tmp[line[-1]] += 1
        self.dict[self.hex2char(f[:4])] = tmp

    wb = xlwt.Workbook()
    sh = wb.add_sheet("ME Model statistics")
    sh.write(0,0,"No")
    sh.write(0,1,"Orthography")
    sh.write(0,2,"Hex Code")
    sh.write(0,3,"Sentences")
    sh.write(0,4,"Details")
    sh.write(0,5,"ME Model")
    sh.write(0,6,"Explanation")
    for idx, item in enumerate(self.dict.items()):
      total = sum(item[1].values())
      tmp = []
      for i in item[1].items():
        tmp.append("%s\t %.2f(%d)"%(i[0], i[1]/total, i[1]))
      tmp = "\n".join(tmp)
      hexcode = self.char2hex(item[0])
      sh.write(idx+1, 0, idx)
      sh.write(idx+1, 1, item[0])
      sh.write(idx+1, 2, hexcode)
      sh.write(idx+1, 3, total)
      sh.write(idx+1, 4, tmp)
      if hexcode.lower() in facc:
        fpath = os.path.join(self.options['acc'], hexcode.lower())
        accuracy = self.loadAcc(fpath)
        sh.write(idx+1, 5, accuracy)
        sh.write(idx+1, 6, "L1 = 0.45 L2=0")
    # wb.save("report.xls") 
    # wb = xlwt.Workbook()
    sh = wb.add_sheet("IG Tree statistics")
    sh.write(0,0,"No")
    sh.write(0,1,"Orthography")
    sh.write(0,2,"Hex Code")
    sh.write(0,3,"Default")
    
    
    fs = list(filter(lambda x: "txt" in x and "0000" not in x, os.listdir(self.options['igtree'])))
    for idx, f in enumerate(fs):
      self.logger.info("Loading %s"%f)
      fn = os.path.join(self.options['igtree'], f)
      with codecs.open(fn, 'r', 'utf-8') as fi:
        lines = fi.readlines()
        tg = lines[5].strip().split()
        default_lhp = tg[0]
        orth = tg[1]
      sh.write(idx+1, 0, idx)
      sh.write(idx+1, 1, orth)
      sh.write(idx+1, 2, f[:4])
      sh.write(idx+1, 3, default_lhp)
    wb.save("report.xls")  
    self.logger.info("complete!")





if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup-format')
  parser.add_argument("--version", action="version", version="ferup-format 1.0")
  parser.add_argument(type=str, action="store", dest="align_feat", default="", help='input raw data')
  parser.add_argument("-a", "--acc", action="store", dest="acc", default="", help='accuracy files')
  parser.add_argument("-i", "--ig", action="store", dest="igtree", default="", help='igtree files')
  parser.add_argument("-m", "--me", action="store", dest="maxent", default="", help='maxent files')
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
  # appInst.process()
  appInst.totalAcc()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))
