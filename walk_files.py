#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os
import re
import codecs
"""
Program: walk_files.py
Function: walk all files to check their modified date
Author: Junjie Pan (junjie.pan@nuance.com)
"""

class WalkThrough(object):
  '''
  '''
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    
  def process(self, root):
    format = "%Y-%m-%d %H:%M:%S"
    th_time = time.mktime(time.strptime(self.options["ST"], format))
    for parent, dirnames, filenames in os.walk(root):
      for dirname in dirnames:
        self.process(os.path.join(parent, dirname))
      for filename in filenames:
        mtime = os.path.getmtime(os.path.join(parent, filename))
        if mtime > th_time:
          self.logger.info(os.path.join(parent, filename))
        
    

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='walk_files')
  parser.add_argument("--version", action="version", version="walk_files 1.0")
  parser.add_argument("-s", "--startTime", action="store", dest="ST", default="2017-07-21 17:12:00", help='modified time.')
  parser.add_argument("-r", "--root", action="store", dest="root", default=r"D:\repos\ferup\data\local\hmogrph\cache\full_ldbs", help='root path.')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-walk_files.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = WalkThrough(options, logger)
  appInst.process(options["root"])
  # appInst.formatCheck()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))