#!/usr/bin/env py3
from __future__ import division, print_function, absolute_import

import os
import sys
import re
import numpy as np

import pdb

'''
 ============================
 @FileName: gen_fi_validation_data.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2018-03-22 17:07:19
 ============================
'''

class GENFIVALIDATION(object):
    """docstring for GENFIVALIDATION"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.embedding = self.__load_embedding(options['embed_path'],options['hand_path'])
        self.inputs = self.__load_text_input(options['input'])

    def __load_embedding(self, embed_path, hand_path):
        hand_embedding = np.load(hand_path)
        self.logger.info("load embedding from %s"%embed_path)
        embedding = {}
        try:
            with open(embed_path, 'r', encoding='utf-8') as fi:
                idx = 0
                for line in fi:
                    line = line.strip().split()
                    embedding[line[0]] = line[1:] + list(map(lambda x: str(float(x)), hand_embedding[idx]))
                    # pdb.set_trace()
                    idx+=1
        except Exception as e:
            raise e
        return embedding

    def __load_text_input(self, text_path):
        self.logger.info("load text from %s"%text_path)
        try:
            with open(text_path, 'r', encoding='utf-8') as fi:
                input_array = []
                for line in fi:
                    cur_line = []
                    line = re.sub("[a-zA-Z]+", "ENG", line)
                    line = re.sub("[0-9]+", "NUM", line)
                    line = list(line.strip())
                    idx = 0
                    while(idx < len(line)):
                        if line[idx] == '':
                            char = "".join(line[idx:idx+4])
                            cur_line.append(char)
                            idx+=4
                        elif line[idx] == " ":
                            idx+=1
                            continue
                        else:
                            char = line[idx]
                            cur_line.append(char)
                            idx+=1
                    input_array.append(cur_line)
            return input_array
        except Exception as e:
            raise e

    def __embed_lkp(self, char):
        if char in self.embedding.keys():
            return self.embedding[char]
        else:
            return self.embedding[r"</s>"]

    def  __gen_embedding(self):
        char_embed = []
        for sent in self.inputs:
            cur_embed = []
            for char in sent:
                cur_embed.append(self.__embed_lkp(char))
            char_embed.append(cur_embed)
        # pdb.set_trace()
        return char_embed

    def process(self):
        try:
            char_embed = self.__gen_embedding()
            time_step = 50
            with open(self.options['output'], 'w', encoding='utf-8') as fo:
                fo.write("feats :  L3\nlabel : L2 string   \nfeat_sep : space\ncol_sep: vb\nndim :2\n===============\n")
                for sent, sent_embed in zip(self.inputs, char_embed):
                    count = 0
                    for char, char_embed in zip(sent, sent_embed ):
                        if char == "|" or char == " " or char =="\t":
                            char = "S"
                        elif char == "ENG":
                            char = "E"
                        elif char == "NUM":
                            char = "N"
                        fo.write("%s|0|%s|\n"%(char," ".join(char_embed)))
                        count += 1
                    for i in range(time_step - count):
                        fo.write("%s|0|%s|\n"%(char," ".join(map(str, np.zeros(311)))))
                    fo.write("*EOS*\n")
        except Exception as e:
            raise e

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='gen_fi_validation_data')
  parser.add_argument("--version", action="version", version="gen_fi_validation_data 1.0")
  parser.add_argument("-i", "--input", action="store", dest="input", default="", help='input sentence file')
  parser.add_argument("-e", "--embed", action="store", dest="embed_path", default="", help='embedding path')
  parser.add_argument("-f", "--hand", action="store", dest="hand_path", default="", help='embedding path')
  parser.add_argument("-o", "--output", action="store", dest="output", default="valid.txt", help='output name')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-gen_fi_validation_data.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = GENFIVALIDATION(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))



