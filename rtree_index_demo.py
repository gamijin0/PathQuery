from rtree import index

rdx = index.Index()

a = [-120, 0, 5, 50]
b = (-119.158127, 38.04083, -118.798767, 38.18417)

rdx.insert(0, a)
res = rdx.intersection(b)

print(list(res))
