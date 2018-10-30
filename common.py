def isPathCover(path, ot, dt):
    if (ot in path and dt in path):  # 现在是精确匹配，后面改成估算
        return True
    return False


def extractSubPath(path: list, ot, dt):
    oi = path.index(ot)
    di = path.index(dt)
    if (oi < di):
        return path[oi:di + 1]
    else:
        return path[di:oi + 1][::-1]
