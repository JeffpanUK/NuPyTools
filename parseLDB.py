#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: parserLDB
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-11-06 11:01:28
 ============================
'''
class LDBPARSER(object):
    """docstring for LDBPARSER"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.punc = re.compile('[%s]'%(''.join(self.load_punc(options['puncf']))))

    #load punctuation file
    def load_punc(self, puncf):
        punc = []
        with open(puncf, 'r', encoding='utf-8') as fi:
            for line in fi:
                line = line.strip().split()
                punc.extend(line)
        return list(set(punc))

    def parse_line(self, line):
        line = line.strip().split()[1]
        return line

    def  parse_ldb(self, lines):
        sent = []
        phone = []
        for idx, line in enumerate(lines):
            if "WORD_DCT" in line:
                sent_tmp = list(re.sub(self.punc, '', self.parse_line(lines[idx-1])))
                phone_tmp = self.parse_line(lines[idx+3]).split(r"-")
                assert(len(sent_tmp) == len(phone_tmp))
                sent+= sent_tmp
                phone += phone_tmp
        return sent, phone

    def process(self):
        fs = os.listdir(self.options['ldb'])
        sents = []
        phones = []
        for  f in fs:
            self.logger.info("Process LDB: %s"%f)
            fn = os.path.join(self.options['ldb'], f)
            with open(fn, 'r', encoding='utf-8') as fi:
                lines = fi.readlines()
            sent, phone = self.parse_ldb(lines)
            sents.append(sent)
            phones.append(phone)
        return sents, phones

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='parseLDB')
  parser.add_argument("--version", action="version", version="parseLDB 1.0")
  parser.add_argument(type=str, action="store", dest="ldb", default="", help='input ldb files')
  parser.add_argument("-p", "--puncf", action="store", dest="puncf", default=r"F:\Jeff\NN\prm\scripts\punc.txt")


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-parseLDB.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = LDBPARSER(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))

