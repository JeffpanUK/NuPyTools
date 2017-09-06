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

    for item in items:
      name = re.sub('"', "", item[1][1])
      name = self.name_convert(name)
      item[1][0] = '"%s"'%name
      #conver all stress > 0  to 1
      if name == "词重音":
        for i in item:
          if i[0] == "text":
            if i[1] == '""' or i[1] == '"0"':
              i[1] = '"0"'
            else:
              i[1] = '"1"'
        self.items[name] = item
      # remove all tone in phoneme
      elif name == "音素":
        for i in item:
          if i[0] == "text":
            i[1] = re.sub("[0-9]", "", i[1])
        self.items[name] = item
      # record prosody bondary for prm
      elif name == "韵律边界":
        pass
      elif name == "skip":
        end = item[-2][1]
      else:
        self.items[name] = item




