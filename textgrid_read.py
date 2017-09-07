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
  def __init__(self, f):
    self.fn = f
    self.head = []
    self.items = {"文本":[], "汉字":[], "拼音":[], "音素":[], "半音素":[], "韵律边界":[], "句重音":[], "语言":[], "语气":[], "风格":[], "词重音":[]}

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

  def process(self):
    with open(fn, 'r', encoding='utf-8') as fi:
      lines = fi.readlines()
    self.head = lines[:8]
    lines = lines[8:]
    items = []
    idx = -1
    for line in lines:
      line = line.strip()
      if "item" in line:
        items.append(line)
        idx += 1
      else:
        line = line.split(" = ") if "intervals" not in line else line
        items[idx].append(line)
    
    end = 0
    prm = [0]
    sil_phone = []
    for item in items:
      name = re.sub('"', "", item[1][1])
      name = self.name_convert(name)
      item[1][0] = '"%s"'%name
      #conver all stress > 0  to 1
      if name == "词重音":
        sil_count = 0
        for idx, i in enumerate(item):
          if i[0] == "text":
            if item[idx-2][1] >= sil_phone[sil_count][0] or item[idx-1][1] <= sil_phone[sil_count][1]:
              sil_count += 1
              item[idx][1] = '"None"'
            elif i[1] == '""' or i[1] == '"0"':
              item[idx][1] = '"0"'
            else:
              item[idx][1] = '"1"'
        self.items[name] = item
      elif name == "汉字":
        self.items[name] = item
        for idx, i in enumerate(item):
          if i[0] == 'text' and i[1] in ['sil','None']:
            sil_phone.append([item[idx-2][1], item[idx-1][1]])
      # remove all tone in phoneme
      elif name == "音素":
        for i in item:
          if i[0] == "text":
            i[1] = re.sub("[0-9]", "", i[1])
        self.items[name] = item
      # record prosody bondary for prm
      elif name == "韵律边界":
        self.items[name] = item
        for i in item:
          if i[0] == time:
            prm.append(i[1])
        prm.append(end)
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
        vprm[vprm_count] = max(vprm[vprm_count], item[1]) if item[1] != '"None"' else '"None"'
    assert(vprm_count == len(vprm)-1)

    self.items['句重音'] = [['class','IntervalTier'],['name','句重音'],['xmin',0],['xmax',end],['intervals: size', len(prm)-1]]
    for idx, p in enumerate(prm[:-1]):
      self.items['句重音'].append('itervals [%d]:'%idx+1)
      self.items['句重音'].append(['xmin',p])
      self.items['句重音'].append(['xmax',prm[idx+1]])
      if vprm[idx] == '"None"':
        self.items['句重音'].append(['text',vprm[idx]])
      elif vprm[idx] > 0:
        self.items['句重音'].append(['text','1'])
      else:
        self.items['句重音'].append(['text','0'])

    self.items['语言'] = [['class','IntervalTier'],['name','语言'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
    self.items['语气'] = [['class','IntervalTier'],['name','语气'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
    self.items['风格'] = [['class','IntervalTier'],['name','风格'],['xmin',0],['xmax',end],['intervals: size', len(sil_phone)*2-1]]
    
    for idx, i in enumerate(sil_phone):
      self.items['语言'].append('itervals [%d]:'%idx+1)
      self.items['语气'].append('itervals [%d]:'%idx+1)
      self.items['风格'].append('itervals [%d]:'%idx+1)

      self.items['语言'].append(['xmin',i[0]])
      self.items['语气'].append(['xmin',i[0]])
      self.items['风格'].append(['xmin',i[0]])

      self.items['语言'].append(['xmax',i[1]])
      self.items['语气'].append(['xmax',i[1]])
      self.items['风格'].append(['xmax',i[1]])

      self.items['语言'].append(['text','"None"'])
      self.items['语气'].append(['text','"None"'])
      self.items['风格'].append(['text','"None"'])




