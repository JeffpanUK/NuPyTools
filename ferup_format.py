#-*-coding:utf-8-*-
#!\usr\bin\env py3

import os
import sys
import re
import codecs

class Format(object):
  '''
  format Shanghainese (SHC) corpus from Naunce Linguistic team
  '''
  def __init__(self, options, logger):
    self.base = options['fpath']
    self.fs = os.listdir(self.base)
    self.logger = logger
    self.options = options
  
  def Process(self):
    if self.options['comb'] == 1:
      self.Process_comb(self.options['out'], self.options['task'])
    else:
      self.Process_Nocomb(self.options['out'], self.options['task'])

  def Process_comb(self, out, task):
    try:
      outbase = os.path.dirname(os.path.abspath(out))
      if not os.path.exists(outbase):
        os.makedirs(outbase)
        self.logger.info("%s does not exists, will be created!" % outbase)
      with codecs.open(out, 'w', 'utf-8') as fo:
        self.fs = list(sorted(self.fs))
        for f in self.fs:
          fn = os.path.join(self.base, f)
          self.logger.info("Process: %s" % f)
          with codecs.open(fn, 'r', 'utf-8') as fi:
            for line in fi:
              line = re.sub('[\'\+]','',line)
              if task == 'ws':
                line = re.sub('[\-]',' ',line)
              line = re.sub('\s+',' ',line)
              fo.write(line + '\n')
            
    except IOError as ioerror:
      self.logger.error(ioerror)
    except Exception as e:
      self.logger.error(e)
  
  def Process_Nocomb(self, out, task):
    try:
      if not os.path.exists(out):
        os.makedirs(out)
        self.logger.info("%s does not exists, will be created!"%out)
      for f in self.fs:
        fn = os.path.join(self.base, f)
        fop = os.path.join(out, f)
        fo = codecs.open(fop, 'w', 'utf-8')
        with codecs.open(fn, 'r', 'utf-8') as fi:
          self.logger.info("Process: %s" % f)
          for line in fi:
            line = re.sub('[\'\+]','',line)
            if task == 'ws':
                line = re.sub('[\-]',' ',line)
            line = re.sub('\s+',' ',line)
            fo.write(line + '\n')
    except IOError as ioerror:
      self.logger.error(ioerror)
    except Exception as e:
      self.logger.error(e)
      
  
  def formatCheck(self):
    fs = os.listdir(self.options['checkf'])
    #No combination
    if self.options['comb'] == 0:
      dirn = self.options['out']
      if not os.path.exists(dirn):
        os.makedirs(dirn)
      for f in fs:
        fn = codecs.open(os.path.join(self.options['checkf'], f), 'r', 'utf-8')
        fo = codecs.open(os.path.join(self.options['out'], f), 'w', 'utf-8')
        #fo.write("")
        self.logger.info("Processing: %s"%f)
        for line in fn:
          if "Lexicon" not in line:
            continue
          line = re.sub('\/POS:[^\s]+\s+',' ',line[8:])
          fo.write("!%s\n"%line)
        fo.close()
        fn.close()
    else:
      dirn = os.path.dirname(os.path.abspath(self.options['out']))
      if not os.path.exists(dirn):
        os.makedirs(dirn)
      fo = codecs.open(os.path.join(self.options['out']), 'w', 'utf-8')
      for f in fs:
        fn = codecs.open(os.path.join(self.options['checkf'], f), 'r', 'utf-8')
        self.logger.info("Processing: %s"%f)
        #fo.write("")
        for line in fn:
          if "Lexicon" not in line:
            continue
          line = re.sub('[\/POS:[a-z]+\s+]',' ',line[8:])
          fo.write("!%s"%line)
        fn.close()
      fo.close()
      
if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ferup-format')
  parser.add_argument("--version", action="version", version="ferup-format 1.0")
  parser.add_argument(type=str, action="store", dest="fpath", default="", help='input raw data')
  parser.add_argument(type=str, action="store", dest="out", default="", help='output file(for comb mode); output dir(for non-comb mode)')
  parser.add_argument(type=str, action="store", dest="task", default="", help='pw - prosody word; ws - word segmentation')
  parser.add_argument("-c", "--comb", action="store", dest="comb", type=int, default=0, help='0: no combination; 1: combination.')
  parser.add_argument("-f", "--checkf", action="store", dest="checkf", type=str, default=r"D:\Documents\GitHub\Tools\data\corpus\ws_result", help='corpus directory')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ferup-format.txt', 'w')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = Format(options, logger)
  # appInst.Process()
  appInst.formatCheck()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))


