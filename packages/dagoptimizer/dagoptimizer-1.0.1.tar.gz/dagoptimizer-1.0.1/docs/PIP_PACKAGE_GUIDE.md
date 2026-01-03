# 📦 DAG Optimizer - Pip Package Guide

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Complete API Reference](#complete-api-reference)
- [Advanced Usage](#advanced-usage)
- [Real-World Examples](#real-world-examples)
- [Publishing to PyPI](#publishing-to-pypi)
- [Development](#development)

---

## Installation

### Basic Installation

```bash
pip install dagoptimizer
```

### With Optional Dependencies

```bash
# For Neo4j database integration
pip install dagoptimizer[neo4j]

# For visualization (matplotlib, pygraphviz)
pip install dagoptimizer[visualization]

# For AI-powered features (OpenAI, Anthropic)
pip install dagoptimizer[ai]

# Install everything
pip install dagoptimizer[all]
```

### Development Installation

```bash
git clone https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs.git
cd Optimisation_of_DAGs
pip install -e ".[dev]"
```

### Requirements

- Python >= 3.8
- NetworkX >= 2.6
- NumPy >= 1.20
- SciPy >= 1.7

---

## Quick Start

### 1. Basic Optimization

```python
from dagoptimizer import DAGOptimizer

# Define your DAG
edges = [
    ('A', 'B'),
    ('B', 'C'),
    ('A', 'C'),  # Redundant edge!
]

# Optimize
optimizer = DAGOptimizer(edges)
optimizer.transitive_reduction()

# Results
print(f"Reduced from {optimizer.original_graph.number_of_edges()} to {optimizer.graph.number_of_edges()} edges")
# Output: Reduced from 3 to 2 edges

# Get optimized edges
print(list(optimizer.graph.edges()))
# Output: [('A', 'B'), ('B', 'C')]
```

### 2. Using the Convenience Function

```python
from dagoptimizer import optimize_dag

# One-liner optimization
optimizer = optimize_dag(
    edges=[('A', 'B'), ('B', 'C'), ('A', 'C')],
    transitive_reduction=True,
    merge_nodes=False
)

print(f"Optimized! {optimizer.graph.number_of_edges()} edges remaining")
```

---

## Complete API Reference

### `DAGOptimizer` Class

#### Constructor

```python
DAGOptimizer(edges, edge_attrs=None)
```

**Parameters**:
- `edges` (list): List of (u, v) tuples representing directed edges
- `edge_attrs` (dict, optional): Mapping of edges to attributes

**Raises**:
- `ValueError`: If the input graph contains cycles (not a DAG)

**Example**:
```python
edges = [('A', 'B'), ('B', 'C')]
optimizer = DAGOptimizer(edges)

# With attributes
edge_attrs = {
    ('A', 'B'): ['critical', 'fast'],
    ('B', 'C'): ['optional']
}
optimizer = DAGOptimizer(edges, edge_attrs=edge_attrs)
```

---

#### `transitive_reduction()`

Apply adaptive transitive reduction algorithm.

```python
optimizer.transitive_reduction()
```

**Returns**: None (modifies `optimizer.graph` in-place)

**Algorithm Selection**:
- Sparse graphs (density < 0.1): DFS-based, O(n·m)
- Dense graphs (density ≥ 0.1): Floyd-Warshall, O(n³)

**Example**:
```python
optimizer = DAGOptimizer(edges)
optimizer.transitive_reduction()

print(f"Algorithm used: {optimizer.optimization_method}")
# Output: "DFS-based TR (sparse graph)" or "Floyd-Warshall TR (dense graph)"
```

---

#### `merge_equivalent_nodes()`

Merge nodes with identical predecessors and successors.

```python
optimizer.merge_equivalent_nodes()
```

**Returns**: None (modifies `optimizer.graph` in-place)

**Example**:
```python
# Both B and C have the same dependencies
edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')]

optimizer = DAGOptimizer(edges)
optimizer.merge_equivalent_nodes()

# B and C are now merged into one node
```

---

#### `compute_critical_path_with_slack(G)`

Compute PERT/CPM critical path analysis.

```python
result = optimizer.compute_critical_path_with_slack(optimizer.graph)
```

**Parameters**:
- `G` (NetworkX DiGraph): The graph to analyze

**Returns**: Dictionary containing:
- `critical_path` (list): Nodes on the critical path
- `makespan` (int): Total execution time
- `est` (dict): Earliest Start Time for each node
- `lst` (dict): Latest Start Time for each node
- `slack` (dict): Slack time (LST - EST) for each node
- `parallel_time_saved` (float): % time saved through parallelization

**Example**:
```python
cp = optimizer.compute_critical_path_with_slack(optimizer.graph)

print(f"Critical Path: {cp['critical_path']}")
print(f"Makespan: {cp['makespan']} time units")
print(f"Parallel Time Saved: {cp['parallel_time_saved']:.1%}")

# Find bottleneck tasks (zero slack)
bottlenecks = [node for node, slack in cp['slack'].items() if slack == 0]
print(f"Bottlenecks: {bottlenecks}")
```

---

#### `compute_layer_structure(G)`

Compute layer-based structure for parallelism analysis.

```python
result = optimizer.compute_layer_structure(optimizer.graph)
```

**Parameters**:
- `G` (NetworkX DiGraph): The graph to analyze

**Returns**: Dictionary containing:
- `layers` (dict): Mapping of layer number to list of nodes
- `width` (int): Maximum layer width (max parallel tasks)
- `depth` (int): Number of layers (min execution time)
- `avg_layer_size` (float): Average nodes per layer
- `width_efficiency` (float): How efficiently parallelism is used

**Example**:
```python
layers = optimizer.compute_layer_structure(optimizer.graph)

print(f"Max Parallel Tasks: {layers['width']}")
print(f"Min Execution Time: {layers['depth']} steps")
print(f"Width Efficiency: {layers['width_efficiency']:.1%}")

# See layer breakdown
for layer_num, nodes in layers['layers'].items():
    print(f"Layer {layer_num}: {nodes} can run in parallel")
```

---

#### `compute_edge_criticality(G)`

Classify edges as critical or redundant.

```python
result = optimizer.compute_edge_criticality(optimizer.graph)
```

**Parameters**:
- `G` (NetworkX DiGraph): The graph to analyze

**Returns**: Dictionary containing:
- `critical_edges` (list): Edges that cannot be removed
- `redundant_edges` (list): Edges that were transitive
- `edge_criticality_scores` (dict): Score per edge (1.0 = critical, 0.0 = redundant)
- `avg_criticality` (float): Average criticality ratio

**Example**:
```python
criticality = optimizer.compute_edge_criticality(optimizer.graph)

print(f"Critical Edges: {len(criticality['critical_edges'])}")
print(f"Redundant Edges: {len(criticality['redundant_edges'])}")
print(f"Criticality Ratio: {criticality['avg_criticality']:.2%}")

# Check specific edges
for edge, score in criticality['edge_criticality_scores'].items():
    status = "CRITICAL" if score == 1.0 else "REDUNDANT"
    print(f"{edge}: {status}")
```

---

#### `evaluate_graph_metrics(G)`

Compute 25+ comprehensive graph metrics.

```python
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
```

**Parameters**:
- `G` (NetworkX DiGraph): The graph to analyze

**Returns**: Dictionary containing all metrics:

**Basic Metrics**:
- `num_nodes`, `num_edges`, `density`, `leaf_nodes`

**Path Metrics**:
- `longest_path_length`, `shortest_path_length`, `avg_path_length`, `diameter`

**Structural Metrics**:
- `topological_complexity`, `degree_distribution`, `degree_entropy`

**Efficiency Metrics**:
- `efficiency_score`, `redundancy_ratio`, `compactness_score`

**Critical Path Metrics**:
- `critical_path`, `critical_path_length`, `bottleneck_nodes`, `makespan`

**Parallelism Metrics**:
- `width`, `depth`, `width_efficiency`, `avg_layer_size`

**Advanced Metrics**:
- `strongly_connected_components`, `transitivity`, `cyclomatic_complexity`

**Example**:
```python
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)

# Basic metrics
print(f"Nodes: {metrics['num_nodes']}")
print(f"Edges: {metrics['num_edges']}")
print(f"Density: {metrics['density']:.3f}")

# Efficiency metrics
print(f"Efficiency Score: {metrics['efficiency_score']:.1%}")
print(f"Redundancy Ratio: {metrics['redundancy_ratio']:.1%}")

# Structural metrics
print(f"Topological Complexity: {metrics['topological_complexity']} levels")
print(f"Degree Entropy: {metrics['degree_entropy']:.2f}")

# Advanced metrics
print(f"Bottleneck Nodes: {metrics['bottleneck_nodes']}")
print(f"Critical Path: {metrics['critical_path']}")
```

---

## Advanced Usage

### 1. Complete Workflow Example

```python
from dagoptimizer import DAGOptimizer

# Define complex DAG
edges = [
    ('checkout', 'install_deps'),
    ('install_deps', 'lint'),
    ('install_deps', 'test_unit'),
    ('install_deps', 'test_integration'),
    ('lint', 'build'),
    ('test_unit', 'build'),
    ('test_integration', 'build'),
    ('build', 'deploy_staging'),
    ('deploy_staging', 'test_e2e'),
    ('test_e2e', 'deploy_prod'),
    # Redundant edges
    ('checkout', 'lint'),
    ('checkout', 'test_unit'),
    ('checkout', 'build'),
]

# Initialize
optimizer = DAGOptimizer(edges)

# Step 1: Optimize
optimizer.transitive_reduction()
print(f"✅ Reduced from {optimizer.original_graph.number_of_edges()} to {optimizer.graph.number_of_edges()} edges")

# Step 2: Critical Path Analysis
cp = optimizer.compute_critical_path_with_slack(optimizer.graph)
print(f"\n🎯 Critical Path: {' → '.join(cp['critical_path'])}")
print(f"⏱️  Makespan: {cp['makespan']} steps")
print(f"⚡ Parallel Time Saved: {cp['parallel_time_saved']:.1%}")

# Step 3: Parallelism Analysis
layers = optimizer.compute_layer_structure(optimizer.graph)
print(f"\n📊 Parallelism Analysis:")
print(f"   Max Parallel Jobs: {layers['width']}")
print(f"   Min Pipeline Depth: {layers['depth']} steps")
print(f"   Speedup Potential: {len(edges) / layers['depth']:.1f}×")

# Step 4: Layer Breakdown
print(f"\n📋 Layer Breakdown:")
for layer_num, nodes in sorted(layers['layers'].items()):
    print(f"   Layer {layer_num}: {nodes}")

# Step 5: Edge Criticality
criticality = optimizer.compute_edge_criticality(optimizer.graph)
print(f"\n🔍 Edge Analysis:")
print(f"   Critical Edges: {len(criticality['critical_edges'])}")
print(f"   Redundant Edges Removed: {len(criticality['redundant_edges'])}")

# Step 6: Comprehensive Metrics
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
print(f"\n📈 Graph Metrics:")
print(f"   Efficiency Score: {metrics['efficiency_score']:.1%}")
print(f"   Redundancy Ratio: {metrics['redundancy_ratio']:.1%}")
print(f"   Graph Density: {metrics['density']:.3f}")
```

### 2. Comparing Before and After

```python
from dagoptimizer import DAGOptimizer

edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('A', 'C'), ('B', 'D'), ('A', 'D')]

optimizer = DAGOptimizer(edges)

# Metrics before optimization
metrics_before = optimizer.evaluate_graph_metrics(optimizer.original_graph)

# Optimize
optimizer.transitive_reduction()

# Metrics after optimization
metrics_after = optimizer.evaluate_graph_metrics(optimizer.graph)

# Compare
print("=== Comparison ===")
print(f"Edges: {metrics_before['num_edges']} → {metrics_after['num_edges']} "
      f"({((metrics_before['num_edges'] - metrics_after['num_edges']) / metrics_before['num_edges'] * 100):.1f}% reduction)")
print(f"Efficiency: {metrics_before['efficiency_score']:.1%} → {metrics_after['efficiency_score']:.1%}")
print(f"Redundancy: {metrics_before['redundancy_ratio']:.1%} → {metrics_after['redundancy_ratio']:.1%}")
```

### 3. Working with Edge Attributes

```python
from dagoptimizer import DAGOptimizer

edges = [('A', 'B'), ('B', 'C'), ('A', 'C')]

# Define attributes for each edge
edge_attrs = {
    ('A', 'B'): ['critical', 'fast', 'priority:1'],
    ('B', 'C'): ['optional', 'slow', 'priority:2'],
    ('A', 'C'): ['redundant', 'fast', 'priority:3']
}

optimizer = DAGOptimizer(edges, edge_attrs=edge_attrs)
optimizer.transitive_reduction()

# Check which attributes survived
print("Surviving edge attributes:")
for edge in optimizer.graph.edges():
    attrs = optimizer.edge_attrs.get(edge, [])
    print(f"  {edge}: {attrs}")
```

---

## Real-World Examples

### Example 1: Maven Build Dependencies

```python
from dagoptimizer import DAGOptimizer

# Maven module dependencies
maven_deps = [
    ('common-utils', 'data-access'),
    ('common-utils', 'business-logic'),
    ('data-access', 'business-logic'),
    ('business-logic', 'api-layer'),
    ('data-access', 'api-layer'),  # Redundant!
    ('common-utils', 'api-layer'),  # Redundant!
    ('api-layer', 'web-app'),
]

optimizer = DAGOptimizer(maven_deps)
optimizer.transitive_reduction()

print(f"Maven Dependencies Optimized:")
print(f"  Before: {optimizer.original_graph.number_of_edges()} dependencies")
print(f"  After: {optimizer.graph.number_of_edges()} dependencies")
print(f"  Reduction: {((optimizer.original_graph.number_of_edges() - optimizer.graph.number_of_edges()) / optimizer.original_graph.number_of_edges() * 100):.1f}%")

# Find critical path for build order
cp = optimizer.compute_critical_path_with_slack(optimizer.graph)
print(f"\nBuild Order (Critical Path): {' → '.join(cp['critical_path'])}")
```

### Example 2: CI/CD Pipeline

```python
from dagoptimizer import DAGOptimizer

# GitHub Actions workflow
github_actions = [
    ('checkout', 'setup_python'),
    ('setup_python', 'install_deps'),
    ('install_deps', 'lint'),
    ('install_deps', 'test_unit'),
    ('install_deps', 'test_integration'),
    ('lint', 'build'),
    ('test_unit', 'build'),
    ('test_integration', 'build'),
    ('build', 'docker_build'),
    ('docker_build', 'deploy_staging'),
    ('deploy_staging', 'test_e2e'),
    ('test_e2e', 'deploy_prod'),
]

optimizer = DAGOptimizer(github_actions)
layers = optimizer.compute_layer_structure(optimizer.graph)

print("CI/CD Pipeline Parallelization Opportunities:")
for layer_num, jobs in sorted(layers['layers'].items()):
    print(f"  Step {layer_num}: {len(jobs)} job(s) can run in parallel")
    print(f"    Jobs: {', '.join(jobs)}")

print(f"\nMax Parallel Jobs: {layers['width']}")
print(f"Min Pipeline Duration: {layers['depth']} steps")
```

### Example 3: Apache Airflow DAG

```python
from dagoptimizer import DAGOptimizer

# Airflow data pipeline
airflow_dag = [
    ('start', 'extract_users'),
    ('start', 'extract_orders'),
    ('start', 'extract_products'),
    ('extract_users', 'transform_users'),
    ('extract_orders', 'transform_orders'),
    ('extract_products', 'transform_products'),
    ('transform_users', 'join_data'),
    ('transform_orders', 'join_data'),
    ('transform_products', 'join_data'),
    ('join_data', 'aggregate'),
    ('aggregate', 'load_warehouse'),
]

optimizer = DAGOptimizer(airflow_dag)
optimizer.transitive_reduction()

# Analyze
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
cp = optimizer.compute_critical_path_with_slack(optimizer.graph)

print("Airflow DAG Analysis:")
print(f"  Tasks: {metrics['num_nodes']}")
print(f"  Dependencies: {metrics['num_edges']}")
print(f"  Critical Path: {' → '.join(cp['critical_path'])}")
print(f"  Makespan: {cp['makespan']} time units")
print(f"  Bottleneck Tasks: {metrics['bottleneck_nodes']}")
```

---

## Publishing to PyPI

### Building the Package

```bash
# Install build tools
pip install build twine

# Build distributions
python -m build

# This creates:
# - dist/dagoptimizer-1.0.0.tar.gz (source)
# - dist/dagoptimizer-1.0.0-py3-none-any.whl (wheel)
```

### Testing Locally

```bash
# Install locally
pip install -e .

# Run tests
pytest

# Check package
twine check dist/*
```

### Publishing to PyPI

```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ dagoptimizer

# Publish to PyPI
twine upload dist/*
```

### Post-Publication

```bash
# Verify installation
pip install dagoptimizer

# Test
python -c "from dagoptimizer import DAGOptimizer; print('Success!')"
```

---

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs.git
cd Optimisation_of_DAGs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dagoptimizer --cov-report=html

# Run specific test file
pytest tests/test_optimizer.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/

# All checks
black src/ && flake8 src/ && mypy src/ && pytest
```

### Making a Release

1. Update version in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit changes: `git commit -am "Release v1.1.0"`
4. Tag release: `git tag v1.1.0`
5. Push: `git push && git push --tags`
6. Build: `python -m build`
7. Publish: `twine upload dist/*`

---

## Troubleshooting

### ImportError: No module named 'dagoptimizer'

```bash
# Make sure you installed the package
pip install dagoptimizer

# Or if developing locally
pip install -e .
```

### ValueError: The input graph must be a DAG

```python
# Your graph contains a cycle
# Check for cycles before creating optimizer

import networkx as nx

G = nx.DiGraph(edges)
if not nx.is_directed_acyclic_graph(G):
    cycles = list(nx.simple_cycles(G))
    print(f"Found {len(cycles)} cycle(s): {cycles}")
```

### Performance Issues with Large Graphs

```python
# For very large graphs, disable expensive metrics
optimizer = DAGOptimizer(edges)
optimizer.transitive_reduction()  # This is fast

# Only compute metrics you need
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
# Only access the metrics you actually need
```

---

## Additional Resources

- **GitHub Repository**: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs
- **Documentation**: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/wiki
- **Research Paper**: [Research Papers/DAG_Optimizer_Open_Source_Library.docx](../Research%20Papers/)
- **Benchmark Results**: [BENCHMARK_SUMMARY.md](BENCHMARK_SUMMARY.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **License**: [MIT License](../LICENSE)

---

## Support

- **Issues**: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/issues
- **Email**: sahilshrivastava28@gmail.com
- **Discussions**: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/discussions

---

**Happy Optimizing! 🚀**

