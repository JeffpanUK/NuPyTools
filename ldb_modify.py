#-*-coding:utf-8-*-
#!\usr\bin\env py3
import os,sys
import codecs
import re
import shutil

class ldbMod(object):
  """docstring for ldbMod"""
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    os.system('chcp 65001')
    self.pattern = re.compile('[\!\:\,\.\?\;\(\)]')
    print(self.pattern)
    if not os.path.exists(options['output']):
      os.mkdir(options['output']) 
    else:
      if input("%s exists. continue? (y/n)").lower() != 'y':
        logger.info("terminated!")
        exit(0)


  def removeSIL(self):
    fs = os.listdir(self.options['ldbs'])
    for f in fs:
      self.logger.info("Process: %s"%f)
      count = 0
      find_sil = False
      isPhrase = False
      LexNum = 0
      LexCount = 0
      keep_sil = False
      tmp_keep_sil = False
      fn = os.path.join(self.options['ldbs'], f)
      with codecs.open(fn,'r','utf-8') as fi:
        fo = open(os.path.join(self.options['output'], f), 'w', encoding='utf-8')
        for line in fi:
          line = line.strip('\n')
          if r"<LD_W_ORTH>" in line:
            text = re.search(' *<LD_W_ORTH> (.*) </LD_W_ORTH>', line).group(1)
            if re.search(self.pattern, text) is not None:
              tmp_keep_sil = True
            else:
              tmp_keep_sil = False
            tmpLexNum = len(text.split())

            
            isPhrase = False
            fo.write(line)
          elif r"<LD_W_TYPE>" in line:
            text = re.search(' *<LD_W_TYPE> (.*) </LD_W_TYPE>', line).group(1)
            if text == "WORD_PHRASE":
              isPhrase = True
              LexNum = tmpLexNum
            elif text == "WORD_DCT" or text == "WORD_CROSSTOKEN" or text == "WORD_SKIPCROSSTOKEN":
              isPhrase = False
              LexCount += 1
              if LexCount == LexNum:
                find_sil = True
            fo.write(line)
          elif isPhrase and r"<LD_W_SILDUR>" in line:
            LexCount = 0
            keep_sil = (True and tmp_keep_sil)
            text = re.search(' *<LD_W_SILDUR> (.*) </LD_W_SILDUR>', line).group(1)
            if keep_sil is False:
              print('find')
              sil_record = "0"
              fo.write("    <LD_W_SILDUR> 0 </LD_W_SILDUR>\n")
            else:
              sil_record = text
              keep_sil = False
              tmp_keep_sil = False
              fo.write(line)
          elif find_sil and r"<LD_W_SILDUR>" in line:
            find_sil = False
            fo.write("    <LD_W_SILDUR> %s </LD_W_SILDUR>\n"%sil_record)
            if sil_record == "0":
              print(sil_record)
          else:
            fo.write(line)

  def insertWeak(self):
    default_sil = '175'
    fs = os.listdir(self.options['ldbs'])
    for f in fs:
      self.logger.info("Process: %s"%f)
      count = 0
      find_sil = False
      isPhrase = False
      LexNum = 0
      LexCount = 0
      strong_sil = False
      tmp_strong_sil = False
      keep_sil = False
      fn = os.path.join(self.options['ldbs'], f)
      with codecs.open(fn,'r','utf-8') as fi:
        fo = open(os.path.join(self.options['output'], f), 'w', encoding='utf-8')
        for line in fi:
          line = line.strip('\n')
          if r"<LD_W_ORTH>" in line:
            text = re.search(' *<LD_W_ORTH> (.*) </LD_W_ORTH>', line).group(1)
            if re.search(self.pattern, text) is not None:
              tmp_strong_sil = True
            
            newLexNum = len(text.split())
            isPhrase = False
            fo.write(line)
          elif r"<LD_W_TYPE>" in line:
            text = re.search(' *<LD_W_TYPE> (.*) </LD_W_TYPE>', line).group(1)
            if text == "WORD_PHRASE":
              isPhrase = True
              LexCount = 0
              LexNum = newLexNum
              strong_sil = (True and tmp_strong_sil)
            elif text == "WORD_DCT" or text == "WORD_CROSSTOKEN" or text == "WORD_SKIPCROSSTOKEN":
              isPhrase = False
              LexCount += 1
              if LexCount == LexNum:
                find_sil = True              
            fo.write(line)
          elif isPhrase and r"<LD_W_SILDUR>" in line:
            text = re.search(' *<LD_W_SILDUR> (.*) </LD_W_SILDUR>', line).group(1)
            if strong_sil:
              sil_record = default_sil
              fo.write("    <LD_W_SILDUR> %s </LD_W_SILDUR>\n"%default_sil)
              strong_sil = False
              tmp_strong_sil = False
            elif int(text) == 0:
              sil_record = self.options['sil']
              fo.write("    <LD_W_SILDUR> %s </LD_W_SILDUR>\n"%sil_record)        
            else:
              sil_record = default_sil
              fo.write(line)
          elif find_sil and r"<LD_W_SILDUR>" in line:
            find_sil = False
            text = re.search(' *<LD_W_SILDUR> (.*) </LD_W_SILDUR>', line).group(1)
            fo.write("    <LD_W_SILDUR> %s </LD_W_SILDUR>\n"%sil_record)
          elif r"<LD_W_SILDUR>" in line:
            text = re.search(' *<LD_W_SILDUR> (.*) </LD_W_SILDUR>', line).group(1)
            if int(text) > 0:
              fo.write("    <LD_W_SILDUR> %s </LD_W_SILDUR>\n"%default_sil)
            else:
              fo.write(line)
          else:
            fo.write(line)

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='ldbMod')
  parser.add_argument("--version", action="version", version="ldbMod 1.0")
  parser.add_argument(type=str, action="store", dest="ldbs", default="", help='input ldb data directory')
  parser.add_argument("-o", "--output", action="store", dest="output", default="labs", help='output directory')
  parser.add_argument("-t", "--task", action="store", dest="task", default="insert_weak", help='insert_weak|remove_sil')
  parser.add_argument("-s", "--sil", action="store", dest="sil", default="0", help='insert_weak|remove_sil')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-ldbMod.txt', 'w')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = ldbMod(options, logger)
  if options["task"].lower() == "insert_weak":
    appInst.insertWeak()
  else:
    appInst.removeSIL()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))