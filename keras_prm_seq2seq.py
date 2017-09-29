#!/usr/bin/env py3
import os
import sys
import re
import numpy as np
from  keras.layers import Masking, LSTM, Dense, TimeDistributed, Input, merge, Bidirectional
from keras.models import Model, Sequential, load_model
from keras.utils import np_utils
from keras.optimizers import RMSprop
from parseTextGrid import TGPARSER
'''
 ============================
 @FileName: keras_prm_seq2seq.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-09-22 10:23:57
 ============================
'''

class PRM(object):
    """docstring for PRM"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.embedding = self.loadEmbedding(r"D:\Documents\PRM\embedding\chr.txt")
        self.stress_timestep = 10
        self.padding = np.zeros(100)

    def  loadTextGrid(self, fi):
        tg = TGPARSER(fi, self.logger)
        tg.process()
        return tg
    
    def loadEmbedding(self, embed):
        embedding = {}
        with open(embed, 'r', encoding='utf-8') as fi:
            for line in fi:
                line = line.strip().split()
                embedding['%s%s'%(line[0],line[1])] = np.array(list(map(lambda x: float(x), line[2:])))
        return embedding

    def get_pw_words_stress(self, tgs):
        orths, pws, stresses = [], [],[]
        for tg in tgs:
            orths += tg.items['汉字']['intervals'][1:-1]
            pws += tg.items['韵律边界']['points'][:-1]
            stresses += tg.items['词重音']['intervals'][1:-1]
        self.logger.debug(orths)
        self.logger.debug(pws)
        self.logger.debug(stresses)
        assert(len(orths) == len(pws))
        pw_words = []
        pw_stresses = []
        idx = -1
        for orth, pw, stress in zip(orths, pws, stresses):
            if pw[1] != '0' and orth[2]!='sp' and stress[2]!='None':
                pw_words.append([])
                pw_stresses.append([])
                idx += 1
                pw_words[idx].append(orth[2])
                pw_stresses[idx].append(int(stress[2]))
            elif pw[1] == '0':
                pw_words[idx].append(orth[2])
                pw_stresses[idx].append(int(stress[2]))
        self.logger.debug(pw_words)
        self.logger.debug(pw_stresses)
        return pw_words, pw_stresses

    def isChinese(self, ch):
        try:
            hexCH = ord(ch)
        except:
            print(ch)
        if (hexCH >= 0x3100  and hexCH <= 0x312F) \
            or (hexCH >= 0x3400  and hexCH <= 0x4BDF) \
            or (hexCH >= 0x4e00  and hexCH <= 0x9fff) \
            or (hexCH >= 0xF900  and hexCH <= 0xFA2D) \
            or (hexCH >= 0x20000 and hexCH <= 0x2a6d6)  \
            or (hexCH >= 0x2A700 and hexCH <= 0x2CEAF)  \
            or (hexCH >= 0x2F800 and hexCH <= 0x2FA1D):
            return True
        else:
            return False



    def BMES_tag(self, pw_word):
        pw_len = len(pw_word)
        if pw_len > self.stress_timestep:
            pw_word = pw_word[:self.stress_timestep]
            pw_len = stress_timestep
        elif pw_len < self.stress_timestep:
            for i in range(self.stress_timestep - pw_len):
                pw_word.append('NULL')

        tags = []
        for idx, ch in enumerate(pw_word):
            if ch == "NULL" or ch == "sp" or ch == "sil":
                ch = "NULL"
                tag = "" 
            elif ch == '</s>' or not self.isChinese(ch):
                pw_word = '</s>'
                tag = 's'
            elif pw_len == 1:
                tag = 's'
            elif idx == 0:
                tag = 'b'
            elif idx == len(pw_word) - 1:
                tag = 'e'
            else:
                tag = 'm'
            tags.append('%s%s'%(ch, tag))

        return tags


    def convert_pw_to_embedding(self, pw_word):
        pw_tags = self.BMES_tag(pw_word)
        ch_embedding = []
        for ch in pw_tags:
            if ch != "NULL":
                ch_embedding.append(self.embedding[ch])
            else:
                ch_embedding.append(self.padding)
        return ch_embedding

    def Model_1(self, timestep, tag_num, hidden_unit, dimension):
        model = Sequential()
        model.add(Masking(mask_value=np.array([0]*dimension),input_shape=(timestep,dimension,)))
        model.add(TimeDistributed(Dense(units=hidden_unit,activation = 'sigmoid')))
        model.add(Bidirectional(LSTM(units=hidden_unit,activation='tanh', dropout=0.5,return_sequences=True)))
        model.add(Bidirectional(LSTM(units=hidden_unit,activation='tanh',dropout=0.5, return_sequences=True)))
        model.add(Dense(tag_num,activation='softmax'))
        #pt = Adam()
        rmspop = RMSprop()
        #sgd = SGD(lr=0.001, decay=1e-9, momentum=0.9, nesterov=True)
        model.compile(optimizer=rmspop,loss='categorical_crossentropy',metrics=["accuracy"])
        model.summary()
        return model


    def stress_train(self, pw_words, pw_stresses):
        tags = [0,1]
        tag_num = len(tags)
        hidden_unit = 256
        timestep = self.stress_timestep
        dimension = 100
        batchsize = 100
        epochs = 20

        _input = []
        for word in pw_words:
            _input.append(self.convert_pw_to_embedding(word))
        _input = np.array(_input)

        _output = []
        for stress in pw_stresses:
            _output.append(np.array(list(np_utils.to_categorical(stress, tag_num)) + [np.array([0, 0])]*(timestep-len(stress))))

        _output =  np.array(_output).reshape((-1,timestep,tag_num))

        model = self.Model_1(timestep, tag_num, hidden_unit, dimension)
        model.fit(_input, _output, batch_size=batchsize, epochs=epochs)
        model.save("prm.kmd")

    def test(self, fspath):
        tgs = []
        fs = os.listdir(fspath)
        for f in fs:
            fn = os.path.join(fspath, f)
            self.logger.info("Process: %s"%f)
            tgs.append(appInst.loadTextGrid(fn))
        pw_words, pw_stresses = appInst.get_pw_words_stress(tgs)
        appInst.stress_train(pw_words, pw_stresses)

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='keras_prm_seq2seq.py')
  parser.add_argument("--version", action="version", version="keras_prm_seq2seq.py 1.0")

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-keras_prm_seq2seq.py.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = PRM(options, logger)
  appInst.test(r'D:\Documents\PRM\demo')

  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))

        

