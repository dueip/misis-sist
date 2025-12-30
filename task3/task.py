import json


def main(ranking_a_json: str, ranking_b_json: str) -> str:
    ranking_a = json.loads(ranking_a_json)
    ranking_b = json.loads(ranking_b_json)

    objects = sorted(set(flatten_ranking(ranking_a) + flatten_ranking(ranking_b)))
    n = len(objects)
    obj_to_idx = {obj: idx for idx, obj in enumerate(objects)}

    YA = build_relation_matrix(ranking_a, obj_to_idx, n)
    YB = build_relation_matrix(ranking_b, obj_to_idx, n)

    SA = build_strict_matrix(YA, n)
    SB = build_strict_matrix(YB, n)

    P = and_matrix(SA, SB, n)

    EA = build_equivalence_from_relation(YA, n)
    EB = build_equivalence_from_relation(YB, n)

    K = build_contradictions_adjacent(ranking_a, ranking_b, SA, SB, obj_to_idx)

    E0 = or3_matrix(EA, EB, K, n)
    for i in range(n):
        E0[i][i] = 1

    E_star = warshall(E0, n)
    clusters = extract_clusters(E_star, n)

    result = order_clusters(clusters, P, objects)
    return json.dumps(result, ensure_ascii=False)


def build_relation_matrix(ranking, obj_to_idx, n):
    Y = create_matrix(n)
    for i in range(len(ranking)):
        level_i = ranking[i] if isinstance(ranking[i], list) else [ranking[i]]
        for a in level_i:
            for b in level_i:
                Y[obj_to_idx[a]][obj_to_idx[b]] = 1
        for j in range(i + 1, len(ranking)):
            level_j = ranking[j] if isinstance(ranking[j], list) else [ranking[j]]
            for a in level_i:
                for b in level_j:
                    Y[obj_to_idx[a]][obj_to_idx[b]] = 1
    return Y


def build_strict_matrix(Y, n):
    S = create_matrix(n)
    for i in range(n):
        for j in range(n):
            if i != j and Y[i][j] == 1 and Y[j][i] == 0:
                S[i][j] = 1
    return S


def build_equivalence_from_relation(Y, n):
    YT = transpose_matrix(Y, n)
    E = create_matrix(n)
    for i in range(n):
        for j in range(n):
            if Y[i][j] == 1 and YT[i][j] == 1:
                E[i][j] = 1
    return E


def iter_levels(ranking):
    return [x if isinstance(x, list) else [x] for x in ranking]


def add_adjacent_conflicts(levels, S_left, S_right, obj_to_idx, K):
    for t in range(len(levels) - 1):
        for a in levels[t]:
            ia = obj_to_idx[a]
            for b in levels[t + 1]:
                ib = obj_to_idx[b]
                if S_left[ia][ib] == 1 and S_right[ib][ia] == 1:
                    K[ia][ib] = 1
                    K[ib][ia] = 1


def build_contradictions_adjacent(ranking_a, ranking_b, SA, SB, obj_to_idx):
    n = len(obj_to_idx)
    K = create_matrix(n)
    levels_a = iter_levels(ranking_a)
    levels_b = iter_levels(ranking_b)
    add_adjacent_conflicts(levels_a, SA, SB, obj_to_idx, K)
    add_adjacent_conflicts(levels_b, SB, SA, obj_to_idx, K)
    return K


def extract_clusters(E_star, n):
    visited = [False] * n
    clusters = []
    for i in range(n):
        if not visited[i]:
            cluster = []
            for j in range(n):
                if E_star[i][j] == 1:
                    cluster.append(j)
                    visited[j] = True
            clusters.append(sorted(cluster))
    return clusters


def order_clusters(clusters, P, objects):
    num_clusters = len(clusters)
    order = create_matrix(num_clusters)
    for i in range(num_clusters):
        for j in range(num_clusters):
            if i == j:
                continue
            forward = False
            backward = False
            for a in clusters[i]:
                for b in clusters[j]:
                    if P[a][b] == 1:
                        forward = True
                    if P[b][a] == 1:
                        backward = True
            if forward and not backward:
                order[i][j] = 1
    sorted_clusters = topological_sort(order, clusters, num_clusters)
    result = []
    for cl in sorted_clusters:
        items = [objects[i] for i in cl]
        result.append(items[0] if len(items) == 1 else sorted(items))
    return result


def topological_sort(order_matrix, clusters, n):
    in_degree = [0] * n
    for j in range(n):
        for i in range(n):
            if order_matrix[i][j] == 1:
                in_degree[j] += 1
    result = []
    available = [i for i in range(n) if in_degree[i] == 0]
    while available:
        available.sort()
        cur = available.pop(0)
        result.append(clusters[cur])
        for j in range(n):
            if order_matrix[cur][j] == 1:
                in_degree[j] -= 1
                if in_degree[j] == 0:
                    available.append(j)
    return result


def create_matrix(n):
    return [[0] * n for _ in range(n)]


def transpose_matrix(M, n):
    return [[M[j][i] for j in range(n)] for i in range(n)]


def and_matrix(A, B, n):
    return [[1 if A[i][j] and B[i][j] else 0 for j in range(n)] for i in range(n)]


def or3_matrix(A, B, C, n):
    return [[1 if A[i][j] or B[i][j] or C[i][j] else 0 for j in range(n)] for i in range(n)]


def warshall(M, n):
    R = [row[:] for row in M]
    for k in range(n):
        for i in range(n):
            if R[i][k]:
                for j in range(n):
                    if R[k][j]:
                        R[i][j] = 1
    return R


def flatten_ranking(ranking):
    res = []
    for x in ranking:
        if isinstance(x, list):
            res.extend(x)
        else:
            res.append(x)
    return res


if __name__ == "__main__":
    ranking_a = json.dumps([1, 2, 3, 4, 5])
    ranking_b = json.dumps([3, 1, 4, 2, 5])
    result = main(ranking_a, ranking_b)
    print(result)