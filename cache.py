import hashlib
import math
from rtree import index


# 向云服务查询一条最短路径
def mockCloudBaseQuery(query: "(Node,Node)") -> "Path":
    return Path([])


# 从长的path中截取subpath作为query的答案
# 由于path不在Cache2中，所以不能用Rtree加速
def extractSubPath(path: "Path", query: "(Node,Node)") -> "Path":
    return Path([])


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
                print("PSA Hit %d :%s-->%s" % (count, longerPath, shorterQuery))
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

    __repr__ = __str__


class Path:
    shareAbility = 0
    nodelist = []
    length = 0.0
    nodeNumber = 0

    def __init__(self, nodelist):
        self.nodelist = nodelist
        L2 = (self.originNode.x - self.destinationNode.x) ** 2 + \
             (self.originNode.y - self.destinationNode.y) ** 2  # 适当放大避免精度问题
        self.length = math.sqrt(L2 * (10 ** 8))  # 适当放大避免精度问题
        self.nodeNumber = len(nodelist)

    # 起点
    @property
    def originNode(self):
        return self.nodelist[0]

    # 终点
    @property
    def destinationNode(self):
        return self.nodelist[-1]

    # path是否包含一个node
    def isCoverNode(self, node: "Node"):
        for n in self.nodelist:
            if (node == n):
                return True
        return False

    # 是否包含了另一个path
    def isCoverPath(self, path2: "Path"):
        if (self.isCoverNode(path2.originNode)
            and self.isCoverNode(path2.destinationNode)
            ):
            return True
        return False

    # 返回一个唯一的ID
    @property
    def ID(self):
        return "-".join([str(node.nid) for node in self.nodelist])
        # return int(hashlib.sha256(str(self.nodelist).encode('utf-8')).hexdigest(), 16) % 10 ** 9

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
    def PCCA(self, pathlist: "[Path]", ):

        pathlist.sort(key=lambda x: x.length, reverse=True)

        i = 0
        j = 1

        while (i < len(pathlist) - 1):
            longerOne = pathlist[i]
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

    def PCA(self, querylist: "[(Node,Node)]"):
        res = {}
        count = 0
        for query in querylist:
            for path in self.pathlist:
                if (path.isCoverNode(query[0]) and path.isCoverNode(query[1])):
                    count += 1
                    print("PCA Hit %d :%s -> %s" % (count, path, query))
                    res[query] = extractSubPath(path, query)
                    querylist.remove(query)
                    break
        res += PSA(querylist)
        return res


# 第二种缓存结构
# 利用倒排索引和邻接表来进行加速查找
class PathCache2:
    __reverseDict = {}
    __neighbourDict = {}
    capacity = 0
    size = 0

    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.ridx = index.Index()
        pass

    def __insertNodeReversePathTable(self, node, path: "Path"):
        self.__reverseDict.setdefault(node, path.ID)

    def __updateNeighbourTable(self, path: "Path"):
        for node1 in path.nodelist:
            for node2 in path.nodelist:
                if (node1 != node2):
                    if (node1 in self.__neighbourDict):
                        self.__neighbourDict.setdefault(node1, [node2])
                    else:
                        if (node2 not in self.__neighbourDict[node1]):
                            self.__neighbourDict[node1].append(node2)

    def get_path_by_ID(self, ID) -> "Path":
        pass

    def __addpath(self, path: "Path"):
        for node in path.nodelist:
            self.__insertNodeReversePathTable(node, path)
        self.__updateNeighbourTable(path)
        self.size += path.nodeNumber
        self.ridx.insert(path.ID, path.bonding_box)

    def PCCA(self, pathlist: "list[Path]"):

        # ====================================================
        pathlist.sort(key=lambda x: x.length, reverse=True)

        i = 0
        j = 1

        while (i < len(pathlist) - 1):
            longerOne = pathlist[i]
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

    # 利用Rtree来查找覆盖的path
    def do_rtree_query(self, query) -> "Path":
        query = Path(query)
        for item in self.ridx.intersection(query.bonding_box):
            path = self.get_path_by_ID(item.id)
            if (path.isCoverPath(query)):
                return extractSubPath(path, query)
        return None

    def PCA(self, querylist: "[(Node,Node),]"):
        res = {}
        for query in querylist:
            path = self.do_rtree_query(query)
            if (path):
                res[query] = path
                querylist.remove(query)
        res += PSA(querylist)

        return res


if (__name__ == "__main__"):
    POIlist = []
    from .readdata import readNode, readPOI, generateOneQuery, generateOnePath

    for poi_node in readNode():
        pass
    for poi_node in readPOI():
        POIlist.append(poi_node)

    # 用POI生成一些query
    querylist = []
    for i in range(2):
        query = generateOneQuery()
        querylist.append(query)

    # 用POI和node生成一些path
    pathlist = []
    for i in range(10000):
        path = generateOnePath()
        pathlist.append(path)

    # 初始化两种cache
    cache1 = PathCache1(capacity=2000)
    cache2 = PathCache2(capacity=2000)

    # 把path信息添加到缓存内
    cache1.PCCA(pathlist)
    cache2.PCCA(pathlist)

    # 利用缓存进行查询
    cache1.PCA(querylist)
    cache2.PCA(querylist)
