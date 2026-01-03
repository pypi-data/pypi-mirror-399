"""
DAG Optimizer - Advanced Directed Acyclic Graph Optimization Library
Author: Sahil Shrivastava (sahilshrivastava28@gmail.com)
License: MIT
"""

from setuptools import setup, find_packages
import os

# Read the long description from README
def read_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dagoptimizer",
    version="1.0.0",
    author="Sahil Shrivastava",
    author_email="sahilshrivastava28@gmail.com",
    description="Advanced DAG optimization library with adaptive transitive reduction, PERT/CPM analysis, and 25+ research-grade metrics",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs",
    project_urls={
        "Bug Tracker": "https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/issues",
        "Documentation": "https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/wiki",
        "Source Code": "https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs",
        "Demo Application": "https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs#demo-application",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "neo4j": [
            "neo4j>=5.0.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "pygraphviz>=1.10",
        ],
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
        ],
    },
    keywords=[
        "dag",
        "graph",
        "optimization",
        "transitive-reduction",
        "pert",
        "cpm",
        "critical-path",
        "networkx",
        "directed-acyclic-graph",
        "graph-algorithms",
        "workflow-optimization",
        "build-systems",
        "dependency-analysis",
        "task-scheduling",
    ],
    entry_points={
        "console_scripts": [
            "dagoptimizer=dagoptimizer.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

