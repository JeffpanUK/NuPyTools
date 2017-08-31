#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: textgrid_rm_prm_stress.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-08-17 11:06:58
 ============================
''' 

class ModTextGrid(object):
  """docstring for ModTextGrid"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    if not os.path.exists(options['output']):
      os.mkdir(options['output'])

  def process(self):
    fs = os.listdir(self.options['textgrid'])
    for f in fs:
      self.logger.info("Process: %s"%f)
      fn = os.path.join(self.options['textgrid'], f)
      fon = os.path.join(self.options['output'], f)
      reset = True
      with open(fn, 'r', encoding='utf-8') as fi, open(fon, 'w', encoding='utf-8') as fo:
        for line in fi:
          if "item" in line:
            reset = True
          elif "词重音" in line or "句重音" in line:
            reset = False
          elif reset == False and "text" in line and "None" not in line:
            line = '            text = "0"\n'
          fo.write(line)

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ModTextGrid')
  parser.add_argument("--version", action="version", version="ModTextGrid 1.0")
  parser.add_argument(type=str, action="store", dest="textgrid", default="", help='input raw data')
  parser.add_argument("-o", "--output", action="store", dest="output", default="", help='output files')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ModTextGrid.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = ModTextGrid(options, logger)
  appInst.process()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))


