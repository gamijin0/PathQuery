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


def myTest(type: int = 1,
           queryNum=500,
           capacity=10000,
           cachepathNum=10000):
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

    ts = time.time()
    hit_rate = cache.PCA(querylist)
    te = time.time()
    et = (te - ts) * 1000

    msg = "#%d\t%d\t%d\t%.2f%%\t%2.2fms" % (type, queryNum, capacity, hit_rate, et * 1.0 / queryNum)

    logging.info(msg)


if (__name__ == "__main__"):

    processPool = []

    for queryNum in [10000, ]:
        for capacity in [50000, 90000]:
            test1 = Process(target=myTest, args=(1, queryNum, capacity, 200))
            test2 = Process(target=myTest, args=(2, queryNum, capacity, 200))

            test1.start()
            test2.start()

            processPool.append(test1)
            processPool.append(test2)

    for p in processPool:
        p.join()
