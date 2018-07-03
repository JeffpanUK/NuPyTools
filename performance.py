#!/usr/bin/env py3
from __future__ import division, print_function, absolute_import

import os
import sys
import re
import codecs
import pdb

'''
 ============================
 @FileName: performance.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2018-03-19 13:09:18
 ============================
'''
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

class PERFORMANCE(object):
    """docstring for PERFORMANCE"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.perform = {"init":[],"latency":[],"rtf":[]}

    def warm_up(self, repeat=3):
        for i in range(repeat):
            self.logger.info("Warn-up Round: %d"%(i+1))
            os.system("%s %s"%(self.options['exe'],self.options['args']))

    def test(self, repeat=5):
        for i in range(repeat):
            self.logger.info("Test Round: %d"%(i+1))
            os.system("%s %s"%(self.options['exe'],self.options['args']))
            os.system("mv vocalizer_0.txt vocalizer_%d.txt"%(i+1))

    def result_parsing(self, idx, fname):
        f = open(fname, 'r', encoding='utf-8',erros='ignore')
        init_time = 0
        latency = 0
        init_time_ready = False
        latency_ready = False
        for line in f:
            if "Compstats Pipeline Open Report Start" in line:
                init_time_ready = True
            elif "Compstats Synthesis Latency Report Start" in line:
                latency_ready = True
            elif "TOTAL" in line and init_time_ready:
                init_time_ready = False
                init_time += float(line.strip().split()[1])
            elif "TOTAL" in line and latency_ready:
                latency_ready = False
                latency = float(line.strip().split()[1])
            elif "Real-time rate" in line:
                rtf = float(line.strip().split()[2])
        self.perform["init"].append(init_time)
        self.perform["latency"].append(latency)
        self.perform["rtf"].append(rtf)
        self.logger.info("[%d] init: %.2f ms, latency: %.2f ms, RTF: %.2f"%(idx, init_time, latency, rtf))

    def process(self, warm_time=3, test_time=5):
        self.warm_up(repeat = warm_time)
        self.test(repeat = test_time)
        for idx in range(test_time):
            self.result_parsing(idx+1, "vocalizer_%d.txt"%(idx+1))
        self.logger.info("[Average] init: %.2f ms, latency: %.2f ms, RTF: %.2f"%(mean(self.perform["init"]), mean(self.perform["latency"]), mean(self.perform["rtf"])))

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='performance')
  parser.add_argument("--version", action="version", version="performance 1.0")
  parser.add_argument(type=str, action="store", dest="exe", default="sample_static.exe", help='engine name')
  parser.add_argument(type=str, action="store", dest="args", default=r'-I "../mnc" -v lili-ml -O embedded-high -T 2 -i "testinginput.txt"', help='engine name')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-performance.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = PERFORMANCE(options, logger)
  appInst.process()
  # appInst.result_parsing(1, "vocalizer_0.txt")
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))

