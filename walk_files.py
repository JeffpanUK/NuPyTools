#-*- coding:utf-8 -*-
#!\usr\bin\env py3

import os
import re
import sys
import numpy as np
import pdb
"""
Program: walk_files.py
Function: walk all files to check their modified date
Author: Junjie Pan (junjie.pan@nuance.com)
"""

class WalkThrough(object):
    '''
    '''
    def __init__(self, options, logger):
        self.logger = logger
        self.options = options
        self.count = 0
        if np.array(options.values()).all() == "":
                self.usage()
                exit(-1)
        self.fo = open(self.options['output'], 'w', encoding='utf-8')
        self.fo.write("===================================================\nCreated Time: %s -> %s\n===================================================n"%(self.options["start"], self.options["end"]))

        
    def process(self, root):
        format = "%Y-%m-%d %H:%M:%S"
        th_time = time.mktime(time.strptime(self.options["start"], format))
        ed_time = time.mktime(time.strptime(self.options["end"], format))

        for parent, dirnames, filenames in os.walk(root):
            for dirname in dirnames:
                if dirname == "..":
                    continue
                self.process(os.path.join(parent, dirname))
            for filename in filenames:
                mtime = os.path.getmtime(os.path.join(parent, filename))
                if mtime >= th_time and mtime <= ed_time:
                    self.count += 1
                    self.logger.info("[%d] %s"%(self.count, os.path.join(os.path.abspath(parent), filename)))
                    self.fo.write("[%d] %s\n"%(self.count, os.path.join(os.path.abspath(parent), filename)))

    def usage(self):
        self.logger.error('''Usage Example:\nwalk_files.py -s "2017-1-1 12:12:12" -e "2018-1-1 12:12:12" -r root_dir''')
                
        

if __name__ == '__main__':
    import time
    import logging
    from argparse import ArgumentParser

    parser = ArgumentParser(description='walk_files')
    parser.add_argument("--version", action="version", version="walk_files 1.0")
    parser.add_argument("-s", "--start", action="store", dest="start", default="", help='modified time.')
    parser.add_argument("-e", "--end", action="store", dest="end", default="", help='modified time.')
    parser.add_argument("-r", "--root", action="store", dest="root", default=r"", help='root path.')
    parser.add_argument("-o", "--output", action="store", dest="output", default=r"output.txt", help='root path.')

    args = parser.parse_args()
    options = vars(args)

    logger = logging.getLogger()
    formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*] - %(message)s', '%Y%m%d-%H:%M:%S')
    file_handler = logging.FileHandler('LOG-walk_files.txt', 'w','utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    allStartTP = time.time()
    appInst = WalkThrough(options, logger)
    appInst.process(options["root"])
    allEndTP = time.time()
    logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))