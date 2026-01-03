# DAG Optimizer - Streamlit Demo Application
import pandas as pd
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from io import BytesIO, StringIO
from neo4j import GraphDatabase

# DAG optimizer (updated import path)
from src.dagoptimizer.dag_class import DAGOptimizer

# --- Configuration ---
st.set_page_config(
    page_title="DAG Optimizer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---


def aggregate_edge_classes(df, source_col, target_col, class_col=None):
    """
    Collapse DataFrame rows into unique edges and collect classes per edge.
    Returns:
      edges: list of (u, v) tuples
      edge_attrs: dict mapping (u, v) -> sorted list of classes
    """
    access_map = defaultdict(set)
    for _, row in df.iterrows():
        u = row[source_col]
        v = row[target_col]
        if class_col and class_col in df.columns and pd.notna(row[class_col]):
            c = row[class_col]
            access_map[(u, v)].add(c)
        else:
            access_map[(u, v)]  # ensure key exists
    edges = list(access_map.keys())
    edge_attrs = {e: sorted(access_map[e]) for e in access_map}
    return edges, edge_attrs


def get_ml_pipeline_example():
    """ML Training Pipeline example"""
    edges = [
        ("DataIngestion", "DataValidation"),
        ("DataValidation", "FeatureEngineering"),
        ("FeatureEngineering", "DataSplit"),
        ("DataSplit", "ModelTraining"),
        ("DataSplit", "ModelValidation"),
        ("ModelTraining", "ModelEvaluation"),
        ("ModelValidation", "ModelEvaluation"),
        ("ModelEvaluation", "ModelRegistry"),
        ("ModelRegistry", "Deployment"),
        ("Deployment", "Monitoring"),
    ]
    edge_attrs = {e: [] for e in edges}
    return edges, edge_attrs


def get_langgraph_example():
    """LangGraph Agent workflow example"""
    edges = [
        ("Input", "Router"),
        ("Router", "SearchAgent"),
        ("Router", "AnalysisAgent"),
        ("Router", "CodeAgent"),
        ("SearchAgent", "Aggregator"),
        ("AnalysisAgent", "Aggregator"),
        ("CodeAgent", "Aggregator"),
        ("Aggregator", "QualityCheck"),
        ("QualityCheck", "ResponseGenerator"),
        ("ResponseGenerator", "Output"),
    ]
    edge_attrs = {e: [] for e in edges}
    return edges, edge_attrs


def get_distributed_training_example():
    """Distributed Training example"""
    edges = [
        ("DataSharding", "Worker1"),
        ("DataSharding", "Worker2"),
        ("DataSharding", "Worker3"),
        ("DataSharding", "Worker4"),
        ("Worker1", "GradientAggregation"),
        ("Worker2", "GradientAggregation"),
        ("Worker3", "GradientAggregation"),
        ("Worker4", "GradientAggregation"),
        ("GradientAggregation", "ParameterUpdate"),
        ("ParameterUpdate", "Checkpoint"),
        ("Checkpoint", "Evaluation"),
    ]
    edge_attrs = {e: [] for e in edges}
    return edges, edge_attrs


def get_feature_engineering_example():
    """Feature Engineering pipeline example"""
    edges = [
        ("RawData", "MissingValueHandler"),
        ("MissingValueHandler", "OutlierDetection"),
        ("OutlierDetection", "NumericalScaling"),
        ("OutlierDetection", "CategoricalEncoding"),
        ("NumericalScaling", "FeatureSelection"),
        ("CategoricalEncoding", "FeatureSelection"),
        ("FeatureSelection", "FeatureUnion"),
        ("FeatureUnion", "FinalDataset"),
    ]
    edge_attrs = {e: [] for e in edges}
    return edges, edge_attrs


def format_metric_value(value):
    """Format metric values for display"""
    if isinstance(value, (int, float)):
        if isinstance(value, float):
            return f"{value:.4f}"
        return str(value)
    elif isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)


