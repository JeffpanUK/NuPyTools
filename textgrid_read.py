#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: textgrid_read.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-09-04 13:16:08
 ============================
'''

class TextgridReader(object):
  """docstring for TextgridReader"""
  def __init__(self, f, fout, reset=False):
    self.fn = f
    self.fout = fout
    self.reset = reset
    self.head = []
    self.items = {"文本":[], "汉字":[], "拼音":[], "音素":[], "半音素":[], "韵律边界":[], "句重音":[], "语言":[], "语气":[], "风格":[], "词重音":[]}
    self.names = ["文本", "汉字", "拼音", "音素", "半音素", "韵律边界", "句重音", "语言", "语气", "风格", "词重音"]

  def name_convert(self, name):
    if name.lower() == "sentence":
      return "文本"
    elif name.lower() == "hz":
      return "汉字"
    elif name.lower() == 'stress':
      return "词重音"
    elif name.lower() == "pinyin":
      return "拼音"
    elif name.lower() == "cv":
      return "skip"
    elif name.lower() == "phoneme":
      return "音素"
    elif name.lower() == "demi-phone":
      return "半音素"
    elif name.lower() == "prosody":
      return "韵律边界"
    else:
      return "remove"

  def writeTG(self):
    with open(self.fout, 'w', encoding='utf-8') as fo:
      fo.write("".join(self.head))
      for idx, name in enumerate(self.names):
        item = self.items[name]
        fo.write("    item [%d]:\n"%(idx+1))
        indent = 2
        subitem = False
        for line in item:
          if isinstance(line, list):
            if subitem:
              indent = 3
            fo.write("    "*indent)
            fo.write(" = ".join(list(map(lambda x: str(x), line))))
          else:
            indent = 2
            fo.write("    "*indent)
            fo.write(line)
            subitem = True
          fo.write("\n")

  def process(self):
    try:
      with open(self.fn, 'r', encoding='utf-8') as fi:
        lines = fi.readlines()
    
      self.head = lines[:8]
      self.head[6] = "size = 11\n"
      lines = lines[8:]
      items = []
      idx = -1
      for line in lines:
        line = line.strip()
        if "item" in line:
          idx += 1
          items.append([])
        else:
          line = line.split(" = ") if "intervals" not in line else line
          items[idx].append(line)
      
      end = 0
      prm = [0]
      pw = []
      sil_phone = []
      level3 = []
      for item in items:
        name = re.sub('"', "", item[1][1])
        name = self.name_convert(name)
        item[1][1] = '"%s"'%name
        #conver all stress > 0  to 1
        if name == "词重音":
          sil_count = 0
          for idx, i in enumerate(item):
            if i[0] == "text":
              if item[idx-2][1] >= sil_phone[sil_count][0] and item[idx-1][1] <= sil_phone[sil_count][1]:
                sil_count += 1
                item[idx][1] = '"None"'
              elif i[1] == '""' or i[1] == '"0"' or self.reset:
                item[idx][1] = '"0"'
              else:
                item[idx][1] = '"1"'
              pw.append(item[idx-1][1])
          self.items[name] = item
        elif name == "汉字":
          self.items[name] = item
          for idx, i in enumerate(item):
            if i[0] == 'text':
              if i[1] in ['"sil"','"sp"']:
                sil_phone.append([item[idx-2][1], item[idx-1][1],'None'])
                level3.append(item[idx-2][1])
                level3.append(item[idx-1][1])
        # remove all tone in phoneme
        elif name == "音素":
          for i in item:
            if i[0] == "text":
              i[1] = re.sub("[0-9]", "", i[1])
          self.items[name] = item
        # record prosody bondary for prm
        elif name == "韵律边界":
          for i in item:
            if i[0] == 'time':
              prm.append(i[1])
          prm.append(end)

          self.items[name] = item[:4]
          self.items[name].append(["points: size", len(pw)-1])
          pwbnd = {}
          final_pw = []
          # print(item)
          for idx, rd in enumerate(item): 
            if rd[0] == 'time':
              pwbnd[rd[1]] = item[idx+1][1]
          for  p in pw[:-1]:
            if p in level3[2:-2]:
              final_pw.append([p, '"3"'])
            elif p in pwbnd.keys():
              final_pw.append([p, pwbnd[p]])
            else:
              final_pw.append([p, '"0"'])
          for idx, i in  enumerate(final_pw):
            self.items[name].append("points [%d]:"%(idx+1))
            self.items[name].append(['time', i[0]])
            self.items[name].append(['mark', i[1]])


        elif name == "skip":
          end = item[-2][1]
        else:
          self.items[name] = item


      vprm = [0 for _ in prm[:-1]]
      vprm_count = 0
      for idx, item in enumerate(self.items['词重音']):
        if item[0] == 'text':
          if self.items['词重音'][idx-1][1] > prm[vprm_count+1]:
            vprm_count += 1
          tmp = int(re.sub('"','',item[1])) if "None" not in item[1] else 0
          
          vprm[vprm_count] = max(vprm[vprm_count], tmp) if item[1] != '"None"' else '"None"'
          if self.reset:
            vprm[vprm_count] = 0 if item[1] != '"None"' else '"None"'
      assert(vprm_count == len(vprm)-1)

      self.items['句重音'] = [['class','"IntervalTier"'],['name','"句重音"'],['xmin',0],['xmax',end],['intervals: size', len(prm)-1]]
      for idx, p in enumerate(prm[:-1]):
        self.items['句重音'].append('itervals [%d]:'%(idx+1))
        self.items['句重音'].append(['xmin',p])
        self.items['句重音'].append(['xmax',prm[(idx+1)]])
        if idx == 0 or idx == len(prm[:-1])-1:
          self.items['句重音'].append(['text','"None"'])
        elif vprm[idx] == '"None"':
          # self.items['句重音'].append(['text','"None"'])
          self.items['句重音'].append(['text','%s'%vprm[idx]])
        elif vprm[idx] > 0:
          self.items['句重音'].append(['text','"1"'])
        else:
          self.items['句重音'].append(['text','"0"'])
      self.items['语言'] = [['class','"IntervalTier"'],['name','"语言"'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
      self.items['语气'] = [['class','"IntervalTier"'],['name','"语气"'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
      self.items['风格'] = [['class','"IntervalTier"'],['name','"风格"'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
      
      for idx, i in enumerate(sil_phone):
        index = (idx+1)*2-1
        self.items['语言'].append('itervals [%d]:'%index)
        self.items['语气'].append('itervals [%d]:'%index)
        self.items['风格'].append('itervals [%d]:'%index)

        self.items['语言'].append(['xmin',i[0]])
        self.items['语气'].append(['xmin',i[0]])
        self.items['风格'].append(['xmin',i[0]])

        self.items['语言'].append(['xmax',i[1]])
        self.items['语气'].append(['xmax',i[1]])
        self.items['风格'].append(['xmax',i[1]])

        self.items['语言'].append(['text','"None"'])
        self.items['语气'].append(['text','"None"'])
        self.items['风格'].append(['text','"None"'])

        if(idx<len(sil_phone)-1):
          index+=1
          self.items['语言'].append('itervals [%d]:'%index)
          self.items['语气'].append('itervals [%d]:'%index)
          self.items['风格'].append('itervals [%d]:'%index)

          self.items['语言'].append(['xmin',i[1]])
          self.items['语气'].append(['xmin',i[1]])
          self.items['风格'].append(['xmin',i[1]])

          self.items['语言'].append(['xmax',sil_phone[idx+1][1]])
          self.items['语气'].append(['xmax',sil_phone[idx+1][1]])
          self.items['风格'].append(['xmax',sil_phone[idx+1][1]])

          self.items['语言'].append(['text','"TC"'])
          self.items['语气'].append(['text','"TS"'])
          self.items['风格'].append(['text','"TN"'])

      self.writeTG()
    except:
      return -1
    return 0

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='textgrid_read.py')
  parser.add_argument("--version", action="version", version="textgrid_read.py 1.0")
  parser.add_argument("-i", "--input", action="store", dest="input", default="", help='accuracy files')
  parser.add_argument("-o", "--output", action="store", dest="output", default="", help='accuracy files')
  parser.add_argument("-r", "--reset", action="store", dest="reset", default=False, help='reset all prm and stress')


  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-textgrid_read.py.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  fs = os.listdir(options['input'])
  if not os.path.exists(options['output']):
    os.mkdir(options['output'])

  os.system('chcp 65001')
  correct = 0
  for f in fs:
    fn = os.path.join(options['input'], f)
    fo = os.path.join(options['output'],"%sTextGrid"%f[:-8])
    logger.info("Process: %s"%f)
    appInst = TextgridReader(fn, fo, options['reset'])
    if appInst.process()!=0:
      logger.info("FAILURE: %s"%f)
    else:
      correct+=1
  logger.info("Success %s/%s"%(correct,len(fs)+1))

  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))

