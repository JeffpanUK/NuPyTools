'''
	This script is used to operate unicode characters
	
	Created by Mei Xiao? Kenneth?
'''
import re
import codecs
class UnicodeOps(object):

	def __init__(self,logger,puncfname):
		self.logger = logger
		self.puncfname = puncfname
		self.logger.debug("Unicode Operation Init...")
		self.puncs = None

	def getAllPuncs(self):
		'''
			full set of puncs, Notice:return a set
		'''

		if self.puncs != None:
			return list(self.puncs.keys())

		f = codecs.open(self.puncfname,"r",encoding='utf8')
		self.puncs={}
		for line in f:
			line = line.strip()
			lineA = re.split("[ \t]+",line)
			if lineA[0] in self.puncs:
				self.logger.error("Duplicated puncs:%s,IGNORE!" % lineA[0])
			else:
				self.puncs[lineA[0]] = lineA[2]
		f.close()
		self.logger.debug("There are %d puncs in file" % len(self.puncs))
		return list(self.puncs.keys())

	def getPuncMap(self):
		if self.puncs == None:
			self.getAllPuncs()
		return self.puncs


	def getSentenceDelimiter(self):
		return ['\u3002','\uff01','\uff1f']   #see http://www.unicode.org/charts/PDF/U3000.pdf,http://www.unicode.org/charts/PDF/UFF00.pdf

	def getSentenceDefaultDelimiter(self):
		return '\u3002'

	def getSkipCodes(self):
		return re.compile(r"[\r\n]")

	def getAlphabets(self):
		'''
			full width & half width alphabets
		'''
		return re.compile(r"([a-zA-Z\uFF21-\uFF3A\uFF41-\uFF5A]+)")

	def getNumbers(self):
		'''
			full width & half width Numbers
		'''
		return re.compile(r"([0-9\uFF10-\uFF19]+)")

	def getMNC(self):
		'''
			get Chinese Characters, we use 4E00 - 9FA5 now, and it can be extended easily in this function
			see http://www.unicode.org/charts/PDF/U4E00.pdf
		'''
		return re.compile(r"([\u4E00-\u9FA5]+)")

	def isChinese(self, c):
		try:
			x = ord(c)
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
		
		#add more characters for SHC
		elif x == 0x20c8e:
		
			return True
		else:
			return False


