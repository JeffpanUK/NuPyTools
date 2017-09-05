#-*-coding:utf-8-*-
#!\usr\bin\env py3

import os
import sys

"""
Program: file_tree_generator.py
Function: walk all files to generate file tree
Author: Junjie Pan (kevinjjp@gmail.com)
"""

class FileTree(object):
  """docstring self.for FileTree"""
  def __init__(self, options, logger):
    self.options = options
    self.logger = logger
    self.brkstr = []
    self.spec = [1, 0, 0]

  def process(self):
    root = os.path.basename(self.options['rootdir'])
    fn = self.options['output']+"-%s.txt"%root
    with open(fn, 'w', encoding='utf-8') as fo:
      self.printDirTree(self.options['rootdir'], 0, self.brkstr, 0)
      if self.options['spec']:
        fo.write("+---------Sepcific Info-----------+\n")
        head = ['depth', 'folders', 'files']
        refStr = "+---------------------------------+"
        for i,j in zip(head, self.spec):
          tmpStr = "| %s: %s"%(i,j)

          fo.write("| %s: %s%s|\n"%(i,j," "*(len(refStr)-len(tmpStr)-1)))
        fo.write("%s\n\n"%refStr)
      fo.write("".join(self.brkstr))
      self.logger.info("Generate %s sucessfully!"%fn)
    



  def printDirTree(self, rootdir, indent, brkstr, skip_indent, last=False):
    if not os.path.isdir(rootdir):
      selg.logger.error("%s is not a directory"%rootdir)
    else:
      self.spec[1] += 1
      brkstr.append(self.getIndentString(indent, skip_indent*last))
      if indent > 1:
        brkstr.append(" ")
      if indent != 0:
        if last:
          self.spec[0] += 1
          brkstr.append("└── ")
        else:
          brkstr.append("├── ")
      brkstr.append(os.path.basename(rootdir))
      brkstr.append("/")
      brkstr.append("\n")
      subfiles = os.listdir(rootdir)
      for idx, sub in enumerate(subfiles):
        subn = os.path.join(rootdir, sub)
        if idx == len(subfiles) - 1:
          last = True
          skip_indent += 1
        if os.path.isdir(subn):
          self.printDirTree(subn, indent+1, brkstr, skip_indent, last)
        else:
          self.printFile(sub, indent+1, brkstr, skip_indent, last)

  def printFile(self, file, indent, brkstr, skip_indent, last=False):
    self.spec[2] += 1
    brkstr.append(self.getIndentString(indent, skip_indent*last))
    if indent > 1:
        brkstr.append(" ")
    if last:
        brkstr.append("└── ")
    else:
        brkstr.append("├── ")
    brkstr.append(file)
    brkstr.append('\n')

  def getIndentString(self, indent, skip_indent):
    if indent == 0 :
      return ""
    brkstr = ""
    for i in range(indent-1):
      if indent-i <= skip_indent:
        brkstr+=("   ")
      else:
        brkstr+="%s│  "%(" "*(i!=0))

    return brkstr

if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser

  parser = ArgumentParser(description='file_tree_generator')
  parser.add_argument("--version", action="version", version="file_tree_generator 1.0")
  parser.add_argument(type=str, action="store", dest="rootdir", default=".", help='rootdir path')
  parser.add_argument("-o", "--output", action="store", dest="output", default=r"filetree", help='output path.')
  parser.add_argument("-s", "--spec", action="store", dest="spec", default=True, help='show specific info')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-file_tree_generator.txt', 'w','utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = FileTree(options, logger)
  appInst.process()
  # appInst.self.formatCheck()
  allEndTP = time.time()
  logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))       