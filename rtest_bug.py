#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: rtest_bug.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-08-20 13:30:37
 ============================
'''

class rtest_bug(object):
  """docstring for rtest_bug"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger

  def process(self, root):
    exe = r'D:\programs\txt2spt-rls12\vautomotive\dbg\_tools\txt2spt_static.exe -I D:\programs\txt2spt-rls12\vautomotive\dbg\ori'
    for parent, dirns, files in os.walk(root):
      for dirn in dirns:
        self.process(os.path.join(parent, dirn))
      for f in files:
        fn = os.path.join(parent, f)
        self.logger.info("Process: %s"%fn)
        try:
          os.system('%s -n ding-ding -l Shanghainese -f "%s" -O embedded-high -o shc -x -e -c "text/plain;charset=UTF-8"'%(exe, fn))
        except:
          self.logger.error("Error in %s"%fn)
          continue

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='rtest_bug')
  parser.add_argument("--version", action="version", version="rtest_bug 1.0")
  parser.add_argument(type=str, action="store", dest="tests", default="", help='input raw data')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-rtest_bug.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = rtest_bug(options, logger)
  appInst.process(options['tests'])
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))
