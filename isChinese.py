#-*-encoding:utf-8-*-
#!/usr/bin/env py3
import os
import sys
import re

'''
 ============================
 @FileName: isChinese
 @Author:   Jeff Pan (kevinjjp@gmail.com)
 @Version:  1.0 
 @DateTime: 2017-11-02 14:25:35
 ============================
'''
class isChinese(object):
    """docstring for isChinese"""
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger

    def isChinese(self, c):
        try:
            x = ord (c)
        except:
            return False

        # CJK Unified Ideographs
        if x >= 0x4e00 and x <= 0x9fbb:
            return True

        # CJK Compatibility Ideographs
        elif x >= 0xf900 and x <= 0xfad9:
            return True

        # CJK Unified Ideographs Extension A
        elif x >= 0x3400 and x <= 0x4dbf:
            return True

        # CJK Unified Ideographs Extension B
        elif x >= 0x20000 and x <= 0x2a6d6:
            return True

        # CJK Unified Ideographs Extension C+D+E
        elif x >= 0x2a700 and x <= 0x2ceaf:
            return True

        # CJK Compatibility Supplement
        elif x >= 0x2f800 and x <= 0x2fa1d:
            return True
        else:
            return False