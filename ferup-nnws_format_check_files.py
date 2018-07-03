#!/usr/bin/env py3
from __future__ import division, print_function, absolute_import

import os
import sys
import re
import numpy as np

import pdb

'''
 ============================
 @FileName: ferup-nnws_format_check_files.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2018-07-03 10:51:07
 ============================
'''

def main(file_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    fs = os.listdir(file_dir)
    count = 0
    for f in fs:
        fn = os.path.join(file_dir, f)
        with open(fn, "r", encoding='utf-8') as fi:
            fon = os.path.join(output_dir, f)
            with open(fon, "w", encoding='utf-8') as fo:
                for line in fi:
                    if re.match("Lexicon", line)!= None:
                        count+=1
                        line = line[len("Lexicon:"):]
                        pattern_pos = re.compile(r"/.*?([ \n])")
                        pattern_eng = re.compile(r"[a-zA-Z].*?([ \n])")
                        pattern_num = re.compile(r"[0-9]+([ \n])")
                        pattern_multi_space = re.compile(r"[ \t]+")

                        line = re.sub(pattern_pos, r"\1", line)
                        line = re.sub(pattern_eng, r"ENG\1", line)
                        line = re.sub(pattern_num, r"NUM\1", line)
                        line = re.sub(pattern_multi_space, r" ", line)
                        fo.write(line)
    print("total line: %d"%count)

if __name__ == '__main__':
    file_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(file_dir, output_dir)


