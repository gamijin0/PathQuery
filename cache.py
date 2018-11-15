import hashlib
import math
from rtree import index
import pickle
import time
import networkx as nx
import sys


# from readdata import readNode, readEdge, readPOI, generateOneQuery


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


# 向云服务查询一条最短路径
def mockCloudBaseQuery(query: "(Node,Node)") -> "Path":
    from readdata import CloudBaseQuery
    return CloudBaseQuery(query[0].nid, query[1].nid)


# 从长的path中截取subpath作为query的答案
# 由于path不在Cache2中，所以不能用Rtree加速
def extractSubPath(path: "Path", query: "(Node,Node)") -> "Path":
    return None
    # oi = path.nodelist.index(query[0])
    # di = path.nodelist.index(query[1])
    # if (oi < di):
    #     return Path(path.nodelist[oi:di + 1])
    # else:
    #     return Path(path.nodelist[di:oi + 1][::-1])


# PSA
# 大量query的内部覆盖缩减
def PSA(querylist: "list([(Node,Node),])"):
    querylist.sort(key=lambda x: x[0].lengthTo(x[1]), reverse=True)

    i = 0
    j = 1

    res = {}
    count = 0

    while (i < len(querylist) - 1):
        longerPath = mockCloudBaseQuery(querylist[i])
        res[querylist[i]] = longerPath
        while (j < len(querylist)):
            shorterQuery = querylist[j]
            if (longerPath.isCoverNode(shorterQuery[0])
                and longerPath.isCoverNode(shorterQuery[1])):
                count += 1
                # print("PSA Hit %d :%s-->%s" % (count, longerPath, shorterQuery))
                res[shorterQuery] = extractSubPath(longerPath, shorterQuery)
                querylist.remove(shorterQuery)
            else:
                j += 1
        i += 1

    return res


class Node:
    nid = 0
    x = 0.0
    y = 0.0

    def __init__(self, nid, x, y):
        self.nid, self.x, self.y = int(nid), float(x), float(y)

    def __eq__(self, other):
        if (self.x == other.x and self.y == other.y):
            return True
        return False

    def lengthTo(self, a_node: "Node"):
        return math.sqrt((self.x - a_node.x) ** 2 + (self.y - a_node.y) ** 2)

    def __str__(self):
        return "Node<%d>(%.2f,%.2f)" % (self.nid, self.x, self.y)

    def __hash__(self):
        return self.nid

    def isStraightLineTo(self, n: "Node", offset=0.015):
        if (self.x - offset <= n.x <= self.x + offset or self.y - offset <= n.y <= self.y + offset):
            return True
        return False

    __repr__ = __str__


#
# class Edge:
#     def __init__(self,n1:Node,n2:Node):
#         self.n1 = n1
#         self.n2 = n2

class Path:
    shareAbility = 0
    nodelist = []
    length = 0.0
    nodeNumber = 0
    ID = 0

    def __init__(self, nodelist):
        self.nodelist = tuple(nodelist)
        L2 = (self.originNode.x - self.destinationNode.x) ** 2 + \
             (self.originNode.y - self.destinationNode.y) ** 2  # 适当放大避免精度问题
        self.length = math.sqrt(L2 * (10 ** 8))  # 适当放大避免精度问题
        self.nodeNumber = len(nodelist)
        self.ID = hash(tuple(set(self.nodelist)))

    # 起点
    @property
    def originNode(self):
        return self.nodelist[0]

    def __repr__(self):
        return str(self.nodelist) + "->" + str(len(self.nodelist))
        # return "{" + "->".join([str(node) for node in self.nodelist]) + "}"

    def __hash__(self):
        return self.ID

    # 终点
    @property
    def destinationNode(self):
        return self.nodelist[-1]

    # path是否包含一个node
    def isCoverNode(self, node: "Node"):
        for i in range(len(self.nodelist) - 1):
            n1 = self.nodelist[i]
            n2 = self.nodelist[i + 1]
            l2 = n1.lengthTo(node) + n2.lengthTo(node)
            l1 = n1.lengthTo(n2)

            if (l2 <= l1 * 1.5):
                return True

        # for n in self.nodelist:
        #     if (node == n):
        #         return True
        return False

    # 是否包含了另一个path
    def isCoverPath(self, path2: "Path"):
        if (self.isCoverNode(path2.originNode)
            and self.isCoverNode(path2.destinationNode)
            ):
            return True
        return False

    @property
    def ShareAblityPerNode(self):
        return self.shareAbility * 1.0 / self.nodeNumber

    @property
    def bonding_box(self) -> tuple:
        left = min([node.x for node in self.nodelist])
        bottom = min([node.y for node in self.nodelist])
        right = max([node.x for node in self.nodelist])
        top = max([node.y for node in self.nodelist])
        return (left, bottom, right, top)


