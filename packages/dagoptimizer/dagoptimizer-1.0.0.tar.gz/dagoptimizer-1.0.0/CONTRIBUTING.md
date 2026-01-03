# Contributing to Advanced DAG Optimization Framework

First off, thank you for considering contributing to this project! 🎉

The following is a set of guidelines for contributing to the Advanced DAG Optimization Framework. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## 🤝 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check the [issue tracker](../../issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (sample DAGs, screenshots, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, Node version)

**Bug Report Template**:
```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Load DAG with X nodes
2. Apply transitive reduction
3. Observe error...

## Expected Behavior
What should have happened.

## Actual Behavior
What actually happened.

## Environment
- OS: Windows 11 / Ubuntu 22.04 / macOS 13
- Python: 3.10.5
- Node: 18.16.0
- Browser: Chrome 120

## Additional Context
Screenshots, error logs, etc.
```

### Suggesting Enhancements ✨

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

**Feature Request Template**:
```markdown
## Feature Description
A clear description of the feature.

## Motivation
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've thought about.

## Additional Context
Mockups, examples, related research papers.
```

### Contributing Code 💻

We love pull requests! Here are areas where contributions are especially welcome:

1. **Algorithm Improvements**
   - More efficient transitive reduction algorithms
   - Additional graph optimization techniques
   - Performance optimizations

2. **New Features**
   - Additional graph metrics
   - New visualization modes
   - Export formats (GraphML, DOT, etc.)

3. **Documentation**
   - Tutorials and guides
   - API documentation
   - Code comments and docstrings

4. **Testing**
   - Unit tests for core algorithms
   - Integration tests for API endpoints
   - Frontend component tests

5. **UI/UX Improvements**
   - Accessibility enhancements
   - Mobile responsiveness
   - New themes or customization options

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/YourUsername/dag-optimization-framework.git
cd dag-optimization-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start development server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run linter
npm run lint

# Run tests
npm run test

