import os
import json
from datetime import datetime
import networkx as nx
from collections import defaultdict, Counter
import math
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from neo4j import GraphDatabase
from ..dag_optimiser.dag_class import *


# Example usage
if __name__ == "__main__":
    edges = [
        ('N0', 'N3'),
        ('N0', 'N8'),
        ('N0', 'N5'),
        ('N1', 'N4'),
        ('N2', 'N8'),
        ('N3', 'N11'),
        ('N4', 'N10'),
        ('N4', 'N6'),
        ('N4', 'N9'),
        ('N5', 'N6'),
        ('N6', 'N10'),
        ('N7', 'N13'),
        ('N8', 'N9'),
        ('N8', 'N13'),
        ('N8', 'N10'),
        ('N9', 'N14'),
        ('N9', 'N13'),
        ('N9', 'N12'),
        ('N10', 'N14'),
        ('N10', 'N13'),
        ('N11', 'N12'),
    ]
    optimizer = DAGOptimizer(edges)
    print("Original Graph Edges:", optimizer.graph.edges())

    optimizer.transitive_reduction() # incremental=True
    print("After Transitive Reduction:", optimizer.graph.edges())

    optimizer.merge_equivalent_nodes()
    print("After Merging Equivalent Nodes:", optimizer.graph.edges())

    print("\n--- Graph Metrics Comparison ---")
    optimizer.evaluate_metrics()

    optimizer.save_metadata()

    optimizer.visualize()

    # optimizer.push_to_neo4j(
    #     uri="bolt://localhost:7687",
    #     user="neo4j",
    #     password="your_password"
    # )
