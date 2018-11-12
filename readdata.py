DATA_DIR = './data/'
import os
import random
import sys
import hashlib

sys.path.append(".")

from cache import Node, Path
import networkx as nx

POIList = []
EdgeDict = {}
NodeDict = {}
DijkstraGraph = None


def readPOI():
    count = 0
    with open(os.path.join(DATA_DIR,
                           "California's Points of Interest With Original Category Name (Category Name, Longitude, Latitude).txt"),
              mode='r',
              encoding='utf-8'
              ) as f:
        while True:
            line = f.readline()
            if not line:
                break
            try:
                cata, x, y = line.split(' ')
                nid = int(hashlib.sha256(str((x, y)).encode('utf-8')).hexdigest(), 16) % 10 ** 8
                count += 1
                POIList.append(Node(nid, x, y))
            except Exception as e:
                pass
        print("Read %d POIs." % count)


def readNode():
    count = 0
    with open(os.path.join(DATA_DIR, "California Road Network's Nodes (Node ID, Longitude, Latitude).txt"),
              mode='r',
              encoding='utf-8'
              ) as f:
        while True:
            line = f.readline()
            if not line:
                break
            try:
                nid, x, y = line.strip().split(' ')
                count += 1
                NodeDict[int(nid)] = Node(nid, x, y)
            except Exception as e:
                pass
        print("Read %d Nodes." % count)


def generateOneQuery():
    # origin, destation = random.sample(POIList, 2)
    nids = NodeDict.keys()
    startId, endId = random.sample(nids, 2)
    return NodeDict[startId], NodeDict[endId]


def readEdge():
    global DijkstraGraph
    edge_list_for_dijkstra = []
    with open(os.path.join(DATA_DIR,
                           "California Road Network's Edges (Edge ID, Start Node ID, End Node ID, L2 Distance).txt"),
              mode='r',
              encoding='utf-8'
              ) as f:
        while True:
            line = f.readline()
            if not line:
                break
            edgeid, sid, eid, dis = line.split(' ')
            edge_list_for_dijkstra.append((int(sid), int(eid), float(dis)))
            EdgeDict[int(edgeid)] = (int(sid), int(eid))
    print("Read %d edges" % len(EdgeDict))

    DijkstraGraph = nx.Graph()
    DijkstraGraph.add_weighted_edges_from(edge_list_for_dijkstra)
    print("Generate a dijistra graph for all edges")


def CloudBaseQuery(startId, endId):
    global nx
    path_nids = nx.dijkstra_path(DijkstraGraph, startId, endId)
    nodelist = [NodeDict[nid] for nid in path_nids]
    return Path(nodelist)


# 利用迪杰斯特拉算法生成一些路径
def generateOnePathByDijkstra():
    nids = NodeDict.keys()
    startId, endId = random.sample(nids, 2)
    path_nids = nx.dijkstra_path(DijkstraGraph, startId, endId)
    nodelist = [NodeDict[nid] for nid in path_nids]
    first = nodelist[0]
    last = nodelist[-1]
    nodelist = [sorted(POIList, key=lambda x: x.lengthTo(first))[0]] + nodelist
    nodelist.append(sorted(POIList, key=lambda x: x.lengthTo(last))[0])

    res = Path(nodelist)
    return res


# # 生成一条虚拟的路径
# def generateOnePath(a=3, b=5):
#     targetLength = random.randint(a, b)
#     while True:
#         startEdgeId = random.randint(0, len(EdgeDict) - 1)
#         neighbourEidList = [startEdgeId]
#         nextSid = EdgeDict[startEdgeId][1]
#         for i in range(targetLength):
#             nexts = {k: v for k, v in EdgeDict.items() if v[0] == nextSid}
#             if (len(nexts) == 0):
#                 break
#             k, v = random.choice(list(nexts.items()))
#             neighbourEidList.append(int(k))
#             nextSid = v[1]
#         if (len(neighbourEidList) >= targetLength):
#             break
#
#     nodelist = [NodeDict[EdgeDict[neighbourEidList[0]][0]]]
#     for eid in neighbourEidList:
#         nodelist.append(NodeDict[EdgeDict[eid][1]])
#
#     first = nodelist[0]
#     last = nodelist[-1]
#     nodelist = [sorted(POIList, key=lambda x: x.lengthTo(first))[0]] + nodelist
#     nodelist.append(sorted(POIList, key=lambda x: x.lengthTo(last))[0])
#
#     res = Path(nodelist)
#     return res
#

if (__name__ == "__main__"):
    readNode()
    readPOI()
    readEdge()

    # # print(generateOnePath())
    #
    # import pickle
    # from datetime import datetime
    # #
    # # pkl_file = open('./path100_10_16_49.storage', 'rb')
    # # pathlist = pickle.load(pkl_file)
    # # for path in pathlist:
    # #     print(path)
    #
    pathlist = []
    pathNum = 10000

    import pickle
    from datetime import datetime

    t = datetime.now()

    output = open('path%d_%s.storage' % (pathNum, str(t)[11:19].replace(':', '_')), 'wb')
    for i in range(pathNum):
        path = generateOnePathByDijkstra()
        print(i, len(path.nodelist))
        pathlist.append(path)
    print("Generate %d path." % pathNum)
    pickle.dump(pathlist, output)
