DATA_DIR = '../data/'
import os
import random
from uuid import uuid4

NodeDict = {}
PathDict = {}
EdgeDict = {}


def readNode():
    with open(os.path.join(DATA_DIR, "California Road Network's Nodes (Node ID, Longitude, Latitude).txt"),
              mode='r',
              encoding='utf-8'
              ) as f:
        while True:
            line = f.readline()
            if not line:
                break
            nid, x, y = line.split(' ')
            NodeDict[int(nid)] = (float(x), float(y))
        print("Read %d Nodes." % len(NodeDict))


def readEdge():
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
            EdgeDict[int(edgeid)] = (int(sid), int(eid))
            # print(EdgeDict[int(edgeid)])


def printPath(patharr, type="E"):
    if ('E' in type):
        print('-->'.join(["E(%d,%d)" % (EdgeDict[x][0], EdgeDict[x][1]) for x in patharr]))
    if ('N' in type):
        print(
            '-->\n'.join(
                ["N%d(%.2f,%.2f)" % (EdgeDict[x][0], NodeDict[EdgeDict[x][0]][0], NodeDict[EdgeDict[x][0]][1]) for x in
                 patharr]))

#生成一条虚拟的路径
def generateOnePath(a=3, b=7):
    targetLength = random.randint(a, b)
    while True:
        startEdgeId = random.randint(0, len(EdgeDict) - 1)
        tempPath = [startEdgeId]
        nextSid = EdgeDict[startEdgeId][1]
        for i in range(targetLength):
            nexts = {k: v for k, v in EdgeDict.items() if v[0] == nextSid}
            if (len(nexts) == 0):
                break
            k, v = random.choice(list(nexts.items()))
            tempPath.append(k)
            nextSid = v[1]
        if (len(tempPath) >= targetLength):
            break
    return tempPath


if (__name__ == "__main__"):

    from storage2 import save_edge2, save_path2
    from storage1 import save_path1
    import hashlib

    readNode()
    readEdge()
    i = 0
    # for k,v in list(EdgeDict.items()):
    #     i+=1
    #     save_edge2(v[1], v[0])
    #     save_edge2(v[0], v[1])
    #     print(i,':',v[0],v[1])

    for i in range(0, 10000):
        p = generateOnePath()
        #用hash来确保不会存重复的path
        pid = int(hashlib.sha256(str(p).encode('utf-8')).hexdigest(), 16) % 10 ** 8
        save_path2(pid=pid, nodelist=[EdgeDict[x][0] for x in
                                      p])
        save_path1(pid=pid, nodelist=[(NodeDict[EdgeDict[x][0]][0], NodeDict[EdgeDict[x][0]][1]) for x in
                                      p])
        print(p)
        printPath(p, 'NE')
