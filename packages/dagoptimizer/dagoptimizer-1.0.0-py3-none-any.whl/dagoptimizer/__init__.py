"""
DAG Optimizer - Advanced Directed Acyclic Graph Optimization Library

This library provides state-of-the-art DAG optimization algorithms with:
- Adaptive transitive reduction (DFS for sparse, Floyd-Warshall for dense)
- PERT/CPM critical path analysis
- Layer-based width and parallelism analysis
- Edge criticality classification
- 25+ research-grade metrics

Author: Sahil Shrivastava (sahilshrivastava28@gmail.com)
License: MIT
Version: 1.0.0
"""

from .dag_class import DAGOptimizer

__version__ = "1.0.0"
__author__ = "Sahil Shrivastava"
__email__ = "sahilshrivastava28@gmail.com"
__license__ = "MIT"

__all__ = [
    "DAGOptimizer",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Convenience imports for common use cases
def optimize_dag(edges, transitive_reduction=True, merge_nodes=False, edge_attrs=None):
    """
    Quick optimization function for common use cases.
    
    Args:
        edges: List of (u, v) tuples representing edges
        transitive_reduction: Whether to apply transitive reduction (default: True)
        merge_nodes: Whether to merge equivalent nodes (default: False)
        edge_attrs: Optional dict mapping edges to attributes
    
    Returns:
        DAGOptimizer: Optimized DAG optimizer instance
    
    Example:
        >>> edges = [('A', 'B'), ('B', 'C'), ('A', 'C')]
        >>> optimizer = optimize_dag(edges)
        >>> print(f"Reduced from {optimizer.original_graph.number_of_edges()} to {optimizer.graph.number_of_edges()} edges")
    """
    optimizer = DAGOptimizer(edges, edge_attrs=edge_attrs)
    
    if transitive_reduction:
        optimizer.transitive_reduction()
    
    if merge_nodes:
        optimizer.merge_equivalent_nodes()
    
    return optimizer

