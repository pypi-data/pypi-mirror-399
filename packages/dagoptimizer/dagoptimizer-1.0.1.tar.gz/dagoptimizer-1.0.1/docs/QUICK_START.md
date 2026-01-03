# 🚀 Quick Start Guide

Get started with the DAG Optimizer library and demo application in 5 minutes!

---

## 📦 Installation

### Option 1: Library Only (Recommended for Production)

```bash
pip install dagoptimizer
```

### Option 2: Demo Application (For Exploration)

```bash
# 1. Clone the repository
git clone https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs.git
cd Optimisation_of_DAGs

# 2. Install library in editable mode
pip install -e .

# 3. Install demo dependencies
pip install -r requirements-demo.txt

# 4. Run Streamlit demo
streamlit run app.py

# 5. Open browser (automatic)
# http://localhost:8501
```

---

## 🎯 Basic Usage (Library)

### 1. Simple Optimization

```python
from dagoptimizer import DAGOptimizer

# Define your DAG (e.g., build dependencies)
edges = [
    ('compile', 'link'),
    ('compile', 'test'),
    ('link', 'test'),      # Redundant! test already depends on compile
    ('test', 'deploy')
]

# Create optimizer
optimizer = DAGOptimizer(edges)

# Apply transitive reduction
optimizer.transitive_reduction()

# Results
print(f"Reduced from {optimizer.original_graph.number_of_edges()} to {optimizer.graph.number_of_edges()} edges")
# Output: Reduced from 4 to 3 edges

# Get optimized edges
print(f"Optimized edges: {list(optimizer.graph.edges())}")
# Output: [('compile', 'link'), ('compile', 'test'), ('test', 'deploy')]
```

### 2. Advanced Analysis

```python
from dagoptimizer import DAGOptimizer

edges = [
    ('A', 'B'), ('B', 'C'), ('C', 'D'),
    ('A', 'C'), ('B', 'D'), ('A', 'D')  # Redundant edges
]

optimizer = DAGOptimizer(edges)
optimizer.transitive_reduction()

# PERT/CPM Critical Path Analysis
critical_path = optimizer.compute_critical_path_with_slack(optimizer.graph)
print(f"Critical Path: {critical_path['critical_path']}")
print(f"Makespan: {critical_path['makespan']} time units")
print(f"Parallel Time Saved: {critical_path['parallel_time_saved']:.1%}")

# Layer Analysis (Parallelism Potential)
layers = optimizer.compute_layer_structure(optimizer.graph)
print(f"Max Parallel Tasks: {layers['width']}")
print(f"Min Execution Depth: {layers['depth']}")

# Edge Criticality (Which edges are critical?)
criticality = optimizer.compute_edge_criticality(optimizer.graph)
print(f"Critical Edges: {len(criticality['critical_edges'])}")
print(f"Redundant Edges: {len(criticality['redundant_edges'])}")

# Comprehensive Metrics
metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
print(f"Efficiency Score: {metrics['efficiency_score']:.2%}")
print(f"Graph Density: {metrics['density']:.4f}")
```

### 3. Node Merging

```python
from dagoptimizer import DAGOptimizer

# DAG with equivalent nodes (same dependencies)
edges = [
    ('A', 'C'), ('A', 'D'),
    ('B', 'C'), ('B', 'D'),  # B has same dependencies as A
    ('C', 'E'), ('D', 'E')
]

optimizer = DAGOptimizer(edges)

# Merge equivalent nodes
optimizer.merge_equivalent_nodes()
print(f"Merged to {optimizer.graph.number_of_nodes()} nodes")

# Get merged groups
metadata = optimizer.metadata()
print(f"Merged groups: {metadata.get('merged_nodes', {})}")
```

---

## 🎨 Demo Application Features

The Streamlit demo provides an interactive interface to explore the library:

### Input Methods

1. **Upload CSV/Excel**: Load DAGs from files
2. **Manual Input**: Paste edge lists directly
3. **Random Generation**: Create test DAGs with custom size/density
4. **ML Templates**: Pre-built workflow examples

### Optimization Options

- ✅ **Transitive Reduction**: Remove redundant edges (adaptive algorithm)
- ✅ **Node Merging**: Combine equivalent nodes
- ✅ **Cycle Handling**: Automatic or error display

### Analysis Views

- 📊 **Metrics Comparison**: 25+ metrics before/after
- 🎯 **PERT/CPM Analysis**: Critical path, makespan, slack times
- 📊 **Layer Analysis**: Parallelism width, depth, efficiency
- 🔗 **Edge Criticality**: Critical vs redundant edge classification

### Export Options

- 📄 **Markdown Report**: Comprehensive metrics report
- 📊 **CSV/JSON**: Optimized graph data
- 📷 **PNG**: Visualizations
- 🗄️ **Neo4j**: Database export

---

## 🤖 ML Workflow Templates

The demo includes ready-to-use templates for common ML scenarios:

### 1. ML Training Pipeline

```
DataIngestion → DataValidation → FeatureEngineering → DataSplit
→ ModelTraining/ModelValidation → ModelEvaluation → ModelRegistry
→ Deployment → Monitoring
```

### 2. LangGraph Agent Workflow

```
Input → Router → [SearchAgent, AnalysisAgent, CodeAgent]
→ Aggregator → QualityCheck → ResponseGenerator → Output
```

### 3. Distributed Training

```
DataSharding → [Worker1, Worker2, Worker3, Worker4]
→ GradientAggregation → ParameterUpdate → Checkpoint → Evaluation
```

### 4. Feature Engineering Pipeline

```
RawData → MissingValueHandler → OutlierDetection
→ [NumericalScaling, CategoricalEncoding] → FeatureSelection
→ FeatureUnion → FinalDataset
```

---

## 🆘 Troubleshooting

### Library Installation Issues

```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install dagoptimizer -v

# If NetworkX conflicts, install specific version
pip install networkx==2.8.8 dagoptimizer
```

### Demo App Issues

```bash
# Streamlit not found
pip install streamlit>=1.28.0

# Missing dependencies
pip install -r requirements-demo.txt

# Port already in use
streamlit run app.py --server.port 8502
```

### Import Errors

```python
# If you get "No module named 'dagoptimizer'"
# Make sure you're in the right environment
import sys
print(sys.path)

# Install in editable mode for development
pip install -e .
```

---

## 📚 Next Steps

1. **Read the API Reference**: See `README.md` for complete API documentation
2. **Explore Use Cases**: Check `docs/PIP_PACKAGE_GUIDE.md` for ML applications
3. **Review Research**: Read the paper in `Research Papers/` folder
4. **Contribute**: See `CONTRIBUTING.md` for guidelines

---

## 🎉 You're Ready!

### For Library Usage:
```bash
pip install dagoptimizer
```

### For Demo Exploration:
```bash
git clone <repo>
pip install -r requirements-demo.txt
streamlit run app.py
```

**Start optimizing your DAGs!** 🚀
