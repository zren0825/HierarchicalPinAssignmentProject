a = [0, 1, 2, 3, 4 ]
b = [5, 6, 7, 8, 9 ]
index = 3
#print(a[index:len(a)] + a[0:index])

for i, j in zip(a, b):
	print(i + j)