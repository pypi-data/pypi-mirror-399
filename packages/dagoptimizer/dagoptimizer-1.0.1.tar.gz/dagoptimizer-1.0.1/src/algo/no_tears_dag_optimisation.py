import numpy as np
import networkx as nx
from scipy.optimize import minimize
from scipy.linalg import expm
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime


class DataDrivenDAGOptimizer:
    def __init__(self, X, lambda1=0.01):
        self.X = X  # shape: (n_samples, n_features)
        self.d = X.shape[1]
        self.lambda1 = lambda1
        self.W_est = None

    def _h(self, W_flat):
        """Acyclicity constraint: h(W) = tr(e^{W◦W}) - d"""
        W = W_flat.reshape(self.d, self.d)
        return np.trace(expm(W * W)) - self.d

    def _loss(self, W_flat):
        """Least squares loss + L1 regularization"""
        W = W_flat.reshape(self.d, self.d)
        XW = self.X @ W
        mse = 0.5 * np.linalg.norm(self.X - XW, ord="fro") ** 2 / self.X.shape[0]
        l1 = self.lambda1 * np.sum(np.abs(W))
        return mse + l1

    def fit(self):
        """Run the optimization"""
        W_init = np.zeros((self.d, self.d))
        constraints = {"type": "eq", "fun": self._h}
        result = minimize(self._loss, W_init.flatten(), method="L-BFGS-B", constraints=[constraints])
        self.W_est = result.x.reshape(self.d, self.d)
        return self.W_est

    def to_graph(self, threshold=0.3):
        """Convert weight matrix to graph (adjacency matrix)"""
        W = self.W_est.copy()
        W[np.abs(W) < threshold] = 0
        G = nx.DiGraph()
        for i in range(self.d):
            for j in range(self.d):
                if W[i, j] != 0:
                    G.add_edge(f"N{i}", f"Nj")
        return G

    def optimize_graph(self, G):
        """Apply transitive reduction + optional merge"""
        G = nx.transitive_reduction(G)
        return G

    def save_results(self, G_original, G_optimized, base_path="graph_metadata"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = os.path.join(base_path, f"dag_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        def metrics(G):
            return {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "density": nx.density(G),
                "longest_path": nx.dag_longest_path_length(G),
                "leaf_nodes": len([n for n in G.nodes if G.out_degree(n) == 0])
            }

        data = {
            "original_edges": list(G_original.edges()),
            "optimized_edges": list(G_optimized.edges()),
            "original_metrics": metrics(G_original),
            "optimized_metrics": metrics(G_optimized)
        }

        with open(os.path.join(folder, "metadata.json"), "w") as f:
            json.dump(data, f, indent=4)

        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        pos1 = nx.spring_layout(G_original, seed=42)
        pos2 = nx.spring_layout(G_optimized, seed=42)
        nx.draw(G_original, pos1, ax=axes[0], with_labels=True, node_color="lightblue")
        axes[0].set_title("Original Learned DAG")
        nx.draw(G_optimized, pos2, ax=axes[1], with_labels=True, node_color="lightgreen")
        axes[1].set_title("Optimized DAG")
        plt.tight_layout()
        plt.savefig(os.path.join(folder, "visualization.png"))
        plt.close()

        print(f"✅ DAG metadata saved to {folder}")


# === Example Usage ===
if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic data: X = XW + noise, true DAG is 5 variables
    d = 5
    W_true = np.array([
        [0, 0.8, 0, 0, 0],
        [0, 0, 0.5, 0, 0],
        [0, 0, 0, 1.0, 0],
        [0, 0, 0, 0, 1.2],
        [0, 0, 0, 0, 0]
    ])
    n = 1000
    X = np.random.randn(n, d)
    noise = 0.1 * np.random.randn(n, d)
    X = X @ np.linalg.inv(np.eye(d) - W_true) + noise

    optimizer = DataDrivenDAGOptimizer(X)
    W_learned = optimizer.fit()

    G_learned = optimizer.to_graph()
    G_optimized = optimizer.optimize_graph(G_learned)

    optimizer.save_results(G_learned, G_optimized)
