import hashlib
import math
from rtree import index
import pickle
import time
import networkx as nx
import sys
from readdata import readNode, readEdge, readPOI, generateOneQuery, CloudBaseQuery
from cache2 import PathCache1


if(__name__=='__main__'):



    readNode()
    readPOI()
    readEdge()

    querylist = []
    queryNum = 1000
    for i in range(queryNum):
        query = generateOneQuery()
        querylist.append(query)
    print("Generate %d query." % queryNum)

    pkl_file = open('path10000_20_25_34.storage', 'rb')
    querypathlist = pickle.load(pkl_file)
    print("Read %d path." % (len(querypathlist)))
    cacheset = querypathlist[:1500]


    cache1 = PathCache1(capacity=200000)

    cache1.PCCA(cacheset)
    cache1.PCA(querylist)

