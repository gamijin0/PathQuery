from readdata import readEdge,readNode,readPOI,generateOneQuery
import pickle
from cache2 import PathCache2


if(__name__=="__main__"):
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
    cacheset = querypathlist[:10000]


    cache2 = PathCache2(capacity=10000)
    cache2.PCCA(cacheset)
    print("Cache2 cache %d path." % (len(cacheset)))
    #
    res2 = cache2.PCA(querylist)
    print("PCA2 return %d answer." % (len(res2)))
