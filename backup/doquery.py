from storage1 import generateAvailableQuery, mockCloudBasedPathQuey, PSAQuery1, PCAQuery1, PCCA1

if (__name__ == "__main__"):
    # for od, dt in generateAvailableQuery():
    # mockCloudBasedPathQuey(od, dt)
    qset = list(generateAvailableQuery(num=1000))
    tempres = []
    for query in qset:
        tempres.append(mockCloudBasedPathQuey(query[0],query[1]))
    # pathset = PSAQuery1(qset)
    # print(pathset)
    PCCA1(tempres)
    PCAQuery1(qset)
