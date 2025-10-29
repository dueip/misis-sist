def main(csv_string):
    lines = csv_string.strip().split('\n')
    edges = []
    for line in lines:
        parts = line.split(',')
        if len(parts) >= 2:
            u = parts[0].strip()
            v = parts[1].strip()
            edges.append((u, v))
    
    vertices = set()
    for u, v in edges:
        vertices.add(u)
        vertices.add(v)
    
    sorted_vertices = sorted(vertices)
    n = len(sorted_vertices)
    
    vertex_to_index = {vertex: idx for idx, vertex in enumerate(sorted_vertices)}
    
    adjacency_matrix = [[0] * n for _ in range(n)]
    
    for u, v in edges:
        i = vertex_to_index[u]
        j = vertex_to_index[v]
        adjacency_matrix[i][j] = 1
        adjacency_matrix[j][i] = 1 
        
    return adjacency_matrix

if __name__ == "__main__":
    with open('task2.csv', 'r', encoding='utf-8') as file:
        csv_content = file.read()

    result = main(csv_content)

    for row in result:
        print(row)