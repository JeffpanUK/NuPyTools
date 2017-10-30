#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: extract_shc_stress
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-10-27 11:20:11
 ============================
'''

class ExtractStress(object):
    """docstring for ExtractStress"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.punc = self.load_punc(options['puncf'])

    #load punctuation file
    def load_punc(self, puncf):
        punc = []
        with open(puncf, 'r', encoding='utf-8') as fi:
            for line in fi:
                line = line.strip().split()
                punc.extend(line)
        return list(set(punc))

    # return cleaned sentence
    def cleanup(self, f):
        cleaned_lines = []
        with open(f, 'r', encoding='utf-8') as fi:
            for line in fi:
                cleaned_line = ""
                line = line.strip()
                for char in line:
                    if char == "'":
                        cleaned_line += char
                    if char == "\+":
                        cleaned_line += ""
                    elif char == "-":
                        cleaned_line += ""
                    elif char in self.punc:
                        cleaned_line += " "
                    else:
                        cleaned_line += char
                cleaned_lines.append(cleaned_line)
        return cleaned_lines

    def  process(self, fpath):
        strs = []
        pws =[]
        fs = os.listdir(fpath)
        for f in fs:
            fn = os.path.join(fpath, f)
            with open(fn, 'r', encoding='utf-8') as fi:
                cleaned_lines = self.cleanup(fi)
                for line in cleaned_lines:
                    line = line.split()
                    for pw in line:
                        stress = []
                        for ch in pw:
                            if stress_flag:
                                stress_flag = False
                                continue
                            if ch == r"'":
                                stress.append(1)
                                stress_flag = True
                            else:
                                stress.append(0)
                        strs.append(stress)
                        pws.append(re.sub("'","",pw))
        return pws, strs

