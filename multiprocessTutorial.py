# Written by Vamei
import os
import multiprocessing
import time
#==================
# input worker
def inputQ(queue, info):
    # info = str(os.getpid()) + '(put):' + str(time.time())
    queue.put(info)

# output worker
def outputQ(queue,lock):
    info = queue.get()
    print(info)
    # lock.acquire()
    # print (str(os.getpid()) + '(get):' + info)
    # lock.release()
#===================
# Main
if __name__ == "__main__":
  record1 = []   # store input processes
  record2 = []   # store output processes
  lock  = multiprocessing.Lock()    # To prevent messy print
  queue = multiprocessing.Queue(3)
  a = range(10)
  # input processes
  for i in a:
      process = multiprocessing.Process(target=inputQ,args=(queue,i))
      process.start()
      record1.append(process)

  # output processes
  for i in range(10):
      process = multiprocessing.Process(target=outputQ,args=(queue,lock))
      process.start()
      record2.append(process)

  for p in record1:
      p.join()

  queue.close()  # No more object will come, close the queue

  for p in record2:
      p.join()