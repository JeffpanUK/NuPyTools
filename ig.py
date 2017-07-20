#!/usr/bin/env py3
# -*- coding: utf-8 -*-
__copyright__ = '''
Copyright 2017 Nuance Communications, Inc. All rights reserved.
Company confidential. Use is subject to license terms.'''
__author__ = 'Junjie(Jeff) Pan'

import os
import sys
import glob
import shutil
from os.path import lexists, basename, dirname, abspath, join


def build_igtree(tooldir, fn_in, _hex):
    fn_exe =  'Ig.exe'
    cmdline = "%s -f %s -a igtree -w *" % (fn_exe, fn_in)
    os.system(cmdline)
    input(" ")
    shutil.move("igtree.dat", '%s.dat'%_hex)
    shutil.move("igtree.map", '%s.map'%_hex)
    


def _main():
    tooldir = "."
    fpath = "."
    fs = os.listdir(fpath)
    fs = list(filter(lambda x: ".txt" in x, fs))
    for f in fs:
      fn = fs[:-4]
      print(fn)
      input(" ")
      if not os.path.exists('%s.dat'%fn) and not os.path.exists("%s.map"%fn):
        build_igtree(tooldir, os.path.join(fpath,f), fn)



if __name__ == '__main__':
    sys.exit(_main())
