def transitive_reduction(graph):
    """
    Compute the transitive reduction of a directed graph.

    Args:
        graph (dict): A dictionary representing a directed graph where keys are nodes
                      and values are lists of successor nodes.

    Returns:
        dict: A new dictionary representing the transitive reduction of the graph.
    """
    # Set to store edges to be removed
    to_remove = set()

    # Iterate over each node and its successors
    for u in graph:
        for v in graph[u]:
            # Find all nodes reachable from v
            reachable = DFS(graph, v)
            # Check each reachable node w
            for w in reachable:
                # If w is not v and there's a direct edge u -> w, mark it for removal
                if w != v and w in graph[u]:
                    to_remove.add((u, w))

    # Build the reduced graph by excluding edges marked for removal
    reduced_graph = {u: [w for w in graph[u] if (u, w) not in to_remove] for u in graph}
    return reduced_graph


def DFS(graph, start):
    """
    Perform an iterative depth-first search from a starting node.

    Args:
        graph (dict): The graph as a dictionary of nodes to successor lists.
        start: The starting node for DFS.

    Returns:
        set: A set of all nodes reachable from the start node.
    """
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            # Add unvisited neighbors to the stack
            for neighbor in graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
    return visited


# Test the implementation
if __name__ == "__main__":
    # Example 1: Graph with a redundant edge
    graph1 = {
        'a': ['b', 'c'],  # a -> b, a -> c
        'b': ['c'],  # b -> c
        'c': []  # c has no outgoing edges
    }
    reduced1 = transitive_reduction(graph1)
    print("Graph 1 reduced:", reduced1)
    # Expected output: {'a': ['b'], 'b': ['c'], 'c': []}
    # Edge a -> c is removed because a -> b -> c exists

    # Example 2: Cyclic graph
    graph2 = {
        'a': ['b'],  # a -> b
        'b': ['c'],  # b -> c
        'c': ['a']  # c -> a
    }
    reduced2 = transitive_reduction(graph2)
    print("Graph 2 reduced:", reduced2)
    # Expected output: {'a': ['b'], 'b': ['c'], 'c': ['a']}
    # No edges are removed as the cycle has no redundant paths