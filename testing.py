from readdata import readEdge, readNode, readPOI, generateOneQuery
import pickle
from cache import PathCache2, PathCache1
from multiprocessing import Process
import logging
import time

from datetime import datetime

t = datetime.now()

logging.basicConfig(
    filename='testing_log.txt',
    level=logging.INFO)

readNode()
readPOI()
readEdge()
pkl_file = open('path10000_20_25_34.storage', 'rb')
querypathlist = pickle.load(pkl_file)
print("Read %d path." % (len(querypathlist)))


def myTest(type,
           queryNum,
           capacity,
           cachepathNum):
    querylist = []
    for i in range(queryNum):
        query = generateOneQuery()
        querylist.append(query)
    print("Generate %d query." % queryNum)
    cacheset = querypathlist[:cachepathNum]
    if (type == 1):
        cache = PathCache1(capacity=capacity)
    else:
        cache = PathCache2(capacity=capacity)

    cache.PCCA(cacheset)
    print("type %d PCCA finished" % type)

    ts = time.time()
    hit_cout = cache.PCA(querylist)
    te = time.time()
    et = (te - ts) * 1000
    et+=100*(queryNum-hit_cout)

    msg = "#%d\t%d\t%d\t%d\t%.2f%%\t%2.2fms" % (type,cachepathNum, queryNum, capacity, hit_cout*100.0/queryNum, et * 1.0 / queryNum)

    logging.info(msg)
    print(msg)

if (__name__ == "__main__"):

    logging.info("type\tcachepathNum\tqueryNum\tcapacity\thit_rate\ttime_per_request")

    logging.info("=" * 15 + "queryNum" + "=" * 15)
    capacity = 50000
    cachePathNum =10000
    for queryNum in range(1000,5500,500):
        test1 = Process(target=myTest, args=(1, queryNum, capacity, cachePathNum))
        test2 = Process(target=myTest, args=(2, queryNum, capacity, cachePathNum))
        test1.start()
        test2.start()
        test2.join()
        test1.join()
    #
    logging.info("=" * 15 + "cache size" + "=" * 15)
    queryNum = 3000
    cachePathNum =10000
    for capacity in range(10000,55000,5000):
        test1 = Process(target=myTest, args=(1, queryNum, capacity, cachePathNum))
        test2 = Process(target=myTest, args=(2, queryNum, capacity, cachePathNum))
        test1.start()
        test2.start()
        test1.join()
        test2.join()
    #
    logging.info("=" * 15 + "cache path num" + "=" * 15)
    capacity = 50000
    queryNum = 3000
    for cachePathNum in range(5000,11000,1000):
        test1 = Process(target=myTest, args=(1, queryNum, capacity, cachePathNum))
        test2 = Process(target=myTest, args=(2, queryNum, capacity, cachePathNum))
        test1.start()
        test2.start()
        test2.join()
        test1.join()
    
    #
    #