def generate_metrics_report(optimizer):
    """Generate a comprehensive markdown report"""
    om = optimizer.evaluate_graph_metrics(optimizer.original_graph)
    nm = optimizer.evaluate_graph_metrics(optimizer.graph)

    report = f"""# DAG Optimization Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Original Nodes: {om.get('num_nodes', 'N/A')}
- Optimized Nodes: {nm.get('num_nodes', 'N/A')}
- Original Edges: {om.get('num_edges', 'N/A')}
- Optimized Edges: {nm.get('num_edges', 'N/A')}
- Optimization Method: {optimizer.optimization_method}

## Detailed Metrics Comparison

| Metric | Original | Optimized | Change |
|--------|----------|-----------|--------|
"""

    for key in om.keys():
        if key in [
            'critical_path_analysis',
            'layer_analysis',
                'edge_criticality']:
            continue  # Skip complex nested structures for table
        orig_val = format_metric_value(om.get(key, 'N/A'))
        opt_val = format_metric_value(nm.get(key, 'N/A'))

        # Calculate percentage change for numeric values
        change = "N/A"
        if isinstance(
                om.get(key), (int, float)) and isinstance(
                nm.get(key), (int, float)):
            if om[key] != 0:
                pct_change = ((nm[key] - om[key]) / om[key]) * 100
                change = f"{pct_change:+.2f}%"

        report += f"| {key} | {orig_val} | {opt_val} | {change} |\n"

    # Add PERT/CPM Analysis
    if 'critical_path_analysis' in nm:
        cpa = nm['critical_path_analysis']
        report += f"""
## PERT/CPM Critical Path Analysis

- **Makespan**: {cpa.get('makespan', 'N/A')} time units
- **Critical Path Length**: {len(cpa.get('critical_path', []))} nodes
- **Parallel Time Saved**: {cpa.get('parallel_time_saved', 'N/A')} time units
- **Critical Path**: {' → '.join(cpa.get('critical_path', []))}

### Node Slack Times
"""
        if 'node_slack' in cpa:
            for node, slack in sorted(
                    cpa['node_slack'].items(), key=lambda x: x[1]):
                report += f"- **{node}**: {slack} time units\n"

    # Add Layer Analysis
    if 'layer_analysis' in nm:
        la = nm['layer_analysis']
        report += f"""
## Layer-Based Parallelism Analysis

- **Width (Max Parallelism)**: {la.get('width', 'N/A')} nodes
- **Depth (Sequential Stages)**: {la.get('depth', 'N/A')} layers
- **Width Efficiency**: {la.get('width_efficiency', 0):.2%}
- **Average Layer Size**: {la.get('avg_layer_size', 0):.2f} nodes

### Layer Structure
"""
        if 'layers' in la:
            for layer_id, nodes in sorted(
                la['layers'].items(), key=lambda x: int(
                    x[0])):
                report += f"- **Layer {layer_id}**: {', '.join(nodes)}\n"

    # Add Edge Criticality
    if 'edge_criticality' in nm:
        ec = nm['edge_criticality']
        report += f"""
## Edge Criticality Analysis

- **Critical Edges**: {ec.get('critical_edges_count', 'N/A')}
- **Redundant Edges**: {ec.get('redundant_edges_count', 'N/A')}
- **Criticality Ratio**: {ec.get('criticality_ratio', 0):.2%}

### Critical Edges (Cannot be removed)
"""
        if 'critical_edges' in ec:
            for edge in ec['critical_edges'][:10]:  # Show first 10
                if isinstance(edge, list) and len(edge) == 2:
                    report += f"- {edge[0]} → {edge[1]}\n"

        report += "\n### Redundant Edges (Can be removed via transitive reduction)\n"
        if 'redundant_edges' in ec:
            for edge in ec['redundant_edges'][:10]:  # Show first 10
                if isinstance(edge, list) and len(edge) == 2:
                    report += f"- {edge[0]} → {edge[1]}\n"

    report += f"""
---
*Generated by DAG Optimizer - https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs*
"""

    return report


# --- Session State ---
if "edges" not in st.session_state:
    st.session_state.edges = None
if "edge_attrs" not in st.session_state:
    st.session_state.edge_attrs = {}
if "optimizer" not in st.session_state:
    st.session_state.optimizer = None
