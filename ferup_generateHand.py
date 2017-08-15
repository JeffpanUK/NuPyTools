'''
generateHand.py
combine corpus from pw and ws to generate format in handcraft
Author: Jeff Pan
Contact: junjie.pan@nuance.com
'''
#-*- coding:utf-8 -*-
#!usr/bin/env python3

import os
import sys
import codecs
import logging
class GenHand(object):
	'''
	generate handcraft class
	'''
	def __init__(self, basepath, outfile, logger):		
		self.basepath = basepath
		self.of = outfile
		self.cf = []
		self.logging = logger
		self.filecheck()
		
	def filecheck(self):
		pwfs = sorted(os.listdir(os.path.join(self.basepath,'pw')))
		wsfs = sorted(os.listdir(os.path.join(self.basepath,'ws')))
		missfs = []
		for f in wsfs:
			if f not in pwfs:
				missfs.append(f)
			else:
				self.cf.append(f)
		self.logging.info('Checking:\n\tword-seg files: %d\tprodosy files: %d\tmatched files:%d'%(len(wsfs),len(pwfs),len(self.cf)))
		if len(missfs)>0:
			self.logging.warning('no match word-seg files:')
			for f in missfs:
				self.logging.warning('%s'%f)
	
	def process(self):
		with codecs.open(self.of, 'w', 'utf-8') as fo:
			for f in self.cf:
				self.logging.info('Process: %s'%f)
				wsfn = os.path.join(self.basepath, 'ws',f)
				pwfn = os.path.join(self.basepath, 'pw',f)
				with codecs.open(wsfn, 'r', 'utf-8') as wsfi, codecs.open(pwfn, 'r', 'utf-8') as pwfi:				
					wslines = wsfi.readlines()
					pwlines = pwfi.readlines()
					for wsline, pwline in zip(wslines, pwlines):
	
						ws = wsline.strip().split()
						pw = pwline.strip().split()
						hand = []
						pos = 0
						for p in pw:
							plen = len(p)
							wlen = 0
							tmp = []
							wsp = ws[pos:]
							for idx, w in enumerate(wsp):
								wlen += len(w)
								tmp.append(w)
								pos+=1
								if plen == wlen:
									hand.append('-'.join(tmp))
									break
						fo.write('%s\n'%(' '.join(hand)))

						
if  __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser(description='generate handcraft file')
	parser.add_argument('--version', action='version', version='1.0')
	parser.add_argument('base',type=str)
	parser.add_argument('outfile',type=str)
	args = parser.parse_args()
	
	formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
	logger = logging.getLogger()
	
	file_handler = logging.FileHandler('log-GenHand.txt', 'w','utf-8')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(formatter)
	logger.addHandler(stream_handler)
	logger.setLevel(logging.INFO)
	
	handcraft = GenHand(args.base, args.outfile, logger)
	handcraft.process()
	
					
		
		
		
		
