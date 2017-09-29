#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: parseTextGrid.py
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-09-22 10:35:22
 ============================
'''

class TGPARSER(object):
    """docstring for TGPARSER"""
    def __init__(self, tg, logger):
        os.system("chcp 65001")
        self.tg = tg
        self.logger = logger
        self.items = {"文本":{}, "汉字":{}, "拼音":{}, "音素":{}, "半音素":{}, "韵律边界":{}, "句重音":{}, "语言":{}, "语气":{}, "风格":{}, "词重音":{}}
        for item in self.items.keys():
            self.items[item]["class"] = ""
            self.items[item]["bnd"] = []
            self.items[item]["intervals"] = []
            self.items[item]["points"] = []

    def get_line_value(self, line):
        return re.sub('"','',line.strip().split(" = ")[1])

    def  process(self):
        try:
            with open(self.tg, 'r', encoding='utf-8') as fi:
                self.logger.info("Process: %s"%self.tg)
                f = fi.readlines()
            line_text = f[0]
            idx = 0
            while "item" not in line_text:
                idx += 1
                line_text = f[idx]
            f = f[idx+1:]
            class_name = ""
            intv_flag = False
            poin_flag = False
            spec_idx = -1
            for idx, line in enumerate(f):
                if "item" in line:
                    intv_flag = False
                    poin_flag = False
                    spec_idx = -1
                elif "name" in line:
                    class_name = self.get_line_value(line)
                    self.items[class_name]["class"] = self.get_line_value(f[idx-1])
                elif not intv_flag and not poin_flag and ("xmin" in line or "xmax" in line):
                    self.items[class_name]["bnd"].append(self.get_line_value(line))
                elif "intervals" in line and "size" not in line:
                    intv_flag = True
                    spec_idx += 1
                    self.items[class_name]["intervals"].append([])
                elif intv_flag:
                    self.items[class_name]["intervals"][spec_idx].append(self.get_line_value(line))
                elif "points" in line and "size" not in line:
                    poin_flag = True
                    spec_idx += 1
                    self.items[class_name]["points"].append([])
                elif poin_flag:
                    self.items[class_name]["points"][spec_idx].append(self.get_line_value(line))
                else:
                    pass
        except Exception as e:
            self.logger.error(e)
            return -1
        return 0



