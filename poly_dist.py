#-*- coding:utf-8 -*-
#!/usr/bin/env py3

import os
import sys
import re
import codecs
import copy
import csv
import xlwt

class Poly(object):
  '''
  calculate the distribution of polyphones
  '''
  def __init__(self, options, logger):
    self.options = options
    self.logger =logger
    self.total = 0
    self.poly_list = self.load_poly_list()
    self.all_poly = [self.load_poly_list() for _ in range(6)]
    self.all_total = []
    self.outList = []
    
  def isChinese(self, ch):
    hexCH = ord(ch)
    if (hexCH >= 0x3100  and hexCH <= 0x312F) \
      or (hexCH >= 0x3400  and hexCH <= 0x4BDF) \
      or (hexCH >= 0x4e00  and hexCH <= 0x9fff) \
      or (hexCH >= 0xF900  and hexCH <= 0xFA2D) \
      or (hexCH >= 0x20000 and hexCH <= 0x2a6d6)  \
      or (hexCH >= 0x2A700 and hexCH <= 0x2CEAF)  \
      or (hexCH >= 0x2F800 and hexCH <= 0x2FA1D) \
      or (hexCH >= 0xe000 and hexCH <=0xf8ff):
      return True
    else:
      return False
  
  def load_poly_list(self):
    with codecs.open(self.options['poly_list'], 'r', 'utf-8') as poly_list:
      polys = []
      for line in poly_list:
        line = line.strip().split()[1]
        polys.append([line,0])
    return dict(polys)
  
  def writeFile(self, fn, total, poly):
    with codecs.open(fn,"w","utf-8") as fo:
      fo.write("Total Char: %d\n" % total)
      poly = sorted(poly.items(), key=lambda x: x[1], reverse=True)
      for item in poly:
        fo.write("%s %d %f\n" % (item[0], item[1], (item[1]*100)/total))
    self.logger.info("Finishe %s" % fn)
    
  def writeExcel(self):
    wb = xlwt.Workbook()

    for poly, total, n in zip(self.all_poly, self.all_total, self.outList):
      ws = wb.add_sheet(str(n))      
      ws.write("Character", "Number","Percentage(%)")
      ws.write("Total", total, 100)
      poly = sorted(poly.items(), key=lambda x: x[1], reverse=True)
      for item in poly:
        ws.write(item[0], item[1], (item[1]*100)/total)
    
    ws = wb.add_sheet("Total")
    ws.write("Character", "Number","Percentage(%)")
    ws.write("Total", self.total, 100)
    poly = sorted(self.poly_list.items(), key=lambda x: x[1], reverse=True)
    for item in poly:
      ws.write(item[0], item[1], (item[1]*100)/self.total)
    
    wb.save("poly.xls")
  
  def processPOI(self):
    fbase = self.options['POI']
    total = 0
    poly = self.load_poly_list()
    district = os.listdir(fbase)
    for d in district:
      fs = os.listdir(os.path.join(fbase,d))
      for f in fs:   
        fn = os.path.join(fbase,d,f)
        self.logger.info("Process: %s"%fn)
        fpoi = csv.reader(codecs.open(fn, encoding="GBK"))
        while True:
          try:
            for line in fpoi:
              line = line[0]
              for c in line:
                if self.isChinese(c):
                  total += 1
                  self.total += 1
                  if c in poly.keys():
                    poly[c] += 1
                    self.poly_list[c] += 1
            break
          except:
            continue
    self.writeFile("POI.out", total, poly)
    
  def processSMS(self):
    fbase = self.options['SMS']
    total = 0 
    poly = self.load_poly_list()
    fn = codecs.open(fbase,'r','utf-8')
    self.logger.info("Process: %s"%fbase)
    for line in fn:    
      line = line.strip()
     # count = 0
     # countA = 0
      for c in line:
        if self.isChinese(c):
         # countA += 1
          total += 1
          self.total += 1
          if c in poly.keys():
            #count += 1
            poly[c] += 1
            self.poly_list[c] += 1
      #print("total:%d, poly:%d"%(countA, count))
    self.writeFile("SMS.out", total, poly)
  
  def processRecord(self):
    fbase = self.options['Record']
    total = 0
    poly = self.load_poly_list()
    fs = os.listdir(fbase)
    fs = list(filter(lambda x: "txt" in x, fs))
    for f in fs:
      self.logger.info("Process: %s"%f)
      fn = os.path.join(fbase, f)
      with codecs.open(fn, 'r', 'utf-8') as rd:
        while True:
          try:
            for line in rd:
              line = line.strip()
              for c in line:
                if self.isChinese(c):
                  total += 1
                  self.total += 1
                  if c in poly.keys():
                    poly[c] += 1
                    self.poly_list[c] += 1
            break
          except:
            continue
    self.writeFile("Record.out", total, poly)
    
  def processCTB(self):
    fbase = self.options['CTB']
    total = 0
    poly = self.load_poly_list()
    fs = os.listdir(fbase)
    for f in fs:
      self.logger.info("Process: %s"%f)
      fn = os.path.join(fbase, f)
      with codecs.open(fn, 'r', 'utf-8') as ctb:
        while True:
          try:
            for line in ctb:
              line = line.strip()
              if line[0] == r"<" or line == r"(完)":
                continue
              for c in line:
                if self.isChinese(c):
                  total += 1
                  self.total += 1
                  if c in poly.keys():
                    poly[c] += 1
                    self.poly_list[c] += 1
            break
          except:
            continue
    self.writeFile("CTB.out",total, poly)
  
  def processPKU(self):
    fbase = self.options['PKU']
    total = 0 
    poly = self.load_poly_list()
    fs = os.listdir(fbase)
    for f in fs:
      fn = os.path.join(fbase, f)
      with codecs.open(fn, 'r', 'gbk') as pku:
        self.logger.info("Process: %s"%fn)  
        while True:
          try:
            for line in pku:
              #line = re.sub("[0-9a-zA-Z\s\t]+","",line.strip())
              for c in line:
                if self.isChinese(c):
                  total += 1
                  self.total += 1
                  if c in poly.keys():
                    poly[c] += 1
                    self.poly_list[c] += 1
            break
          except:
            continue
        
    self.writeFile("PKU.out",total, poly)                

  def processWiki(self):  
    fbase = self.options['Wiki']
    total = 0 
    poly = self.load_poly_list()
    fn = fbase
    with codecs.open(fn, 'r', 'utf-8') as wiki:
      self.logger.info("Process: %s"%fn)
      
      while True:
        try:
          for line in wiki:
            line = re.sub("[0-9a-zA-Z\s\t]+","",line.strip())
            for c in line:
              if self.isChinese(c):
                total += 1
                self.total += 1
                if c in poly.keys():
                  poly[c] += 1
                  self.poly_list[c] += 1
          break
        except:
          continue
    self.writeFile("Wiki.out",total, poly) 
    
  def main(self):
    outList = ["PKU","SMS","Record","CTB","Wiki","POI"]
    total = 0
    poly = self.load_poly_list()
    for i in outList:
      fn = i+".out"
      with codecs.open(fn,'r','utf-8') as fout:
        first_line = fout.readline()
        total += int(first_line.strip().split()[-1])
        for line in fout:
          line = line.strip().split()
          poly[line[0]] += int(line[1])

    self.writeFile("Total.out", total, poly)
    