# 所有的查找都是遍历，没有索引加速
# Cache[
#   Path[
#       (x,y),
#       ...],
#   ...]
class PathCache1:
    pathlist = []
    capacity = 0
    size = 0

    def __init__(self, capacity=1000):
        self.capacity = capacity
        pass

    def __addpath(self, path: "Path"):
        self.pathlist.append(path)
        self.size += len(path.nodelist)

    # 输入一些path来构造缓存
    @timeit
    def PCCA(self, pathlist: "[Path]", ):

        pathlist.sort(key=lambda x: x.length, reverse=True)

        i = 0
        j = 1

        while (i < len(pathlist) - 1):
            longerOne = pathlist[i]
            j=i+1
            while (j < len(pathlist)):
                shorterOne = pathlist[j]
                if (longerOne.isCoverPath(shorterOne)):
                    longerOne.shareAbility += 1.0
                    shorterOne.shareAbility = 0
                    pathlist.remove(shorterOne)
                else:
                    j += 1
            i += 1

        pathlist.sort(key=lambda x: x.ShareAblityPerNode, reverse=True)

        for path in pathlist:
            if (self.size + path.nodeNumber > self.capacity):
                break
            else:
                self.__addpath(path)
                print("Add path to cache1,sa:%.2f" % path.ShareAblityPerNode)
    @timeit
    def PCA(self, querylist: "[(Node,Node)]"):
        res = {}
        count = 0
        for query in querylist:
            for path in self.pathlist:
                if (path.isCoverNode(query[0]) and path.isCoverNode(query[1])):
                    count += 1
                    # print("PCA1 Hit %d :%s -> %s" % (count, path, query))
                    res[query] = extractSubPath(path, query)
                    querylist.remove(query)
                    break
        # print("PCA1 hit rate: %.2f" % (100.0*count/len(querylist)))
        # res.update(PSA(querylist))
        return res


# 第二种缓存结构
# 利用倒排索引和邻接表来进行加速查找
class PathCache2:
    NodeDict = {}
    EdgeDict = {}
    DijkstraGraph = nx.Graph()
    capacity = 0
    size = 0

    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.ridx = index.Index()
        pass

    # def __insertEdgeReversePathTable(self, edge: "Path", path: "Path"):
    #     if (edge.ID in self.__edgeID2PathDict):
    #         self.__edgeID2PathDict[edge.ID].add(path.ID)
    #     else:
    #         self.__edgeID2PathDict[edge.ID] = set([path.ID])
    #
    # @timeit
    # def __updateEdgeNeighbourTable(self, path: "Path"):
    #     for i in range(0, len(path.nodelist) - 2):
    #         thisEdge = Path([path.nodelist[i], path.nodelist[i + 1]])
    #         postEdge = Path([path.nodelist[i + 1], path.nodelist[i + 2]])
    #         if (thisEdge.ID in self.__edgeIDNeighbourDict):
    #             self.__edgeIDNeighbourDict[thisEdge.ID].add(postEdge.ID)
    #         else:
    #             self.__edgeIDNeighbourDict[thisEdge.ID] = set([postEdge.ID])
    #         if (postEdge in self.__edgeIDNeighbourDict):
    #             self.__edgeIDNeighbourDict[postEdge.ID].add(thisEdge.ID)
    #         else:
    #             self.__edgeIDNeighbourDict[postEdge.ID] = set([thisEdge.ID])

    def __addpath(self, path: "Path"):
        for i in range(len(path.nodelist) - 1):
            n1 = path.nodelist[i]
            self.NodeDict[n1.nid] = n1
            n2 = path.nodelist[i + 1]

            nx.add_path(self.DijkstraGraph, nodes_for_path=[n1.nid, n2.nid], weight=n1.lengthTo(n2))

            edge = Path([n1, n2])
            self.EdgeDict[edge.ID] = (n1.nid, n2.nid)
            bb = edge.bonding_box
            self.ridx.insert(id=edge.ID, coordinates=bb)

        self.NodeDict[path.nodelist[-1].nid] = path.nodelist[-1]

        self.size += path.nodeNumber
        # print("2Add a path : %d" % path.ID)

    @timeit
    def PCCA(self, pathlist: "list[Path]"):
        # ====================================================
        pathlist.sort(key=lambda x: x.length, reverse=True)
        i = 0
        while (i < len(pathlist) - 1):
            j = i + 1
            longerOne = pathlist[i]
            while (j < len(pathlist)):
                shorterOne = pathlist[j]

                if (longerOne.isCoverPath(shorterOne)):
                    longerOne.shareAbility += 1.0
                    shorterOne.shareAbility = 0
                    pathlist.remove(shorterOne)
                    # print("PCCA2 remove 1")
                else:
                    j += 1
            i += 1
        pathlist.sort(key=lambda x: x.ShareAblityPerNode, reverse=True)

        for path in pathlist:
            if (self.size + path.nodeNumber > self.capacity):
                break
            else:
                self.__addpath(path)

    def findPath(self, fromEdgeId, toEdgeId):
        nid1 = self.EdgeDict[fromEdgeId][0]
        nid2 = self.EdgeDict[toEdgeId][0]
        return nx.dijkstra_path(self.DijkstraGraph, nid1, nid2)

    # 利用Rtree来查找覆盖的path
    def do_rtree_query(self, query: "(Node,Node)") -> "Path":
        # 用一次查询的起点和终点分别构造一个bonding_box
        origin_bb = [query[0].x, query[0].y, query[0].x, query[0].y]
        destination_bb = [query[1].x, query[1].y, query[1].x, query[1].y]

        # 利用bonding_box对rtree_index进行交集查询，得到候选pid_list
        originEdgeIds = list(self.ridx.intersection(origin_bb))
        DestinationIds = list(self.ridx.intersection(destination_bb))
        # print(originEdgeIds, DestinationIds)
        if (originEdgeIds and DestinationIds):
            res = self.findPath(originEdgeIds[0], DestinationIds[0])
            path = Path([self.NodeDict[nid] for nid in res])
            # print("Cache2 hit: " + str(path))
            return path
        else:
            return None

    def PCA(self, querylist: "[(Node,Node),]"):
        count = 0
        res = {}
        for query in querylist:
            path = self.do_rtree_query(query)
            if (path):
                count += 1
                res[query] = path
                querylist.remove(query)
        # res.update(PSA(querylist))
        hit_rate = count * 100.0 / len(querylist)
        # print("Cache2 hit rate: %.2f%%" % (hit_rate))

        return hit_rate
