import multiprocessing as mp
import time

def foo_pool(taskQ, x):
    print(x)
    taskQ.put(x)
    return x*x

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

def apply_async_with_callback():
    pool = mp.Pool()
    taskQ = mp.Queue(4)
    for i in range(10):
        pool.apply_async(foo_pool, args = (taskQ, i, ), callback = log_result)
    pool.close()
    pool.join()
    print(result_list)

if __name__ == '__main__':
    apply_async_with_callback()