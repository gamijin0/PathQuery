import hashlib


# PSA
# 大量query内存缩减
def PathSharing():
    pass


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

    def __str__(self):
        return "Node<%d>(%.2f,%.2f)" % (self.nid, self.x, self.y)

    __repr__ = __str__


class Path:
    shareAbility = 0
    nodelist = []

    def __init__(self, nodelist):
        self.nodelist = nodelist

    # 起点
    @property
    def originNode(self):
        return self.nodelist[0]

    # 终点
    @property
    def destinationNode(self):
        return self.nodelist[-1]

    # path是否包含一个node
    def isContainNode(self, node: list):
        for n in self.nodelist:
            if (node == n):
                return True
        return False

    # 是否包含了另一个path
    def isCover(self, path2: "Path"):
        if (self.isContainNode(path2.originNode)
            and self.isContainNode(path2.destinationNode)
            ):
            return True
        return False

    # 返回一个唯一的ID
    @property
    def ID(self):
        return "-".join([str(node.nid) for node in self.nodelist])
        # return int(hashlib.sha256(str(self.nodelist).encode('utf-8')).hexdigest(), 16) % 10 ** 9


# 第一种缓存结构
# 所有的查找都是遍历，没有索引加速
# Cache[
#   Path[
#       (x,y),
#       ...],
#   ...]
class PathCache1:
    pathlist = []

    def __init__(self):
        pass

    def addpath(self, path: "Path"):
        self.pathlist.append(path)


# 第二种缓存结构
# 利用倒排索引和邻接表来进行加速查找
class PathCache2:
    __reverseDict = {}
    __neighbourDict = {}

    def __int__(self):
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

    def addpath(self, path: "Path"):
        for node in path.nodelist:
            self.__insertNodeReversePathTable(node, path)
        self.__updateNeighbourTable(path)
