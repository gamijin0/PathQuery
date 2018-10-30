def isPathCover(path, ot, dt):
    if (ot in path and dt in path): #现在是精确匹配，后面改成估算
        return True
    return False
