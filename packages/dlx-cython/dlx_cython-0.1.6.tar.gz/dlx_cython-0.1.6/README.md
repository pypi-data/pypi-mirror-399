# DLX Implementation

A DLX (Dancing Links) algorithm implementation in Cython for solving exact cover problems.

## Features

- **Fast**: Implemented in Cython for speed (sub-millisecond for typical problems)
- **Memory Efficient**: Optimized data structures for minimal memory overhead
- **Python Interface**: Easy-to-use Python API
- **Exact Cover Solver**: Solves exact cover problems efficiently

## Installation

### From PyPI (when published)

```bash
pip install dlx-cython
```

### Local Development

```bash
# Install in editable mode
pip install -e /path/to/dlx
```

### From Source

```bash
git clone https://github.com/robmbrooks/dlx.git
cd dlx
pip install -e .
```

See [INSTALLATION.md](INSTALLATION.md) for detailed installation options and troubleshooting.

## Quick Start

```python
from dlxsolver import DLXSolver

# Define your constraint matrix
matrix = [
    [1, 0, 1],  # Row 0 covers columns 0 and 2
    [0, 1, 0],  # Row 1 covers column 1
    [1, 1, 0],  # Row 2 covers columns 0 and 1
]

# Create solver and find solution
solver = DLXSolver(matrix)
solution = solver.solve_one()
print(f"Solution: {solution}")  # [0, 1]
```

## Usage Examples

### Basic Usage

```python
from dlxsolver import DLXSolver

matrix = [[1, 0, 1], [0, 1, 0], [1, 1, 0]]
solver = DLXSolver(matrix)

# Find first solution
solution = solver.solve_one()

# Find all solutions
all_solutions = solver.solve(find_all=True)
```

### Using Convenience Function

```python
from dlxsolver import solve_exact_cover

solutions = solve_exact_cover(matrix, find_all=True)
```

### With NumPy

```python
import numpy as np
from dlxsolver import DLXSolver

matrix = np.array([[1, 0, 1], [0, 1, 0]], dtype=np.int32)
solver = DLXSolver(matrix)
solution = solver.solve_one()
```

### Edge Cases

```python
from dlxsolver import DLXSolver
import numpy as np

# Single row solution
matrix = [[1, 1, 1]]  # One row covers all columns
solver = DLXSolver(matrix)
solution = solver.solve_one()  # [0]

# Handling no solution
matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]  # Column 2 can't be covered
solver = DLXSolver(matrix)
solution = solver.solve_one()  # None
if solution is None:
    print("No solution exists")

# Getting solution rows
matrix = [[1, 0, 1], [0, 1, 0]]
solver = DLXSolver(matrix)
solution = solver.solve_one()  # [0, 1]
if solution:
    solution_rows = solver.get_solution_rows(solution)
    print(f"Solution rows:\n{solution_rows}")
    # Output:
    # [[1 0 1]
    #  [0 1 0]]
```

### Error Handling

```python
from dlxsolver import DLXSolver

# Invalid matrix (non-binary)
try:
    matrix = [[1, 2, 3]]  # Contains values other than 0/1
    solver = DLXSolver(matrix)
except ValueError as e:
    print(f"Error: {e}")  # "Matrix must contain only 0s and 1s"

# Empty matrix
try:
    matrix = []
    solver = DLXSolver(matrix)
except ValueError as e:
    print(f"Error: {e}")  # "Matrix must have at least one row and one column"

# Non-2D matrix
try:
    matrix = [1, 2, 3]  # 1D array
    solver = DLXSolver(matrix)
except ValueError as e:
    print(f"Error: {e}")  # "Matrix must be 2-dimensional"
```

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation instructions and troubleshooting
- **[PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md)** - Performance benchmarks and analysis
- **[RELEASE.md](RELEASE.md)** - Release process for maintainers

## Examples

See the `examples/` directory for usage examples:
- `examples/simple_example.py` - Basic usage examples
- `examples/sudoku_example.py` - Sudoku solver using DLX
- `example_usage.py` - Comprehensive usage examples

## Building from Source

```bash
# Install dependencies
pip install numpy cython setuptools

# Build Cython extension
python setup.py build_ext --inplace

# Install package
pip install -e .
```

## Requirements

- Python 3.7+
- NumPy >= 1.19.0
- Cython >= 0.29.0 (for building)

## API Reference

### `DLXSolver` Class

Main solver class for exact cover problems.

#### `DLXSolver(matrix)`

Initialize the solver with a constraint matrix.

**Parameters:**
- `matrix` (array-like): Binary matrix of shape `(n_rows, n_cols)` where `matrix[i][j] = 1` means row `i` covers column `j`. Can be a list of lists or NumPy array.

**Raises:**
- `ValueError`: If matrix is not 2-dimensional, empty, or contains non-binary values.

