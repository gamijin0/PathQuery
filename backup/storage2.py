from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import json

engine = create_engine("sqlite:///dbv2.sqlite", echo=False)
metadata = MetaData(engine)

nodeReversePathTable = Table('NodeReversePath', metadata,
                             Column('nid', Integer, primary_key=True),
                             Column('pidlist', String(1000))
                             )

nodeNeighborTable = Table('NodeNeighbor', metadata,
                          Column('nid', Integer, primary_key=True),
                          Column('nnidlist', String(1000))
                          )

metadata.create_all()

#向2类存储结构中存储一条edge
def save_edge2(snid, enid):
    s = nodeNeighborTable.select().where(nodeNeighborTable.c.nid == snid)
    res = engine.execute(s).fetchall()
    if (not res):
        insert = nodeNeighborTable.insert().values(nid=snid, nnidlist=str([enid]))
        engine.execute(insert)
    else:
        for row in res:
            # print(row)
            oldnnidlist = json.loads(row[1])
            if (enid not in oldnnidlist):
                oldnnidlist.append(enid)
            update = nodeNeighborTable.update().values(nnidlist=json.dumps(oldnnidlist)).where(
                nodeNeighborTable.c.nid == snid)
            engine.execute(update)
    # print("Saved edge: (%d,%d)" % (snid, enid))

#向2类存储结构中存储一条path
def save_path2(pid, nodelist):
    for nid in nodelist:
        s = nodeReversePathTable.select().where(nodeReversePathTable.c.nid == nid)
        res = engine.execute(s).fetchall()
        if (not res):
            insert = nodeReversePathTable.insert().values(nid=nid, pidlist=json.dumps([pid]))
            engine.execute(insert)
        else:
            for row in res:
                oldpidlist = json.loads(row[1])
                if (pid not in oldpidlist):
                    oldpidlist.append(pid)
                    update = nodeReversePathTable.update().values(pidlist=json.dumps(oldpidlist)).where(
                        nodeReversePathTable.c.nid == nid)
                    engine.execute(update)


# PSA
# 利用查询内部的覆盖性来减少查询的次数
def PSAQuery2(ODtupleList):
    pass


# PCA-Rtree
# 利用缓存与Rtree来进一步减少查询的次数
def PCAQuery2(ODtupleList):
    pass

if (__name__ == "__main__"):
    save_path2(0, [1, 2, 3])
    save_path2(2, [2, 2, 4])
    save_path2(3, [1, 2, 5])
