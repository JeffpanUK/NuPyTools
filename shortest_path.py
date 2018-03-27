import pdb
def dijkstra(W, start,end):
    # safety check
    if start < 0:
        raise "Invalid start point"
    if end >= len(W):
        raise "Invalid end point"
    if len(W) == 0:
        raise "empty weight matrix"
    path = [start]
    distance = W[int(start)]
    for i in range(len(W)):
        nextP = find_next(distance, path)
        path.append(nextP)
        if nextP == end:
            return distance, path

        # update distance matrix
        for j in range(len(W)):
            if j not in path and distance[nextP] + W[nextP][j] < distance[j]:
                distance[j] =  distance[nextP] + W[nextP][j]

def find_next(distance, labelled):
    min_d = float('inf')
    next_p = -1
    for i in range(len(distance)):
        if i not in labelled:
            if distance[i] < min_d:
                min_d = distance[i]
                next_p = i
    return next_p

def main():
    block = float('inf')
    W = [
    [0,1,4,block,block,block],
    [1,0,2,7,5,block],
    [4,2,0,block,1,block],
    [block,7,block,0,3,2],
    [block,5,1,3,0,6],
    [block,block,block,2,6,0]
    ]
    for s in range(len(W)):
        for e in range(len(W)):
            if s == e:
                continue
            distance, path = dijkstra(W, s, e)
            print("Target: %d->%d"%(s,e))
            if distance[len(path)-1] == block:
                print("No path exists")
            else:
                print("The shortest path is: %s"%("->".join(list(map(lambda x: str(x), path)))))
                print("The shortest distance is: %d"%distance[len(path)-1])

if __name__ == '__main__':
    main()





