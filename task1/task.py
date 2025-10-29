from typing import List, Tuple
from collections import defaultdict 

def main(s: str, e: str) -> Tuple[List[List[bool]], List[List[bool]], List[List[bool]], List[List[bool]], List[List[bool]]]:
    edges = [tuple(map(int, line.split(','))) for line in s.strip().split('\n')]
    nodes = sorted({v for edge in edges for v in edge})
    n = len(nodes)
    index = {v: i for i, v in enumerate(nodes)} 
    r1 = [[False]*n for _ in range(n)]  
    r2 = [[False]*n for _ in range(n)]  
    r3 = [[False]*n for _ in range(n)]  
    r4 = [[False]*n for _ in range(n)]  
    r5 = [[False]*n for _ in range(n)]

    for a, b in edges:
        i, j = index[a], index[b]
        r1[i][j] = True
        r2[j][i] = True

    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)

    def dfs(start, node, depth):
        for nxt in adj[node]:
            if nxt != start:
                if depth >= 1:  
                    r3[index[start]][index[nxt]] = True
                dfs(start, nxt, depth + 1)

    for v in nodes:
        dfs(v, v, 0)

    for i in range(n):
        for j in range(n):
            r4[j][i] = r3[i][j]

    parent = {b: a for a, b in edges}
    for i in range(n):
        for j in range(n):
            if i != j:
                vi, vj = nodes[i], nodes[j]
                if parent.get(vi) == parent.get(vj) and parent.get(vi) is not None:
                    r5[i][j] = True

    return r1, r2, r3, r4, r5


if __name__ == "__main__":
    s = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
    e = "1"
    r1, r2, r3, r4, r5 = main(s, e)
    for idx, r in enumerate([r1, r2, r3, r4, r5], 1):
        print(f"r{idx}:")
        for row in r:
            print(row)
        print()