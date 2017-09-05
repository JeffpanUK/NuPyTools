# -*- coding:utf-8 -*-
#/urs/bin/env/ py3
import keras
from keras.utils import np_utils
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, Embedding, LSTM, TimeDistributed, Input, merge, Bidirectional
import numpy as np
import os,sys
import codecs
import pandas as pd
import re
import pdb
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF

KTF.set_session(tf.Session(config=tf.ConfigProto(device_count={'gpu':0})))

class BlstmWS(object):
  """docstring for BlstmWS"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    self.tag = pd.Series({'S':0, 'B':1, 'M':2, 'E':3}) 
    self.tag_size = len(self.tag)
    print(self.tag_size)
    if options['task'] in ["training", "auto"]:
      self.training_data = self.processLabeled(self.options['corpus'])
      self.charDct = self.genWordDct()
      self.training_data = self.genIOData(self.training_data)
    else:
      self.charDct = self.loadWordDct()
    
    


  def wordCount(self, corpus):
    chars = []
    for sent in corpus:
      chars.extend(sent)
    return pd.Series(chars).value_counts()

  def processLabeled(self, corpus):
    if os.path.isdir(corpus):
      fs = os.listdir(corpus)
    else:
      fs = [corpus]
    sent = []
    label = []
    tmp = [[],[]]
    for f in fs:
      self.logger.info("Process: %s"%f)
      fn = os.path.join(corpus, f)
      with codecs.open(fn, 'r', 'utf-8') as f:
        for line in f:
          line = line.strip().split()
          if len(line) == 0:
            sent.append(tmp[0])
            label.append(tmp[1])
            tmp = [[],[]]
          else:
            tmp[0].append(line[0])
            tmp[1].append(line[1])

    data = pd.DataFrame()
    data['sent'] = sent
    data['label'] = label
    #remove over-long sentences
    data = data[data['sent'].apply(len) <= self.options['timestep']]
    return data

  def genWordDct(self):
    data = self.training_data
    # rank chars based on frequencies
    charDct = self.wordCount(data['sent'])
    charDct[:] = range(2, len(charDct)+2)
    with codecs.open(self.options['charDct'], 'w', 'utf-8') as fo:
      for char in charDct.items():
        fo.write("%s %d\n"%(char[0],char[1]))
    return charDct

  def loadWordDct(self):
    tmp = {}
    with codecs.open(self.options['charDct'],'r','utf-8') as fi:
      for line in fi:
        line = line.strip().split()
        tmp[line[0]] = int(line[1])
    charDct = pd.Series(tmp)
    return charDct



  def genIOData(self, data):
    #generate input format
    _input = []
    _output = []
    for s, l in zip(data['sent'], data['label']):
      _input.append(np.array(list(self.charDct[s])+[0]*(self.options['timestep']-len(s))))
      _output.append(np.array(list(map(lambda x: np_utils.to_categorical(x, self.tag_size), self.tag[l].values.reshape(-1,1)))+[np.array([[0,0,0,1]])]*(self.options['timestep']-len(l))))    
    data['input'] = _input
    data['output'] = _output
    return data

  def tagFormat(self, ref, tag):
    catetogry = list(map(lambda x: np_utils.to_categorical(x, self.tag_size), ref[tag].value.reshape(-1,1)))
    return catetogry

  def viterbi(self, nodes):
    transit_maxtrix = {'BE':0.5, 
                      'BM':0.5, 
                      'EB':0.5, 
                      'ES':0.5, 
                      'ME':0.5, 
                      'MM':0.5,
                      'SB':0.5, 
                      'SS':0.5
                     }

    transit_maxtrix = {i:np.log(transit_maxtrix[i]) for i in transit_maxtrix.keys()}
    paths = {'B':nodes[0]['B'], 'S':nodes[0]['S']}
    for node in nodes[1:]:
      begin = paths.copy()
      paths = {}
      for item in node.items():
        cur = {}
        for b in begin.items():
          cur_path = b[0][-1] + item[0]
          if cur_path in transit_maxtrix:
            cur[b[0]+item[0]] = b[1] + transit_maxtrix[cur_path] + item[1]
        idx = np.argmax(list(cur.values()))
        paths[list(cur.keys())[idx]] = list(cur.values())[idx]
    best_path = list(paths.keys())[np.argmax(list(paths.values()))]
    return best_path

    
  def train(self):
    hidden_unit = 32
    timestep, dimension, batchSize, epochs = self.options['timestep'], self.options['dimension'], self.options['batchSize'], self.options['epochs']
    model = Sequential()
    model.add(Embedding(len(self.charDct)+2, dimension, input_length=timestep, mask_zero=True))
    model.add(Bidirectional(LSTM(units=hidden_unit,activation='tanh', return_sequences=True), input_shape=(timestep, dimension)))
    # model.add(Bidirectional(LSTM(units=hidden_unit,activation='tanh', return_sequences=True), input_shape=(hidden_unit, dimension)))
    # model.add(Bidirectional(LSTM(units=hidden_unit,activation='tanh', return_sequences=True), input_shape=(hidden_unit, dimension)))
    model.add(TimeDistributed(Dense(self.tag_size, activation='softmax')))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    history = model.fit(np.array(list(self.training_data['input'])), np.array(list(self.training_data['output'])).reshape((-1,timestep,self.tag_size)), batch_size=batchSize, epochs=epochs)
    model.save(self.options['model'])
    return model

  def evaluate_subprocess(self, sentence, model):
    if sentence:
      results = model.predict(np.array([list(self.charDct[list(sentence)].fillna(0).astype(int)) + [0]*(self.options['timestep']- len(sentence))]), verbose=False)[0][:len(sentence)]
      results = np.log(results)
      nodes = [dict(zip(['S','B','M','E'], i)) for i in results]
      t = self.viterbi(nodes)
      words = []
      for i in range(len(sentence)):
        if t[i] in ['S','B']:
          words.append(sentence[i])
        else:
          words[-1] += sentence[i]
      return words
    else:
      return []

  def test(self):
    model = load_model(self.options['model'])
    eso = re.compile(u'([\da-zA-Z ]+)|[。，、？！\.\?,!]')
    results = []
    fs = os.listdir(self.options["testDir"])
    for f in fs:
      fn = os.path.join(self.options["testDir"],f)
      with codecs.open(fn, 'r','utf-8') as fi:
        for line in fi:
          sentence = line.strip()
          idx = 0
          for sub_idx in re.finditer(eso, sentence):
            results.extend(self.evaluate_subprocess(sentence[idx:sub_idx.start()], model))
            #append ESOs
            results.append(sentence[sub_idx.start():sub_idx.end()])
            idx = sub_idx.end()
    with codecs.open(self.options['output'],'w','utf-8') as fo:
      fo.write("  ".join(results))
    return results

  def evaluation(self):
    model = load_model(self.options['model'])
    test_data = self.genIOData(self.processLabeled(self.options['testDir']))
    loss, accuracy = model.evaluate(np.array(list(test_data['input'])), np.array(list(test_data['output'])).reshape((-1,self.options['timestep'],self.tag_size)), batch_size=self.options['batchSize'], verbose=True)
    print("\nloss: %f"%loss)
    print("accuracy: %f"%accuracy)


if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='BlstmWS')
  parser.add_argument("--version", action="version", version="BlstmWS 1.0")
  parser.add_argument(action="store", dest="corpus", default="", help='training corpus')
  parser.add_argument("-t", "--timstep", action="store", dest="timestep", default=20, help='time step')
  parser.add_argument("-d", "--dimension", action="store", dest="dimension", default=100, help='dimemsion')
  parser.add_argument("-b", "--batchsize", action="store", dest="batchSize", default=20, help='batch size')
  parser.add_argument("-td", "--testdir", action="store", dest="testDir", default="ws_test", help='batch size')
  parser.add_argument("-m", "--model", action="store", dest="model", default="keras_BLSTM_WS.kmd", help='model name')
  parser.add_argument("-o", "--output", action="store", dest="output", default="ws_result.txt", help='output text')
  parser.add_argument("-e", "--epochs", type=int, action="store", dest="epochs", default=2, help='epochs')
  parser.add_argument("-task", "--task", action="store", dest="task", default="auto", help='epochs')
  parser.add_argument("-c", "--charDct", action="store", dest="charDct", default="charDct.pb", help='char dictionary')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-BlstmWS.txt', 'w', 'utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = BlstmWS(options, logger)
  if options['task'] in ["training", "auto"]:
    appInst.train()
    appInst.evaluation()
  elif options['task'] == "test":
    appInst.test()
 
  allEndTP = time.time()