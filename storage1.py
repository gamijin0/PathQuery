from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker
import math
import random
from common import isPathCover
import ast

engine = create_engine("sqlite:///dbv1.sqlite")
metadata = MetaData(engine)

pathtable = Table('Path', metadata,
                  Column('pid', Integer, primary_key=True),
                  Column('nodelist', String(1000)),
                  )

metadata.create_all()


# 向1类存储结构中存储一条路径
def save_path1(pid, nodelist):
    s = pathtable.select().where(pathtable.c.pid == pid)
    res = engine.execute(s).fetchall()
    if (not res):
        insert = pathtable.insert().values(pid=pid, nodelist=str(nodelist))
        engine.execute(insert)
        # else:


# 生成数条系统必定可以回答的query
def generateAvailableQuery(num=6):
    totalNum = engine.scalar(select([func.count('*')]).select_from(pathtable))
    offsetnum = random.randint(0, totalNum - 10)
    res = engine.execute(
        select([pathtable.c.pid, pathtable.c.nodelist]).select_from(pathtable).offset(offsetnum).limit(num)).fetchall()
    for path in res:
        nodes = ast.literal_eval(path[1])
        ot = random.choice(nodes)
        nodes.remove(ot)
        dt = random.choice(nodes)
        print(ot, dt)
        yield (ot, dt)


# 用于模拟向云服务的查询,参数为起点坐标与终点坐标
def mockCloudBasedPathQuey(orginT, destT):
    try:
        s = pathtable.select().where(pathtable.c.nodelist.contains(str(orginT))).where(
            pathtable.c.nodelist.contains(str(destT)))
        res = list(engine.execute(s).fetchall())
        res.sort(key=lambda x: len(x[1]))
        # print([len(x[1]) for x in res])
        return ast.literal_eval(res[0][1])
    except Exception as e:
        print(res)
        return []


# PSA
# 利用查询内部的覆盖性来减少查询的次数
def PSAQuery1(ODtupleList):
    temp = []
    resDict = {}
    for tu in ODtupleList:
        od, td = tu
        L2 = ((od[0] - td[0]) * 100) ** 2 + ((od[1] - td[1]) * 100) ** 2  # 适当放大避免精度问题
        temp.append((L2, tu))
    temp.sort(key=lambda x: x[0], reverse=True)  # 找到最长的
    longestquery = temp[0][1]
    temp = temp[1:]
    # temp = list(filter(lambda x: x[1] != longestquery, temp))
    while (temp):
        longestpath = mockCloudBasedPathQuey(longestquery[0], longestquery[1])
        resDict[longestquery] = longestpath
        i = 0
        while (i < len(temp)):
            thisquery = temp[i][1]
            if (isPathCover(longestpath, thisquery[0], thisquery[1])):
                print("PSA Path Cover !:")
                print(longestpath)
                print(thisquery)
                # TODO:修改shareAblity,用longestpath来回答这个query
                temp.remove(temp[i])
            else:
                i += 1
        longestquery = temp[0][1]
        # temp = list(filter(lambda x: x[1] != longestquery, temp))
        temp = temp[1:]
    print("PSA1 finished.")
    return resDict


# 输入一系列path来构造cache
def PCCA1(pathset, capacity=100):
    pathDict = {}
    temp = []
    for odtu, path in pathset:
        od, td = odtu[0], odtu[-1]
        L2 = ((od[0] - td[0]) * 100) ** 2 + ((od[1] - td[1]) * 100) ** 2  # 适当放大避免精度问题
        pathDict[(od, td)] = [L2, path, 0]  # 长度，路径，SA
        temp.append((L2, odtu))
    temp.sort(key=lambda x: x[0], reverse=True)  # 找到最长的
    longestquery = temp[0][1]
    temp = temp[1:]
    while (temp):
        # 遍历剩下的集合内计算SA
        i = 0
        while (i < len(temp)):
            thisquery = temp[i][1]
            if (isPathCover(pathDict[longestquery][1], thisquery[0], thisquery[1])):
                print("PCCA Path Cover!:")
                print(thisquery)
                # TODO:修改shareAblity
                temp.remove(temp[i])
                pathDict[longestquery][2] += 1
                # print(pathDict[longestquery])
            else:
                i += 1
        pathDict[longestquery][2] /= len(pathDict[longestquery][1])
        print(pathDict[longestquery])
        longestquery = temp[0][1]
        # temp = list(filter(lambda x: x[1] != longestquery, temp))
        temp = temp[1:]


# PCA
# 利用缓存来进一步减少查询的次数
def PCAQuery1(ODtupleList):
    pass


# 基于结构1的查询
def query1(ODtupleList):
    pass
