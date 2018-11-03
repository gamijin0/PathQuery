DATA_DIR = '../data/'
import os
import random
import sys
import hashlib

sys.path.append(".")

from src.cache import Node


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
                yield Node(nid, x, y)
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
                yield Node(nid, x, y)
            except Exception as e:
                pass
        print("Read %d Nodes." % count)


def generateOnePath():
    origin, destation = random.sample(POIlist, 2)



def generateOneQuery():
    origin, destation = random.sample(POIlist, 2)
    return origin, destation


if (__name__ == "__main__"):

    POIlist = []

    for poi_node in readNode():
        pass
    for poi_node in readPOI():
        POIlist.append(poi_node)

    for i in range(2):
        query = generateOneQuery()
        print(query)
