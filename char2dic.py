#!/usr/bin/env py3
from __future__ import division, print_function, absolute_import

import os
import sys
import re
import numpy as np

import pdb

'''
 ============================
 @FileName: char2dic
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2018-01-30 14:50:17
 ============================
'''

class Char2Dic(object):
    """docstring for Char2Dic"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.sys_dic = self.__load_sys_dic(options['sysdic'])
        self.char_index = self.__load_char_index(options['charIndex'])

    def __load_sys_dic(self, dic_path):
        word_dic = set([])
        fdic = open(dic_path, 'r',encoding='utf-8')
        for line in fdic:
            line = line.strip().split('|')[0]
            if len(line) > 1:
                word_dic.add(line)
        return list(word_dic)

    def  __load_char_index(self, char_index):
        return np.load(char_index)

    def gen_feat(self, char):
        feat = [0,0,0,0,0,0,0,0,0]
        for word in self.sys_dic:
            if len(word) == 2:
                if char in word[0]:
                    feat[0] = 1
                if char in word[-1]:
                    feat[1] = 1
            if len(word) == 3:
                if char in word[0]:
                    feat[2] = 1
                if char in word[1:-1]:
                    feat[3]  = 1
                if char in word[-1]:
                    feat[4] = 1
            if len(word) == 4:
                if char in word[0]:
                    feat[5] = 1
                if char in word[1:-1]:
                    feat[6]  = 1
                if char in word[-1]:
                    feat[7] = 1
            if len(word) >= 5:
                if char in word:
                    feat[8] = 1
        return feat

    def process(self):
        feats = []
        for char in self.char_index:
            feats.append(self.gen_feat(char))
        np.save(self.output, feats)

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='char2dic')
  parser.add_argument("--version", action="version", version="char2dic 1.0")
  parser.add_argument("-d", "--sysdic", action="store", dest="sysdic", default=r"data/dic.u08", help='system dictionary')
  parser.add_argument("-c", "--charindex", action="store", dest="charIndex", default=r"data/char_index.npy", help='char index')
  parser.add_argument("-o", "--output", action="store", dest="output", default=r"char_9.dic", help='output')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-char2dic.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = Char2Dic(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))


