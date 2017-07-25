#!/usr/bin/env py3
# -*- coding:utf-8 -*-

import tensorflow as tf
from tensorflow.contrib import keras
from tensorflow.contrib.keras import layers
from tensorflow.contrib.keras import wrappers
from tensorflow.contrib.keras import models
from tensorflow.contrib.keras import utils
import os,sys
import re
import codecs
import numpy as np
import pandas as pd

class Seq2Seq_G2P_P(object):
  '''
  '''
  def __init__(self):
    print("initializing word segmentation...")
  
  def viterbi(self, nodes):
    transit_maxtrix = {'be':0.5, 
                      'bm':0.5, 
                      'eb':0.5, 
                      'es':0.5, 
                      'me':0.5, 
                      'mm':0.5,
                      'sb':0.5, 
                      'ss':0.5}
    transit_matrix = {i:np.log(transit_matrix[i]) for i in transit_matrix.keys()}
    paths = {'b':nodes[0]['b'], 's':nodes[0]['s']}
    for l in range(1,len(nodes)):
        paths_ = paths.copy()
        paths = {}
        for i in nodes[l].keys():
            nows = {}
            for j in paths_.keys():
                if j[-1]+i in transit_matrix.keys():
                    nows[j+i]= paths_[j]+nodes[l][i]+transit_matrix[j[-1]+i]
            k = np.argmax(nows.values())
            paths[nows.keys()[k]] = nows.values()[k]
    return paths.keys()[np.argmax(paths.values())]
  
  def simple_cut(self, s):
    if s:
      r = models.models.predict(np.array([list(chars[list(s)].fillna(0).astype(int)) \
                                  + [0]*(time_step-len(s))]), 
                                  verbose=False)[0][:len(s)]
      r = np.log(r)
      nodes = [dict(zip(['s','b','m','e'], i[:4])) for i in r]
      t = self.viterbi(nodes)
      words = []
      for i in range(len(s)):
        if t[i] in ['s', 'b']:
          words.append(s[i])
        else:
          words[-1] += s[i]
      return words
    else:
        return []
  
  def cut_word(self, s):
    result = []
    j = 0
    for i in not_cuts.finditer(s):
        result.extend(self.simple_cut(s[j:i.start()]))
        result.append(s[i.start():i.end()])
        j = i.end()
    result.extend(self.simple_cut(s[j:]))
    return result
  
  def main(self, fn):
    data = []
    label = []
    tmp_data = []
    tmp_label = []
    train_data = codecs.open(fn, 'r', 'utf-8')
    for line in train_data:
      if len(line.strip().split()) == 0:
        data.append(tmp_data)
        label.append(tmp_label)
        tmp_data = []
        tmp_label = []
        continue
      line = line.strip().split()
      # print(line)
      tmp_data.append(line[0])
      tmp_label.append(line[-2])
      
      
    d = pd.DataFrame(index=range(len(data)))
    d['data'] = data
    d['label'] = label
    d.index = range(len(d))
    tag = pd.Series({'S':0, 'B':1, 'M':2, 'E':3})
    tagL = {'S':0, 'B':1, 'M':2, 'E':3}
    chars = [] #count all words and indexing them
    for i in data:
        chars.extend(i)

    chars = pd.Series(chars).value_counts()
    chars[:] = range(1, len(chars)+1)

    embedding_size = 200
    time_step = 50
    # print(tag)
    # print(d['label'])
    print(d['data'][0])
    print(chars[d['data'][0]])
    d['x'] = d['data'].apply(lambda x: np.array(list(chars[x])+[0]*(time_step-len(x))))
    print(len(d['label'][0]))
    input("pause...")
    # d['y'] = d['label'].apply(lambda x: np.array(utils.to_categorical(tag.reshape(-1,1),4)[tagL[x]]))
    d['y'] = d['label'].apply(lambda x: np.array(list(map(lambda y:utils.to_categorical(y,4), tag[x].reshape((-1,1))))))
    # d['y'] = d['label'].apply(lambda x: np.array(utils.to_categorical(tag.reshape(-1,1),4))+[np.array([[0,0,0,0,1]])]*(time_step-len(x)))

    
    sequence = layers.Input(shape=(time_step,), 
                      dtype='int32')
                      
    embedded = layers.Embedding(len(chars)+1, 
                        embedding_size, 
                        input_length=time_step, 
                        mask_zero=True)(sequence)
                        
    blayers.LSTM1 = wrappers.Bidirectional(layers.LSTM(256, return_sequences=True), 
                          merge_mode='sum')(embedded)
    blayers.LSTM2 = wrappers.Bidirectional(layers.LSTM(256, return_sequences=True), 
                          merge_mode='sum')(blayers.LSTM1)
    blayers.LSTM3 = wrappers.Bidirectional(layers.LSTM(256, return_sequences=True), 
                          merge_mode='sum')(blayers.LSTM2)
    # blayers.LSTM3 = layers.Bidirectional(layers.LSTM(256, return_sequences=True), 
                          # merge_mode='sum')(blayers.LSTM2)
                              
    output = wrappers.TimeDistributed(layers.Dense(4, activation='softmax'))(blayers.LSTM3)
    
    models.models = models.models(input=sequence, output=output)
    models.models.compile(loss='categorical_crossentropy', 
                  optimizer='adam', 
                  metrics=['accuracy'])

    batch_size = 1024
    
    history = models.models.fit(np.array(list(d['x'])), 
                        np.array(list(d['y'])).reshape((-1,time_step,)), 
                        batch_size=batch_size, 
                        nb_epoch=50)
 
if __name__ == '__main__':
  fn = r"D:\Documents\GitHub\Tools\data\corpus\ws.wapiti"
  ws = Seq2Seq_G2P_P()
  ws.main(fn)
  s = "今天天气不错"
  ws.cut(s)
    

