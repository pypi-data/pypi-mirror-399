# 📚 GitHub Wiki Setup Guide

This guide explains how to set up your GitHub Wiki with the research paper and supporting documentation.

---

## 📋 Table of Contents

1. [Enable Wiki](#1-enable-wiki)
2. [Create Wiki Pages](#2-create-wiki-pages)
3. [Upload Research Paper](#3-upload-research-paper)
4. [Add Visualizations](#4-add-visualizations)
5. [Link from README](#5-link-from-readme)
6. [Recommended Wiki Structure](#6-recommended-wiki-structure)

---

## 1. Enable Wiki

1. Go to your GitHub repository
2. Click **Settings** tab
3. Scroll to **Features** section
4. Check ✅ **Wikis**
5. Click **Save changes**

---

## 2. Create Wiki Pages

### Home Page

Navigate to the **Wiki** tab and create the home page:

```markdown
# Advanced DAG Optimization Framework Wiki

Welcome to the comprehensive documentation for the Advanced DAG Optimization Framework!

## 📑 Contents

- [Research Paper](Research-Paper) - Full academic paper with mathematical proofs
- [Algorithm Details](Algorithm-Details) - In-depth algorithm explanations
- [Benchmark Results](Benchmark-Results) - Complete testing results and analysis
- [API Reference](API-Reference) - Backend and frontend API documentation
- [Tutorials](Tutorials) - Step-by-step guides and examples
- [FAQ](FAQ) - Frequently asked questions

## 🎯 Quick Links

- [GitHub Repository](../)
- [Quick Start Guide](../QUICK_START.md)
- [Issue Tracker](../issues)
- [Discussions](../discussions)

## 📊 Key Results

**Validated on 995 test cases:**
- 42.9% average edge reduction
- 68-87% reduction for dense graphs
- 25.6× overhead for 5× feature count

See the [full benchmark results](Benchmark-Results) for details.
```

---

## 3. Upload Research Paper

### Option A: Direct Upload (Recommended)

1. Click **Wiki** tab
2. Click **Create new page**
3. Name it `Research-Paper`
4. Add content (see template below)
5. Upload images via drag-and-drop
6. Click **Save Page**

### Option B: Convert DOCX to Markdown

Use a tool like [Pandoc](https://pandoc.org/):

```bash
# Install pandoc
# Windows: choco install pandoc
# Mac: brew install pandoc
# Linux: sudo apt install pandoc

# Convert DOCX to Markdown
pandoc "Research Papers/DAG_Optimization_Sahil_Shrivastava.docx" \
  -f docx \
  -t gfm \
  -o wiki_research_paper.md \
  --extract-media=wiki_images

# This creates:
# - wiki_research_paper.md (main content)
# - wiki_images/ (extracted images and equations)
```

### Research Paper Template

```markdown
# Advanced DAG Optimization: Adaptive Transitive Reduction with Integrated PERT/CPM Analysis

**Author**: Sahil Shrivastava  
**Contact**: sahilshrivastava28@gmail.com  
**Date**: December 2025  
**Keywords**: Directed Acyclic Graph, Transitive Reduction, Graph Optimization, PERT/CPM, Critical Path Analysis

---

## Abstract

This paper presents a comprehensive framework for Directed Acyclic Graph (DAG) optimization
combining adaptive transitive reduction with integrated PERT/CPM critical path analysis.
Experimental validation on a comprehensive benchmark of 995 DAGs demonstrates **42.9% average
edge reduction** while preserving reachability, with **dense graphs achieving 68-87% reduction**.

[Full abstract from your research paper...]

---

## 1. Introduction

### 1.1 Motivation

[Content from Section 1.1...]

### 1.2 Contributions

[Content from Section 1.2...]

---

## 2. Background and Related Work

### 2.1 Transitive Reduction

[Content...]

### 2.2 Critical Path Analysis

[Content...]

---

## 3. Methodology

### 3.1 Adaptive Transitive Reduction

**Algorithm 1: Density-Based Algorithm Selection**

```python
def adaptive_transitive_reduction(G):
    density = compute_density(G)
    
    if density < 0.1:
        return dfs_transitive_reduction(G)  # O(n·m)
    else:
        return matrix_transitive_reduction(G)  # O(n³)
```

![Algorithm Flowchart](wiki_images/algorithm_flowchart.png)

[More content...]

---

## 4. Mathematical Formulations

### 4.1 Efficiency Score

The efficiency score E is defined as:

$$E = \frac{(1 - R) + (1 - D) + C}{3}$$

Where:
- R = Redundancy Ratio
- D = Graph Density
- C = Compactness Score

[More formulas...]

---

## 5. Experimental Results

### 5.1 Dataset Description

We generated 1,000 synthetic DAGs across 7 categories:

| Category | Count | Nodes | Edges | Density |
|----------|-------|-------|-------|---------|
| Sparse Small | 195 | 10-50 | ~15 | 0.02-0.05 |
| Sparse Medium | 200 | 50-200 | ~286 | 0.01-0.05 |
| Dense Medium | 100 | 40-100 | ~1,057 | 0.3-0.5 |

### 5.2 Performance Results

![Benchmark Results](wiki_images/benchmark_chart.png)

**Table 1: Comprehensive Benchmark Results**

| Category | Tested | Edge Reduction | Outcome |
|----------|--------|----------------|---------|
| Overall | 995 | 42.9% | ✅ Matched prediction |

[More results...]

---

## 6. Discussion

### 6.1 Expected vs Actual Results

We predicted approximately 40% average edge reduction. Experimental results yielded
**42.9%**—closely matching our prediction and validating our theoretical framework.

[More discussion...]

---

## 7. Conclusion

This work presents a comprehensive DAG optimization framework validated on 995 test cases...

[Full conclusion...]

---

## 8. Future Work

- Incremental transitive reduction algorithms
- Distributed graph processing for large-scale DAGs
- Machine learning for optimal algorithm selection

---

## References

1. Aho, A. V., Garey, M. R., & Ullman, J. D. (1972). The transitive reduction of a directed graph.
2. [Additional references...]

---

## Appendix A: Complexity Analysis

[Detailed complexity proofs...]

## Appendix B: Benchmark Data

Full benchmark data available at: [DAG_Dataset/](../DAG_Dataset/)

---

**Citation**:
```bibtex
@software{shrivastava2025dag,
  author = {Shrivastava, Sahil},
  title = {Advanced DAG Optimization Framework},
  year = {2025},
  url = {https://github.com/YourUsername/dag-optimization-framework}
}
```
```

---

## 4. Add Visualizations

### Create Diagrams

Use tools like:
- **Draw.io**: For flowcharts and architecture diagrams
- **Python/Matplotlib**: For benchmark charts
- **Graphviz**: For graph visualizations
- **LaTeX/TikZ**: For mathematical diagrams

### Example: Create Benchmark Chart

```python
import matplotlib.pyplot as plt
import pandas as pd

# Load benchmark data
data = pd.read_json('Benchmark_Results/benchmark_results.json')

# Create chart
fig, ax = plt.subplots(figsize=(12, 6))
categories = ['Sparse\nSmall', 'Sparse\nMedium', 'Sparse\nLarge', 
              'Medium\nSmall', 'Medium\nMedium', 'Dense\nSmall', 'Dense\nMedium']
reductions = [1.2, 12.0, 16.5, 40.5, 75.2, 68.0, 86.9]

bars = ax.bar(categories, reductions, color=['#3b82f6', '#3b82f6', '#3b82f6',
                                              '#10b981', '#10b981', '#f59e0b', '#f59e0b'])
ax.set_ylabel('Edge Reduction (%)', fontsize=12)
ax.set_title('Edge Reduction by Graph Category (995 DAGs Tested)', fontsize=14, fontweight='bold')
ax.set_ylim(0, 100)
ax.axhline(y=42.9, color='red', linestyle='--', label='Overall Average (42.9%)')
ax.legend()

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('wiki_images/benchmark_chart.png', dpi=300, bbox_inches='tight')
print("✅ Saved to wiki_images/benchmark_chart.png")
```

### Upload Images to Wiki

1. Edit a wiki page
2. Drag and drop images directly into the editor
3. GitHub auto-uploads to `wiki_images/` folder
4. Use markdown syntax: `![Alt Text](wiki_images/filename.png)`

---

## 5. Link from README

Update the main `README.md` to link to wiki pages:

```markdown
## 📄 Research Paper

This framework is backed by rigorous academic research. The full paper is available in the
[GitHub Wiki](../../wiki/Research-Paper) and includes:

### Key Contributions

1. **Adaptive Transitive Reduction Algorithm** - [Details](../../wiki/Algorithm-Details#adaptive-tr)
2. **Integrated PERT/CPM Analysis** - [Details](../../wiki/Algorithm-Details#pert-cpm)
3. **Benchmark Results** - [Full Results](../../wiki/Benchmark-Results)

**Read the full paper**: [Advanced DAG Optimization](../../wiki/Research-Paper)
```

---

## 6. Recommended Wiki Structure

### Essential Pages

1. **Home** - Landing page with navigation
2. **Research-Paper** - Full academic paper
3. **Algorithm-Details** - In-depth algorithm explanations
4. **Benchmark-Results** - Complete testing results
5. **API-Reference** - Backend and frontend API docs
6. **Tutorials** - Step-by-step guides
7. **FAQ** - Common questions

### Optional Pages

8. **Mathematical-Proofs** - Detailed proofs and complexity analysis
9. **Case-Studies** - Real-world applications
10. **Performance-Tuning** - Optimization tips
11. **Troubleshooting** - Common issues and solutions
12. **Roadmap** - Future development plans

---

## 📊 Visual Content to Include

### 1. Architecture Diagram

Show the system architecture (frontend, backend, database):

```
[React Frontend] <--REST API--> [FastAPI Backend] <--> [Neo4j]
                                       |
                               [DAGOptimizer Core]
                                       |
                          +------------+------------+
                          |            |            |
                     [Transitive]  [PERT/CPM]  [Metrics]
                     [Reduction]   [Analysis]  [Calculator]
```

### 2. Algorithm Flowchart

Show the adaptive algorithm selection process.

### 3. Benchmark Charts

- **Edge Reduction by Category** (bar chart)
- **Time Overhead by Graph Size** (line chart)
- **Density vs Reduction Correlation** (scatter plot)

### 4. Before/After Graphs

Visual examples of:
- Original DAG with redundant edges
- Optimized DAG after transitive reduction
- Critical path highlighted

### 5. UI Screenshots

Show the application interface:
- Input section with different modes
- Optimization panel
- Results section with metrics comparison
- Interactive graph visualization
- Research insights tab

---

## 🎨 Creating High-Quality Visuals

### Graph Visualizations

Use the app itself or create custom ones:

```python
import networkx as nx
import matplotlib.pyplot as plt

# Example: Before/After comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Original graph
G_orig = nx.DiGraph([(1,2), (2,3), (1,3), (2,4), (3,4), (1,4)])
pos = nx.spring_layout(G_orig)
nx.draw(G_orig, pos, ax=ax1, with_labels=True, node_color='lightblue',
        node_size=500, font_size=12, arrows=True, arrowsize=20)
ax1.set_title('Original DAG (6 edges, 3 redundant)', fontsize=14, fontweight='bold')

# Optimized graph
G_opt = nx.DiGraph([(1,2), (2,3), (2,4), (3,4)])  # Removed (1,3), (1,4)
nx.draw(G_opt, pos, ax=ax2, with_labels=True, node_color='lightgreen',
        node_size=500, font_size=12, arrows=True, arrowsize=20)
ax2.set_title('Optimized DAG (4 edges, 33% reduction)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('wiki_images/before_after_example.png', dpi=300)
```

### LaTeX for Mathematical Formulas

GitHub Wiki supports LaTeX via `$$` blocks:

```markdown
The efficiency score is calculated as:

$$E = \frac{(1 - R) + (1 - D) + C}{3}$$

Where the redundancy ratio R is defined as:

$$R = \frac{|TC| - |TR|}{|E|}$$
```

---

## ✅ Checklist

Before publishing your wiki:

- [ ] Enable Wiki in repository settings
- [ ] Create Home page with navigation
- [ ] Upload full research paper
- [ ] Add all visualizations and charts
- [ ] Include benchmark results and tables
- [ ] Add API reference documentation
- [ ] Create at least 2-3 tutorials
- [ ] Add FAQ page
- [ ] Link wiki from main README
- [ ] Proofread all content
- [ ] Test all internal links
- [ ] Verify all images display correctly

---

## 📝 Markdown Tips for Wiki

### Tables

```markdown
| Algorithm | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| DFS-based TR | O(n·m) | O(n + m) |
| Matrix-based TR | O(n³) | O(n²) |
```

### Code Blocks

```markdown
```python
def example():
    return "Syntax highlighted code"
```
```

### Callouts

```markdown
> **Note**: Important information here

> **Warning**: Be careful with this

> **Tip**: Pro tip for users
```

### Internal Links

```markdown
See [Algorithm Details](Algorithm-Details) for more information.

Jump to [Section 3.2](Research-Paper#32-pert-cpm-analysis).
```

---

## 🚀 Publishing Your Wiki

1. **Draft First**: Write content in a local markdown editor
2. **Review**: Proofread and check formatting
3. **Upload Images**: Prepare all visualizations
4. **Create Pages**: Add pages to wiki one by one
5. **Interlink**: Add navigation between pages
6. **Announce**: Share the wiki in your README and social media

---

## 📞 Need Help?

- **GitHub Wiki Documentation**: https://docs.github.com/en/communities/documenting-your-project-with-wikis
- **Markdown Guide**: https://www.markdownguide.org/
- **LaTeX Math**: https://en.wikibooks.org/wiki/LaTeX/Mathematics

---

**Your GitHub Wiki will be the comprehensive documentation hub for your DAG optimization research!** 📚✨

