def floyd_warshall_transitive_closure(graph):
    """
    Compute the transitive closure of a graph using the Floyd-Warshall algorithm.

    Args:
        graph (list of list): Adjacency matrix where graph[i][j] = 1 if there's an edge from i to j.

    Returns:
        list of list: Transitive closure matrix where closure[i][j] = 1 if there's a path from i to j.
    """
    n = len(graph)
    # Initialize closure matrix: 1 if direct edge exists or i == j (node reaches itself), 0 otherwise
    closure = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j or graph[i][j] == 1:
                closure[i][j] = 1

    # Floyd-Warshall: Update closure[i][j] if there's a path through k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if closure[i][k] and closure[k][j]:
                    closure[i][j] = 1
    return closure


def transitive_reduction(graph_dict):
    """
    Compute the transitive reduction of a directed graph using Floyd-Warshall.
    Note: Correct for DAGs; may not preserve reachability in cyclic graphs.

    Args:
        graph_dict (dict): Graph where keys are nodes and values are lists of successor nodes.

    Returns:
        dict: Transitive reduction of the graph as a dictionary.
    """
    # Get all nodes and map to indices
    nodes = list(graph_dict.keys())
    n = len(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}

    # Build adjacency matrix
    adj = [[0] * n for _ in range(n)]
    for node, successors in graph_dict.items():
        i = node_to_index[node]
        for succ in successors:
            j = node_to_index[succ]
            adj[i][j] = 1

    # Compute transitive closure
    closure = floyd_warshall_transitive_closure(adj)

    # Build reduction matrix
    red = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if adj[i][j] == 1:  # If there's a direct edge
                # Check for alternative path via some k
                redundant = False
                for k in range(n):
                    if k != i and k != j and closure[i][k] and closure[k][j]:
                        redundant = True
                        break
                if not redundant:
                    red[i][j] = 1  # Keep edge if no alternative path exists

    # Convert reduction matrix back to dictionary
    reduced_graph = {node: [] for node in nodes}
    for i in range(n):
        for j in range(n):
            if red[i][j] == 1:
                reduced_graph[nodes[i]].append(nodes[j])
    return reduced_graph


# Test the implementation
if __name__ == "__main__":
    # Test Case 1: DAG with a redundant edge
    graph1 = {
        'a': ['b', 'c'],  # a → b, a → c
        'b': ['c'],  # b → c
        'c': []  # c has no outgoing edges
    }
    reduced1 = transitive_reduction(graph1)
    print("Test Case 1 (DAG):", reduced1)
    # Expected: {'a': ['b'], 'b': ['c'], 'c': []}
    # Edge a → c is removed because a → b → c exists

    # Test Case 2: Cyclic graph
    graph2 = {
        'a': ['b'],  # a → b
        'b': ['c'],  # b → c
        'c': ['a']  # c → a
    }
    reduced2 = transitive_reduction(graph2)
    print("Test Case 2 (Cycle):", reduced2)
    # Note: May output {'a': [], 'b': [], 'c': []}, which is incorrect for cycles
    # Correct reduction should keep the cycle, e.g., {'a': ['b'], 'b': ['c'], 'c': ['a']}