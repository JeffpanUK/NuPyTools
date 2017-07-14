#-*-coding:utf-8-*-
#!\usr\bin\env py3

import os
import sys
import re
import codecs
import multiprocessing
import logging
import logging.handlers
import time
findLists = []

class QueueHandler(logging.Handler):
  """
  This is a logging handler which sends events to a multiprocessing queue.
  """
  def __init__(self, queue):
    """
    Initialise an instance, using the passed queue.
    """
    logging.Handler.__init__(self)
    self.queue = queue
      
  def emit(self, record):
    """
    Emit a record.
    Writes the LogRecord to the queue.
    """
    try:
      ei = record.exc_info
      if ei:
        dummy = self.format(record) # just to get traceback text into record.exc_text
        record.exc_info = None  # not needed any more
      self.queue.put_nowait(record)
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      self.handleError(record)



class SelectWord(object):
  '''
  select unseen word from corpus according to a given dictionary
  '''
  
  def __init__(self, options, logger):
    self.logger = logger
    self.options = options
    self.wlist = set([])
    self.dict = self.wordlist(self.options['dict'])
    self.base = self.options['corpus']
    self.fs = os.listdir(self.base)  
    self.puncs = self.loadPuncs(options['punc'])
    self.outfile = options['outfile']
    self.logger.info('initialization finished.')
    
  def loadPuncs(self, puncf):
    try:
      with codecs.open(puncf, 'r', 'utf-8') as punch:
        punc = set([])
        for line in punch:
          punc.add(line.strip().split()[0])
      punc = list(punc)
      rp = list(map(lambda x: '\\'+x, punc))
      rp = '[' + ''.join(rp) + ']'
      return re.compile(rp)
    except Exception as e:
      self.logger.error(e)
    
  def wordlist(self, dic):
    try:    
      with codecs.open(dic, 'r', 'utf-8') as fd:
        for line in fd:
          f = line.strip().split(r'|')[0]
          self.wlist.add(f)         
    except Exception as e:
      self.logger.error(e)
  
  def writeFile(self, nwords):
    try:
      with codecs.open(self.outfile, 'w', 'utf-8') as fo:
        for w in nwords:
          fo.write('%s\n'%w)
    except Exception as e:
      self.logger.error(e)
    
  def process(self):
    logQ = multiprocessing.Queue(-1)
    taskQ = multiprocessing.Queue(-1)
    listQ = multiprocessing.Queue(-1)
    # taskP = multiprocessing.Pool()
    # procP = multiprocessing.Pool()
    logR=[]
    taskR=[]
    resultR = []
    
    listener = multiprocessing.Process(target=SelectWord.listener_process, 
                                       args=(logQ, SelectWord.listener_configurer))
    listener.start()
    
    for f in self.fs:
      worker = multiprocessing.Process(target=SelectWord.putQ, 
                                        args=(taskQ,
                                        os.path.join(self.base, f),
                                        logQ, 
                                        SelectWord.worker_configure
                                        )
                                      )
      taskR.append(worker)
      worker.start()

    for i, f in enumerate(self.fs):
      f = os.path.join(self.base, f)
      worker = multiprocessing.Process(target=SelectWord.subProcess, 
                                       args=(taskQ, 
                                          self.puncs, 
                                          self.wlist, 
                                          logQ, 
                                          SelectWord.worker_configure,
                                          listQ
                                          )
                                      )
      
      # worker = multiprocessing.Process(target=SelectWord.subProcess, args=(taskQ, self.puncs, self.wlist))
      resultR.append(worker)
      worker.start()
    for i in taskR:
      i.join()
    taskQ.close()
    for i in resultR:
      i.join()
    # procP.close()
    # procP.join()
    logQ.put_nowait(None)
    listener.join()
    result_list = set([])
    
    for _ in range(len(self.fs)):
      findList = listQ.get_nowait()
      result_list = result_list.union(findList)
    

    with codecs.open(self.outfile, 'w', 'utf-8') as fo:
      for w in list(result_list):
        self.logger.info("Find word: %s"%w)
        fo.write("%s\n"%w)


  @classmethod
  def worker_configure(cls, queue):
    h = QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)
  
  @classmethod
  def subProcess(cls, taskQ, puncs, wlist, logQ, configurer, listQ):
    f = taskQ.get()
    configurer(logQ)
    logger = logging.getLogger()
    logger.info('Processing:%s'%f)
    with codecs.open(f, 'r', 'utf-8') as fn:
      nwlist = set([])
      for line in fn:
        line = re.sub(puncs, ' ',line)
        line = line.strip().split()
        for w in line:
          if re.search('[a-za-z0-9]', w) is None and w not in wlist:
            nwlist.add(w)
    listQ.put(nwlist)
    logger.info("complete: %s"%f)
  
  @classmethod
  def putQ(cls, queue, f, logQ, configurer):
    configurer(logQ)
    logger = logging.getLogger()
    logger.info('Queuing: %s'%f)
    queue.put(f)
  
  @classmethod
  def listener_configurer(cls):
    root = logging.getLogger()
    # h = logging.handlers.RotatingFileHandler('LOG-selectWord_sub.txt', 'a', 300, 10)
    f = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
    # h.setFormatter(f)
    # root.addHandler(h)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(f)
    root.addHandler(stream_handler)
    
  @classmethod
  def listener_process(cls, logQ, configurer):
    configurer()
    while True:
      try:
        record = logQ.get()
        if record is None: # We send this as a sentinel to tell the listener to quit.
            break
        logger = logging.getLogger(record.name)
        logger.handle(record) # No level or filter logic applied - just do it!
      except (KeyboardInterrupt, SystemExit):
        raise
      except:
        import sys, traceback
        print >> sys.stderr, 'Whoops! Problem:'
        traceback.print_exc(file=sys.stderr)



if __name__ == '__main__':
  import time
  import logging
  from argparse import ArgumentParser
  
  parser = ArgumentParser(description='selectWord')
  parser.add_argument("--version", action="version", version="selectWord 1.0")
  parser.add_argument(action="store", dest="corpus", default="", help='input corpus direcotry')
  parser.add_argument(action="store", dest="outfile", default="newword.wlist", help='new word list')
  parser.add_argument("-d", "--dict", action="store", dest="dict", default="", help='dictionary')
  parser.add_argument("-p", "--punc", action="store", dest="punc", default="puncs.list", help='punctuation lists')

  args = parser.parse_args()
  options = vars(args)

  logger = logging.getLogger()
  formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
  file_handler = logging.FileHandler('LOG-selectWord.txt', 'w',encoding='utf-8')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)

  allStartTP = time.time()
  appInst = SelectWord(options, logger)
  appInst.process()
  allEndTP = time.time()