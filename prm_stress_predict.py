#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os,sys
import codecs
import re
import numpy as np
import keras
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, Embedding, LSTM, TimeDistributed, Input, merge, Bidirectional
import pandas as pd
import pdb

class StressPredict(object):
  """docstring for StressPredict"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger

  '''
    BMES 
  '''
  def BMES(self, idx, length):
    if length == 1:
      return [0,0,0,1]
    elif idx == 0:
      return [1,0,0,0]
    elif idx == length - 1:
      return [0,0,1,0]
    else:
      return [0,1,0,0]


  def loadCorpus(self):
    fs = self.options['corpus']
    pws = []
    if os.path.isdir(fs):
      fs = os.listdir(fs)
    for f in fs:
      self.logger.info("Process: %s"%f)
      with codecs.open(f, 'r', 'utf-8') as fi:
        for line in fi:
          line = line.strip().split()
          line = list(map(lambda x: re.split('[\+\-]', x), line))
          pws.extend(line)

    '''
      generate stress sequence for each PW
      eg. stresses = [['1','0','1','0'],
                      ['0','0','1','0'],
                      ['0','0','1','1'],
                      ['0','0','1','0']]
    '''
    stresses = []
    for pw in pws:
      idx = 0
      stress = []
      for lex in pw:
        while(idx < len(lex)):
          if pw[idx] == "'":
            stress.append(1)
            idx += 1
          else:
            stress.append(0)
      stresses.append(stress)

    embeddings = []
    for pw in pws:
      for lex in pw:
        lex = re.sub("[0-9]+", "NUM", lex)
        lex = re.sub("[a-zA-Z]+", "ENG", lex)
        lex = re.sub("'", "", lex)
        for idx, c in enumerate(lex):
          position = self.BMES(idx, len(lex))
          if c not in self.embedding.keys():
            embeddings.append(self.embedding['</s>']+position)
          else:
            embeddings.append(self.embedding[c]+position)

    return embeddings, stresses

    def train(self):
      hidden_unit = 256
      timestep, dimension, batchSize, epochs = self.options['timestep'], self.options['dimension'], self.options['batchSize'], self.options['epochs']
      model = Sequential()
      model.add(Bidirectional(LSTM(units=hidden_unit, activation="tanh", return_sequence=True), input_shape=timestep))



      





    




if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup_homos')
  parser.add_argument("--version", action="version", version="ferup_homos 1.0")
  parser.add_argument(action="store", dest="wlist", default="", help='current homograph lists')
  parser.add_argument(action="store", dest="outfile", default="badword.wlist", help='bad word list')
  parser.add_argument("-d", "--dict", action="store", dest="dct", default="", help='dictionary')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup_homos.txt', 'w', 'utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = FilterHomos(options, logger)
  appInst.process()
  allEndTP = time.time()