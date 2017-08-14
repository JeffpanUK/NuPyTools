import os
import sys
from Npp import notepad

filePathSrc=r"D:\Documents\PRM\selected-tiantian\mlf"
for dir,dirs,files in os.walk(filePathSrc):
for fn in files:
if fn.endswith(".mlf"):
notepad.open(os.path.join(dir,fn))
notepad.runMenuCommand("Encoding","Convert to UTF-8 without BOM")