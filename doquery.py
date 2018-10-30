from storage1 import generateAvailableQuery, mockCloudBasedPathQuey, PSAQuery1, PCAQuery1, PCCA1

if (__name__ == "__main__"):
    # for od, dt in generateAvailableQuery():
    # mockCloudBasedPathQuey(od, dt)
    qset = list(generateAvailableQuery(num=2000))
    pathset = PSAQuery1(qset)
    # print(pathset)
    PCCA1(pathset.items())
