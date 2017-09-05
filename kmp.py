#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys

class kmp(object):
  """docstring for kmp"""
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    
  def getNext(self, pattern):
    _next = [-1]
    k = -1
    j = 0
    while(j<len(pattern)-1):
      if k!=-1 and pattern[k]!=pattern[j]:
        k = _next[k]
      j+=1
      k+=1
      print("j: %d\tk: %d"%(j,k))
      if pattern[k] == pattern[j]:
        _next.append(_next[k])
      else:
        _next.append(k)
    return _next

  def main(self):
    pattern = self.options['pattern']
    ref = self.options['ref']
    _next = self.getNext(pattern)
    index, i, j = 0, 0, 0
    self.logger.info("ref: %s"%ref)
    self.logger.info("pat: %s"%pattern)
    self.logger.info(_next)
    while(i < len(ref) and j < len(pattern)):
      if ref[i] == pattern[j]:
        i+=1
        j+=1
      else:
        index += (j - _next[j])
        if _next[j] != -1:
          j = _next[j]
        else:
          j = 0
          i+=1
    if j == len(pattern):
      self.logger.info("find index: %d"%(index))
    else:
      self.logger.warning("do not find substring")

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description="kmp string match alg")
  parser.add_argument("-version", action="version", version="kmp 1.0")
  parser.add_argument("-r","--ref",action="store", dest="ref", default="", help="reference string")
  parser.add_argument("-p","--pattern", action="store", dest="pattern", default="", help="pattern string")

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%H:%S')
  file_handler = logging.FileHandler('Log-kmp.txt','w', 'utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = kmp(options, logger)
  appInst.main()
  allEndTP = time.time()
  logger.info("Operation Finished [Time cost:%.3f Seconds]" % float(allEndTP - allStartTP))