# Start development server
npm run dev
```

---

## 📏 Coding Standards

### Python (Backend)

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Docstrings**: Google style

**Example**:
```python
def compute_transitive_reduction(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Computes the transitive reduction of a directed acyclic graph.

    Args:
        graph: Input DAG as a NetworkX DiGraph

    Returns:
        A new DiGraph representing the transitive reduction

    Raises:
        ValueError: If the input graph contains cycles
    """
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Input graph must be a DAG")
    
    # Implementation...
    return reduced_graph
```

**Tools**:
- **Linter**: `flake8` (configured in `.flake8`)
- **Formatter**: `black` (line length 100)
- **Type Checker**: `mypy` (optional but encouraged)

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type check
mypy backend/
```

### TypeScript (Frontend)

We follow **Airbnb TypeScript Style Guide** with ESLint:

- **Indentation**: 2 spaces
- **Semicolons**: Required
- **Quotes**: Single quotes for strings
- **Components**: Functional components with hooks

**Example**:
```typescript
interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

export const GraphVisualization: React.FC<{ data: GraphData }> = ({ data }) => {
  const [isInteractive, setIsInteractive] = useState(true);

  useEffect(() => {
    // Implementation...
  }, [data]);

  return (
    <div className="graph-container">
      {/* JSX... */}
    </div>
  );
};
```

**Tools**:
- **Linter**: `eslint` (configured in `.eslintrc.json`)
- **Formatter**: `prettier` (integrated with ESLint)
- **Type Checker**: TypeScript compiler

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

---

## 📝 Commit Guidelines

We follow **Conventional Commits** specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build config, etc.)

### Examples

```bash
# Good commits
git commit -m "feat(backend): add edge criticality classification algorithm"
git commit -m "fix(frontend): tooltip z-index issue on ResearchInsights"
git commit -m "docs: update benchmark results in README"
git commit -m "perf(optimizer): improve transitive reduction for dense graphs"

# Bad commits
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

### Scope

Common scopes:
- **backend**: Python backend changes
- **frontend**: React frontend changes
- **optimizer**: Core DAG optimization algorithms
- **docs**: Documentation
- **tests**: Test files
- **ci**: CI/CD configuration

---

## 🔄 Pull Request Process

### 1. Fork & Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YourUsername/dag-optimization-framework.git
cd dag-optimization-framework

# Create a feature branch
git checkout -b feature/my-amazing-feature
```

### 2. Make Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow coding standards

### 3. Test Thoroughly

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
npm run lint

# Manual testing
# Start both servers and test in browser
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(optimizer): add new metric for graph efficiency"
```

### 5. Push & Create PR

```bash
git push origin feature/my-amazing-feature
```

Then go to GitHub and create a Pull Request.

### PR Template

Your PR description should include:

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change necessary?

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
How was this tested?
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Before/after screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings introduced
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linters
2. **Code Review**: Maintainer(s) review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged
5. **Celebration**: 🎉 Your contribution is now part of the project!

---

## 🧪 Testing Guidelines

### Backend Tests

**Location**: `backend/tests/`

**Types**:
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test API endpoints
- **Property Tests**: Test algorithm correctness on random inputs

**Example**:
```python
import pytest
from src.dag_optimiser.dag_class import DAGOptimizer

def test_transitive_reduction_simple():
    """Test transitive reduction on a simple DAG."""
    edges = [(1, 2), (2, 3), (1, 3)]  # 1->3 is redundant
    optimizer = DAGOptimizer()
    optimizer.load_from_edge_list(edges)
    optimizer.transitive_reduction()
    
    assert (1, 3) not in optimizer.graph.edges()
    assert (1, 2) in optimizer.graph.edges()
    assert (2, 3) in optimizer.graph.edges()

def test_cycle_detection():
    """Test that cycle detection works correctly."""
    edges = [(1, 2), (2, 3), (3, 1)]  # Contains cycle
    optimizer = DAGOptimizer()
    
    with pytest.raises(ValueError, match="Graph contains cycles"):
        optimizer.load_from_edge_list(edges)
```

**Running Tests**:
```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_optimizer.py -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

### Frontend Tests

**Location**: `frontend/src/__tests__/`

**Types**:
- **Component Tests**: React Testing Library
- **Hook Tests**: Custom hook testing
- **Integration Tests**: User flow testing

**Example**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { OptimizationPanel } from '../components/OptimizationPanel';

test('optimization panel toggles transitive reduction', () => {
  const mockOnChange = jest.fn();
  
  render(<OptimizationPanel onChange={mockOnChange} />);
  
  const checkbox = screen.getByLabelText(/transitive reduction/i);
  fireEvent.click(checkbox);
  
  expect(mockOnChange).toHaveBeenCalledWith({ transitiveReduction: true });
});
```

**Running Tests**:
```bash
# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

---

## 📦 Project Structure

Understanding the project structure will help you contribute:

```
dag-optimization-framework/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Python dependencies
│   ├── image_dag_extractor.py    # AI image processing
│   ├── research_report_generator.py  # DOCX report generation
│   └── tests/                     # Backend tests
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Main React component
│   │   ├── components/           # React components
│   │   ├── types.ts              # TypeScript types
│   │   └── __tests__/            # Frontend tests
│   ├── package.json              # Node dependencies
│   └── vite.config.ts            # Vite configuration
├── src/
│   ├── dag_optimiser/
│   │   └── dag_class.py          # Core optimization algorithms
│   └── algo/                      # Additional algorithms
├── docs/                          # Documentation
├── Research Papers/               # Academic references
├── DAG_Dataset/                   # Benchmark dataset
├── Benchmark_Results/             # Test results
├── README.md                      # Main documentation
├── CONTRIBUTING.md               # This file
└── LICENSE                        # MIT License
```

---

## 🎓 Research Contributions

If you're contributing algorithm improvements or new optimization techniques:

1. **Provide mathematical justification** for your approach
2. **Include complexity analysis** (time and space)
3. **Reference relevant papers** in the `Research Papers/` folder
4. **Add benchmark results** to demonstrate effectiveness
5. **Update the research paper** in the GitHub Wiki

---

## 🌟 Recognition

Contributors will be:
- Listed in the project's `CONTRIBUTORS.md` file
- Mentioned in release notes for significant contributions
- Acknowledged in the research paper (for algorithmic contributions)

---

## ❓ Questions?

- **GitHub Discussions**: Ask questions in [Discussions](../../discussions)
- **Email**: Contact maintainer at sahilshrivastava28@gmail.com
- **Issues**: Open an issue with the `question` label

---

Thank you for contributing to the Advanced DAG Optimization Framework! 🚀

Your efforts help make graph optimization accessible to everyone. 🙏