**Example:**
```python
matrix = [[1, 0, 1], [0, 1, 0]]
solver = DLXSolver(matrix)
```

#### `solve(find_all=True)`

Solve the exact cover problem.

**Parameters:**
- `find_all` (bool, optional): If `True` (default), find all solutions. If `False`, return only the first solution.

**Returns:**
- `list of lists`: List of solutions, where each solution is a list of row indices forming an exact cover. Returns empty list if no solution exists.

**Example:**
```python
solutions = solver.solve(find_all=True)
# [[0, 1], [2, 3]]  # Multiple solutions
```

#### `solve_one()`

Find the first solution.

**Returns:**
- `list or None`: First solution as a list of row indices, or `None` if no solution exists.

**Example:**
```python
solution = solver.solve_one()
# [0, 1] or None
```

#### `get_solution_rows(solution)`

Get the actual matrix rows for a solution.

**Parameters:**
- `solution` (list): List of row indices (as returned by `solve()` or `solve_one()`).

**Returns:**
- `numpy.ndarray`: The rows of the matrix corresponding to the solution.

**Example:**
```python
solution = [0, 1]
rows = solver.get_solution_rows(solution)
# Returns the actual matrix rows as a NumPy array
```

### `solve_exact_cover()` Function

Convenience function to solve an exact cover problem without creating a solver instance.

**Parameters:**
- `matrix` (array-like): Binary constraint matrix.
- `find_all` (bool, optional): Whether to find all solutions (default: `True`).

**Returns:**
- `list of lists`: Solutions to the exact cover problem.

**Example:**
```python
from dlxsolver import solve_exact_cover

matrix = [[1, 0, 1], [0, 1, 0]]
solutions = solve_exact_cover(matrix, find_all=True)
```

## Performance

### Characteristics

The DLX algorithm has the following performance characteristics:

- **Time Complexity**: 
  - Best case: O(n) where n is the number of rows
  - Average case: O(n × m) where m is average branching factor
  - Worst case: Exponential (inherent to exact cover problems)
  
- **Space Complexity**: O(n × m) where n is rows and m is columns

- **Typical Performance**:
  - **Small problems (100x50)**: ~0.08ms
  - **Medium problems (500x200)**: ~10ms  
  - **Large problems (1000x500)**: ~100ms

### Factors Affecting Performance

1. **Matrix Density**: Sparse matrices (low density) solve faster
2. **Solution Count**: Finding all solutions takes longer than finding one
3. **Problem Structure**: Problems with many overlapping constraints may be slower
4. **Early Termination**: Using `find_all=False` stops after first solution

### Optimization Tips

- Use `solve_one()` instead of `solve(find_all=True)` if you only need one solution
- For very large problems, consider breaking into smaller sub-problems
- Sparse matrices (many zeros) perform better than dense matrices

See [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for detailed benchmarks and analysis.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{dlx_cython,
  title = {DLX-Cython: Dancing Links Implementation},
  author = {Robert Brooks},
  year = {2024},
  url = {https://github.com/robmbrooks/dlx},
  version = {0.1.0}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

#### "No module named 'dlx'"

**Problem:** The Cython extension hasn't been built.

**Solution:**
```bash
cd /path/to/dlx
python setup.py build_ext --inplace
pip install -e .
```

#### "Matrix must contain only 0s and 1s"

**Problem:** Your matrix contains values other than 0 or 1.

**Solution:** Ensure your matrix is binary:
```python
import numpy as np
matrix = np.array(your_matrix, dtype=np.int32)
# Verify it's binary
assert np.all((matrix == 0) | (matrix == 1))
```

#### "Matrix must be 2-dimensional"

**Problem:** You passed a 1D array instead of a 2D matrix.

**Solution:** Reshape your data:
```python
# Wrong
matrix = [1, 0, 1, 0, 1, 0]

# Correct
matrix = [[1, 0, 1], [0, 1, 0]]
# or
matrix = np.array([1, 0, 1, 0, 1, 0]).reshape(2, 3)
```

#### Solver returns empty list / None

**Problem:** No exact cover solution exists for your matrix.

**Solution:** Verify your problem has a solution:
```python
# Check if all columns can be covered
coverage = np.sum(matrix, axis=0)
if np.any(coverage == 0):
    print("Some columns cannot be covered")
```

#### Slow performance on large problems

**Problem:** Very large or dense matrices may take longer.

**Solutions:**
- Use `solve_one()` instead of `solve(find_all=True)` if possible
- Consider if the problem can be decomposed into smaller sub-problems
- Check matrix density - sparse matrices perform better

### Getting Help

- Check the [examples/](examples/) directory for usage patterns
- Review [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for performance tips
- Open an issue on [GitHub](https://github.com/robmbrooks/dlx/issues)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