if "did_optimize" not in st.session_state:
    st.session_state.did_optimize = False

# --- Sidebar ---
with st.sidebar:
    st.header("🔧 Optimization Options")

    st.markdown("### Algorithm Selection")
    do_tr = st.checkbox(
        "Transitive Reduction",
        value=True,
        help="Remove redundant edges that can be inferred (adaptive: DFS for sparse, Floyd-Warshall for dense)")
    do_merge = st.checkbox("Merge Equivalent Nodes", value=True,
                           help="Combine nodes with identical dependencies")

    optimize = st.button(
        "🚀 Optimize DAG",
        type="primary",
        use_container_width=True)

    st.markdown("### Cycle Handling")
    handle_cycles = st.selectbox(
        "If cycles are detected:",
        ["Show error", "Automatically remove cycles"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📊 Export Options")

    if st.session_state.did_optimize:
        # Export Metrics Report
        report_md = generate_metrics_report(st.session_state.optimizer)
        st.download_button(
            "📄 Download Metrics Report (Markdown)",
            data=report_md,
            file_name=f"dag_metrics_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True)

        # Export Optimized Graph as CSV
        opt = st.session_state.optimizer
        edges_df = pd.DataFrame(
            list(
                opt.graph.edges()),
            columns=[
                'source',
                'target'])
        csv = edges_df.to_csv(index=False)
        st.download_button(
            "📊 Download Optimized Graph (CSV)",
            data=csv,
            file_name=f"optimized_dag_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True)

        # Export as JSON
        meta = opt.metadata()
        # Convert tuple keys to strings for JSON serialization
        if 'edge_attributes' in meta:
            meta['edge_attributes'] = {
                f"{u}->{v}": cls for (u, v), cls in meta['edge_attributes'].items()}

        st.download_button(
            "📦 Download Metadata (JSON)",
            data=json.dumps(
                meta,
                indent=2),
            file_name=f"dag_metadata_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True)

    st.markdown("---")
    st.markdown("### 🗄️ Neo4j Export")

    if st.session_state.optimizer:
        graph_target = st.radio(
            "Push which graph?",
            ["Original DAG", "Optimized DAG"],
            index=1
        )
        uri = st.text_input("Neo4j URI", value="bolt://localhost:7687")
        usr = st.text_input("Username", value="neo4j")
        pwd = st.text_input("Password", type="password")
        push = st.button("Push to Neo4j", use_container_width=True)

# --- Main UI ---
st.title("🗺️ DAG Optimizer")
st.markdown("""
**Advanced Python library for DAG optimization with adaptive algorithms, PERT/CPM analysis, and comprehensive metrics.**

This demo application showcases the `dagoptimizer` library capabilities.
""")

# Tabs for different input modes
tab1, tab2, tab3, tab4 = st.tabs(
    ["📂 Upload File", "✍️ Manual Input", "🎲 Random DAG", "📚 ML Examples"])

with tab1:
    st.markdown("### Upload CSV or Excel")
    uploaded_file = st.file_uploader(
        "Upload file with columns: source, target, classes (optional)",
        type=["csv", "xlsx"]
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(
            ".csv") else pd.read_excel(uploaded_file)
        st.write("**Preview:**")
        st.dataframe(df.head(), use_container_width=True)

        # Optional filters
        col1, col2 = st.columns(2)

        with col1:
            if "report_name" in df.columns:
                sel = st.selectbox(
                    "Filter by report_name",
                    df['report_name'].unique())
                df = df[df['report_name'] == sel]

        with col2:
            has_classes = 'classes' in df.columns
            if has_classes:
                cls_choices = df['classes'].unique().tolist()
                sel_classes = st.multiselect(
                    "Include access classes", cls_choices, default=cls_choices)
                df = df[df['classes'].isin(sel_classes)]

        # Select columns
        cols = df.columns.tolist()
        col1, col2 = st.columns(2)
        with col1:
            source_col = st.selectbox(
                "Source Column", cols, index=0 if len(cols) > 0 else None)
        with col2:
            target_col = st.selectbox(
                "Target Column", cols, index=1 if len(cols) > 1 else None)

        if st.button("🔨 Build DAG from File", type="primary"):
            with st.spinner("Building DAG..."):
                # Aggregate edges and classes
                new_edges, edge_attrs = aggregate_edge_classes(
                    df, source_col, target_col, 'classes' if has_classes else None)

                # Show components
                G0 = nx.DiGraph(new_edges)
                comps = nx.number_weakly_connected_components(G0)
                st.info(
                    f"📊 Uploaded DAG has **{comps}** weakly connected component(s).")

                # Cycle handling
                if not nx.is_directed_acyclic_graph(G0):
                    if handle_cycles == "Show error":
                        st.error("⚠️ Graph contains cycles—cannot optimize.")
                        for cyc in list(
                                nx.simple_cycles(G0))[:5]:  # Show first 5 cycles
                            st.write("🔄 " + " → ".join(cyc) + " → " + cyc[0])
                        st.stop()
                    else:
                        # Remove cycles
                        try:
                            from networkx.algorithms.approximation import minimum_feedback_arc_set
                            fas = minimum_feedback_arc_set(G0)
                            G0.remove_edges_from(fas)
                            st.warning(
                                f"⚠️ Automatically removed **{len(fas)}** edge(s) to break cycles")
                        except ImportError:
                            for cyc in nx.simple_cycles(G0):
                                cycle_edges = list(
                                    zip(cyc, cyc[1:] + [cyc[0]]))
                                for u, v in cycle_edges:
                                    if G0.has_edge(u, v):
                                        G0.remove_edge(u, v)
                                        break
                        new_edges = list(G0.edges())

                # Initialize optimizer
                try:
                    st.session_state.optimizer = DAGOptimizer(
                        new_edges, edge_attrs)
                    st.session_state.edges = new_edges
                    st.session_state.edge_attrs = edge_attrs
                    st.session_state.did_optimize = False
                    st.success("✅ DAG built successfully!")
                except Exception as e:
                    st.error(f"❌ Initialization error: {e}")

with tab2:
    st.markdown("### Manual Edge List Input")
    st.markdown(
        "Enter edges in format: `source,target` or `source,target,class` (one per line)")

    txt = st.text_area(
        "Edge list:",
        placeholder="A,B\nB,C\nA,C\nC,D",
        height=200
    )

    if st.button("🔨 Build DAG from Text", type="primary"):
        with st.spinner("Building DAG..."):
            rows = []
            for line in txt.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    rows.append({
                        'source': parts[0],
                        'target': parts[1],
                        'classes': parts[2] if len(parts) > 2 else None
                    })

            if rows:
                df = pd.DataFrame(rows)
                new_edges, edge_attrs = aggregate_edge_classes(
                    df, 'source', 'target', 'classes')

                try:
                    st.session_state.optimizer = DAGOptimizer(
                        new_edges, edge_attrs)
                    st.session_state.edges = new_edges
                    st.session_state.edge_attrs = edge_attrs
                    st.session_state.did_optimize = False
                    st.success("✅ DAG built successfully!")
                except Exception as e:
                    st.error(f"❌ Initialization error: {e}")
            else:
                st.error("❌ No valid edges found in input")

with tab3:
    st.markdown("### Generate Random DAG")

    col1, col2 = st.columns(2)
    with col1:
        n = st.number_input(
            "Number of nodes",
            min_value=2,
            max_value=100,
            value=10)
    with col2:
        p = st.slider(
            "Edge probability",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05)

    if st.button("🎲 Generate Random DAG", type="primary"):
        with st.spinner("Generating random DAG..."):
            access_map = defaultdict(set)
            nodes = [f"Node_{i}" for i in range(n)]

            # Create random DAG (only forward edges to maintain acyclic
            # property)
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < p:
                        access_map[(nodes[i], nodes[j])]  # no classes

            new_edges = list(access_map.keys())
            edge_attrs = {e: [] for e in new_edges}

            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success(
                f"✅ Generated random DAG with **{len(new_edges)}** edges!")

with tab4:
    st.markdown("### Machine Learning Workflow Examples")
    st.markdown("Load pre-built example DAGs for common ML use cases:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🤖 ML Training Pipeline", use_container_width=True):
            new_edges, edge_attrs = get_ml_pipeline_example()
            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success("✅ Loaded ML Training Pipeline example!")

        if st.button("🧠 LangGraph Agent Workflow", use_container_width=True):
            new_edges, edge_attrs = get_langgraph_example()
            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success("✅ Loaded LangGraph Agent example!")

    with col2:
        if st.button("⚡ Distributed Training", use_container_width=True):
            new_edges, edge_attrs = get_distributed_training_example()
            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success("✅ Loaded Distributed Training example!")

        if st.button(
            "🔧 Feature Engineering Pipeline",
                use_container_width=True):
            new_edges, edge_attrs = get_feature_engineering_example()
            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success("✅ Loaded Feature Engineering example!")

# Guard: check if DAG is loaded
if st.session_state.edges is None:
    st.info("👆 Please specify or generate a DAG using the tabs above to get started.")
    st.stop()

opt = st.session_state.optimizer

# --- Neo4j Push Logic ---
if 'push' in locals() and push:
    graph_to_push = opt.original_graph if graph_target == "Original DAG" else opt.graph
    try:
        with st.spinner("Pushing to Neo4j..."):
            driver = GraphDatabase.driver(uri, auth=(usr, pwd))
            
            def create_graph(tx):
                for n in graph_to_push.nodes():
                    tx.run("MERGE (n:Node {name:$name})", name=n)
                for u, v in graph_to_push.edges():
                    classes = st.session_state.edge_attrs.get((u, v), [])
                    tx.run(
                        "MATCH (a:Node {name:$u}) MATCH (b:Node {name:$v})"
                        " MERGE (a)-[r:DEPENDS_ON]->(b) SET r.classes=$classes",
                        u=u, v=v, classes=classes
                    )
            
            with driver.session() as session:
                session.execute_write(create_graph)
            driver.close()
            st.success("✅ Successfully pushed to Neo4j!")
    except Exception as e:
        st.error(f"❌ Neo4j push error: {e}")

# --- Optimization Logic ---
if optimize:
    with st.spinner("Optimizing DAG..."):
        if do_tr:
            opt.transitive_reduction()
        if do_merge:
            opt.merge_equivalent_nodes()
        st.session_state.did_optimize = True
        st.success(
            f"✅ Optimization complete! Method: **{opt.optimization_method}**")
        st.rerun()  # Rerun to show results

# --- Display Results ---
if st.session_state.did_optimize:
    st.markdown("---")
    st.header("📊 Optimization Results")

    # Get metrics
    om = opt.evaluate_graph_metrics(opt.original_graph)
    nm = opt.evaluate_graph_metrics(opt.graph)

    # Key metrics at top
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Nodes",
            nm.get('num_nodes', 'N/A'),
            delta=int(nm.get('num_nodes', 0) - om.get('num_nodes', 0)),
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "Edges",
            nm.get('num_edges', 'N/A'),
            delta=int(nm.get('num_edges', 0) - om.get('num_edges', 0)),
            delta_color="inverse"
        )

    with col3:
        edge_reduction = 0
        if om.get('num_edges', 0) > 0:
            edge_reduction = (
                (om.get('num_edges', 0) - nm.get('num_edges', 0)) / om.get('num_edges', 0)) * 100
        st.metric(
            "Edge Reduction",
            f"{edge_reduction:.1f}%",
            delta=None
        )

    with col4:
        efficiency_change = nm.get(
            'efficiency_score', 0) - om.get('efficiency_score', 0)
        st.metric(
            "Efficiency Score",
            f"{nm.get('efficiency_score', 0):.2%}",
            delta=f"{efficiency_change:+.2%}"
        )

    # Tabs for different result views
    result_tab1, result_tab2, result_tab3, result_tab4 = st.tabs([
        "📈 Metrics Comparison",
        "🎯 PERT/CPM Analysis",
        "📊 Layer Analysis",
        "🔗 Edge Criticality"
    ])

    with result_tab1:
        st.markdown("### Comprehensive Metrics Comparison")

        # Create comparison dataframe
        metrics_data = []
        for key in om.keys():
            if key not in [
                'critical_path_analysis',
                'layer_analysis',
                    'edge_criticality']:
                orig_val = om.get(key, 'N/A')
                opt_val = nm.get(key, 'N/A')

                # Calculate change
                change = "N/A"
                if isinstance(
                        orig_val, (int, float)) and isinstance(
                        opt_val, (int, float)):
                    if orig_val != 0:
                        pct_change = ((opt_val - orig_val) / orig_val) * 100
                        change = f"{pct_change:+.2f}%"
                    else:
                        change = "N/A" if opt_val == 0 else "+∞"

                metrics_data.append({
                    "Metric": key.replace('_', ' ').title(),
                    "Original": format_metric_value(orig_val),
                    "Optimized": format_metric_value(opt_val),
                    "Change": change
                })

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    with result_tab2:
        st.markdown("### PERT/CPM Critical Path Analysis")

        if 'critical_path_analysis' in nm:
            cpa = nm['critical_path_analysis']

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Makespan", f"{cpa.get('makespan', 'N/A')} units")
            with col2:
                st.metric("Critical Path Length",
                          f"{len(cpa.get('critical_path', []))} nodes")
            with col3:
                st.metric(
                    "Parallel Time Saved", f"{
                        cpa.get(
                            'parallel_time_saved', 'N/A')} units")

            st.markdown("#### Critical Path")
            if 'critical_path' in cpa and cpa['critical_path']:
                path_str = " → ".join(cpa['critical_path'])
                st.code(path_str, language=None)

            st.markdown("#### Node Slack Times")
            if 'node_slack' in cpa:
                slack_df = pd.DataFrame([
                    {"Node": node, "Slack Time": slack, "Is Critical": "Yes" if slack == 0 else "No"}
                    for node, slack in sorted(cpa['node_slack'].items(), key=lambda x: x[1])
                ])
                st.dataframe(
                    slack_df,
                    use_container_width=True,
                    hide_index=True)
        else:
            st.info("No PERT/CPM analysis available")

    with result_tab3:
        st.markdown("### Layer-Based Parallelism Analysis")

        if 'layer_analysis' in nm:
            la = nm['layer_analysis']

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Width (Max Parallelism)", f"{
                        la.get(
                            'width', 'N/A')} nodes")
            with col2:
                st.metric("Depth (Stages)", f"{la.get('depth', 'N/A')} layers")
            with col3:
                st.metric(
                    "Width Efficiency", f"{
                        la.get(
                            'width_efficiency', 0):.1%}")
            with col4:
                st.metric(
                    "Avg Layer Size", f"{
                        la.get(
                            'avg_layer_size', 0):.2f}")

            st.markdown("#### Layer Structure")
            if 'layers' in la:
                layer_data = []
                for layer_id, nodes in sorted(
                    la['layers'].items(), key=lambda x: int(
                        x[0])):
                    layer_data.append({
                        "Layer": layer_id,
                        "Node Count": len(nodes),
                        "Nodes": ", ".join(nodes)
                    })
                layer_df = pd.DataFrame(layer_data)
                st.dataframe(
                    layer_df,
                    use_container_width=True,
                    hide_index=True)
        else:
            st.info("No layer analysis available")

    with result_tab4:
        st.markdown("### Edge Criticality Analysis")

        if 'edge_criticality' in nm:
            ec = nm['edge_criticality']

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Critical Edges", ec.get(
                        'critical_edges_count', 'N/A'))
            with col2:
                st.metric(
                    "Redundant Edges", ec.get(
                        'redundant_edges_count', 'N/A'))
            with col3:
                st.metric(
                    "Criticality Ratio", f"{
                        ec.get(
                            'criticality_ratio', 0):.1%}")

            col_crit, col_red = st.columns(2)

            with col_crit:
                st.markdown("#### Critical Edges (Cannot be removed)")
                if 'critical_edges' in ec and ec['critical_edges']:
                    critical_edges_list = []
                    for edge in ec['critical_edges'][:20]:  # Show first 20
                        if isinstance(edge, list) and len(edge) == 2:
                            critical_edges_list.append(
                                f"{edge[0]} → {edge[1]}")
                    st.code("\n".join(critical_edges_list), language=None)
                else:
                    st.info("No critical edges")

            with col_red:
                st.markdown("#### Redundant Edges (Can be removed)")
                if 'redundant_edges' in ec and ec['redundant_edges']:
                    redundant_edges_list = []
                    for edge in ec['redundant_edges'][:20]:  # Show first 20
                        if isinstance(edge, list) and len(edge) == 2:
                            redundant_edges_list.append(
                                f"{edge[0]} → {edge[1]}")
                    st.code("\n".join(redundant_edges_list), language=None)
                else:
                    st.info("No redundant edges")
        else:
            st.info("No edge criticality analysis available")

    # Visualization Section
    st.markdown("---")
    st.header("🎨 Graph Visualization")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    for idx, (G, ax, title, color) in enumerate([
        (opt.original_graph, axes[0], "Original DAG", 'lightblue'),
        (opt.graph, axes[1], "Optimized DAG", 'lightgreen')
    ]):
        # Try hierarchical layout first, fallback to spring
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except BaseException:
            try:
                pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
            except BaseException:
                pos = nx.random_layout(G, seed=42)

        # Edge colors based on classes
        edge_colors = []
        for u, v in G.edges():
            cls = st.session_state.edge_attrs.get((u, v), [])
            if 'Modify' in cls:
                edge_colors.append('magenta')
            elif 'Call_by' in cls:
                edge_colors.append('gray')
            else:
                edge_colors.append('lightblue' if idx == 0 else 'lightgreen')

        # Draw graph
        nx.draw(
            G, pos, ax=ax,
            with_labels=True,
            node_color=color,
            edge_color=edge_colors,
            node_size=800,
            font_size=8,
            font_weight='bold',
            arrows=True,
            arrowsize=15,
            arrowstyle='->',
            width=2,
            alpha=0.9
        )

        ax.set_title(
            f"{title}\n({
                G.number_of_nodes()} nodes, {
                G.number_of_edges()} edges)",
            fontsize=14,
            fontweight='bold',
            pad=20)
        ax.axis('off')

    plt.tight_layout()
    st.pyplot(fig)

    # Download visualization
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)

    st.download_button(
        "📷 Download Visualization (PNG)",
        data=buf,
        file_name=f"dag_visualization_{
            datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png",
        use_container_width=True)

