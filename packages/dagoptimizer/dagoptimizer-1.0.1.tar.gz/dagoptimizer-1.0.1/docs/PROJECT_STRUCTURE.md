# 📁 Project Structure

This document provides an overview of the DAG Optimizer library's file organization.

---

## 🏗️ High-Level Structure

```
dag-optimizer/
├── 📂 src/                  # Core optimization library
├── 📂 docs/                 # Comprehensive documentation
├── 📂 Research Papers/      # Academic references (gitignored)
├── 📂 DAG_Dataset/          # Benchmark test cases (gitignored)
├── 📂 Benchmark_Results/    # Test results (gitignored)
├── 📄 app.py                # Streamlit demo application
├── 📄 setup.py              # Package setup configuration
├── 📄 pyproject.toml        # Modern packaging configuration
├── 📄 README.md             # Main project documentation
├── 📄 CONTRIBUTING.md       # Contribution guidelines
├── 📄 CODE_OF_CONDUCT.md    # Community standards
├── 📄 CHANGELOG.md          # Version history
├── 📄 MANIFEST.in           # Package manifest
├── 📄 LICENSE               # MIT License
├── 📄 requirements.txt      # Library dependencies
├── 📄 requirements-demo.txt # Demo app dependencies
└── 📄 .gitignore            # Git exclusions
```

---

## 📂 Detailed Structure

### Core Library (`src/dagoptimizer/`)

Python library implementing DAG optimization algorithms.

```
src/
└── dagoptimizer/
    ├── __init__.py           # Package exports
    └── dag_class.py          # DAGOptimizer class (main algorithm)
```

**Key Algorithms in `dag_class.py`**:
- `transitive_reduction()`: Adaptive algorithm (DFS for sparse, Floyd-Warshall for dense)
- `compute_critical_path_with_slack()`: PERT/CPM analysis with earliest/latest start times
- `compute_layer_structure()`: Width and parallelism calculation for concurrent execution
- `compute_edge_criticality()`: Critical vs redundant edge classification
- `evaluate_graph_metrics()`: 25+ comprehensive graph metrics
- `merge_equivalent_nodes()`: Combine nodes with identical dependencies
- `metadata()`: Export complete graph state with attributes

### Demo Application (`app.py`)

Streamlit application for visual demonstration of the library capabilities.

**Features**:
- 📤 Multiple input methods (CSV, text, random, ML templates)
- 🎯 Real-time optimization with adaptive algorithm selection
- 📊 Side-by-side graph visualization
- 📈 Comprehensive metrics display (25+ metrics)
- 🔬 PERT/CPM critical path analysis
- 📊 Layer-based parallelism analysis
- 🔗 Edge criticality classification
- 📄 Export options (Markdown, CSV, JSON, PNG)
- 🗄️ Neo4j database integration

**ML Workflow Templates**:
- ML Training Pipeline (Data Ingestion → Training → Deployment)
- LangGraph Agent Workflow (Router → Agents → Aggregator)
- Distributed Training (Workers → Gradient Aggregation → Update)
- Feature Engineering Pipeline (Raw Data → Transformations → Features)

### Documentation (`docs/`)

Comprehensive project documentation.

```
docs/
├── README.md                             # Documentation index
├── QUICK_START.md                        # 5-minute setup guide
├── PIP_PACKAGE_GUIDE.md                  # Pip package documentation
├── BUILD_AND_PUBLISH.md                  # PyPI publishing guide
├── BENCHMARK_SUMMARY.md                  # 995-DAG benchmark results
├── REAL_NUMBERS_FOR_PAPER.md            # Research paper data
├── MATHEMATICAL_FEATURES_ROADMAP.md     # Mathematical analysis guide
├── PIP_PACKAGE_REFACTORING_SUMMARY.md   # Refactoring history
├── REFACTORING_COMPLETE.md              # Completion summary
├── GITHUB_WIKI_GUIDE.md                 # GitHub Wiki setup
└── PROJECT_STRUCTURE.md                 # This file
```

### Research Assets (Git-Ignored)

These folders contain research materials not pushed to GitHub.

```
Research Papers/                  # Academic papers (gitignored)
├── DAG_Optimization_ML_Workflows.docx
├── DAGs with No Curl.pdf
├── DAGs with NO TEARS.pdf
└── ...

DAG_Dataset/                      # 1000 synthetic DAGs (gitignored)
├── dag_0000.json
├── ...
└── dataset_metadata.json

Benchmark_Results/                # Test results (gitignored)
├── benchmark_results.json
└── paper_tables.txt

scripts/                          # Generation utilities (gitignored)
├── generate_dag_dataset.py
└── benchmark_dags.py
```

---

## 🔑 Key Entry Points

### For Users (Library)

1. **Install Library**: `pip install dagoptimizer`
2. **Import and Use**:
   ```python
   from dagoptimizer import DAGOptimizer
   
   edges = [('A', 'B'), ('B', 'C'), ('A', 'C')]
   optimizer = DAGOptimizer(edges)
   optimizer.transitive_reduction()
   ```
3. **Read Documentation**: `README.md` → `docs/PIP_PACKAGE_GUIDE.md`

### For Users (Demo App)

1. **Clone Repository**: `git clone https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs.git`
2. **Install Dependencies**: `pip install -r requirements-demo.txt`
3. **Run Demo**: `streamlit run app.py`
4. **Open Browser**: http://localhost:8501

### For Developers

1. **Core Algorithm**: `src/dagoptimizer/dag_class.py`
2. **Package Setup**: `setup.py` and `pyproject.toml`
3. **Demo Application**: `app.py`

### For Researchers

1. **Research Paper**: `Research Papers/DAG_Optimization_ML_Workflows.docx`
2. **Benchmark Data**: `docs/BENCHMARK_SUMMARY.md`

---

## 📦 Dependencies

### Library Dependencies (`requirements.txt`)

- **NetworkX** (>=2.5): Graph algorithms
- **NumPy** (>=1.20): Numerical operations
- **SciPy** (>=1.6): Scientific computing
- **python-docx** (>=0.8.11): DOCX generation
- **python-dotenv** (>=0.19.0): Environment variables

### Demo App Dependencies (`requirements-demo.txt`)

- **Streamlit** (>=1.28.0): Web framework
- **Matplotlib** (>=3.5.0): Visualization
- **Pandas** (>=1.3.0): Data manipulation
- **Neo4j** (>=4.4.0): Database integration (optional)

---

## 📊 Data Flow

### Library Usage

```
User Code → DAGOptimizer → Optimization Algorithms → Results
```

### Demo App Flow

```
User Input (Streamlit) → app.py → DAGOptimizer → Results → Display/Export
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `setup.py` | Package setup and PyPI configuration |
| `pyproject.toml` | Modern Python packaging |
| `MANIFEST.in` | Distribution file manifest |
| `requirements.txt` | Library dependencies |
| `requirements-demo.txt` | Demo dependencies |
| `.gitignore` | Version control exclusions |
| `CHANGELOG.md` | Version history |

---

## 📈 Repository Positioning

**PRIMARY**: Pip-installable Python library (`dagoptimizer`)  
**SECONDARY**: Research paper and mathematical framework  
**TERTIARY**: Streamlit demo for visualization  

---

**This structure is designed for clarity, ease of use, and professional distribution!** 🚀
