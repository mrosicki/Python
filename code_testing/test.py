import sys

arr = []
for i in range(10):
    arr.append([])

for i in range(10):
    for j in range(10):
        arr[i].append(i)
        sys.stdout.write(str(arr[i][j]))
    print()
        

elements = [inner for outer in arr for inner in outer]


for value in enumerate(elements):
    print(value[0])
# print(enumerate(elements))