else:
    # Show original graph info before optimization
    st.markdown("---")
    st.header("📊 Original DAG Information")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Nodes", opt.original_graph.number_of_nodes())
    with col2:
        st.metric("Edges", opt.original_graph.number_of_edges())
    with col3:
        density = nx.density(opt.original_graph)
        st.metric("Density", f"{density:.3f}")
    with col4:
        comps = nx.number_weakly_connected_components(opt.original_graph)
        st.metric("Components", comps)

    st.info(
        "👈 Click **'🚀 Optimize DAG'** in the sidebar to run optimization algorithms!")

    # Show original graph visualization
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    G = opt.original_graph
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except BaseException:
        try:
            pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
        except BaseException:
            pos = nx.random_layout(G, seed=42)

    nx.draw(
        G, pos, ax=ax,
        with_labels=True,
        node_color='lightblue',
        node_size=800,
        font_size=8,
        font_weight='bold',
        arrows=True,
        arrowsize=15,
        arrowstyle='->',
        width=2,
        alpha=0.9
    )

    ax.set_title(
        f"Original DAG\n({
            G.number_of_nodes()} nodes, {
            G.number_of_edges()} edges)",
        fontsize=14,
        fontweight='bold',
        pad=20)
    ax.axis('off')

    plt.tight_layout()
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🗺️ <strong>DAG Optimizer</strong> | An advanced Python library for ML workflow optimization</p>
    <p>📚 <a href="https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs" target="_blank">GitHub Repository</a> |
    📖 <a href="https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/wiki" target="_blank">Documentation</a></p>
</div>
""", unsafe_allow_html=True)