if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser
  
  parser = ArgumentParser(description='selectWord')
  parser.add_argument("--version", action="version", version="selectWord 1.0")
  parser.add_argument("--pku", action="store", dest="PKU", default=r"D:\Documents\poly\PKU", help='pku')
  parser.add_argument("--poi", action="store", dest="POI", default=r"D:\Documents\poly\POI\Data", help='poi')
  parser.add_argument("--ctb", action="store", dest="CTB", default=r"D:\Documents\poly\ctb8.0\data\raw", help='ctb')
  parser.add_argument("--sms", action="store", dest="SMS", default=r"D:\Documents\poly\Chinese SMS Corpus-Word.txt", help='sms')
  parser.add_argument("--wiki", action="store", dest="Wiki", default=r"D:\Documents\poly\wiki_s.txt", help='wiki')
  parser.add_argument("--record", action="store", dest="Record", default=r"D:\Documents\poly\li-li record", help='record')
  parser.add_argument("--poly_list", action="store", dest="poly_list", default=r"D:\Documents\poly\poly.list", help='record')
  

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-polylist.txt', 'w',encoding='utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = Poly(options, logger)
  # appInst.processPKU()
  # appInst.processWiki()
  # appInst.processRecord()
  # appInst.processPOI()
  # appInst.processCTB()  
  # appInst.processSMS()
  appInst.main()
  #appInst.writeExcel()
  allEndTP = time.time()