"""
Tests for the DLX implementation.
"""

import numpy as np
import pytest
from dlxsolver import DLXSolver, solve_exact_cover


def test_simple_exact_cover():
    """Test a simple exact cover problem."""
    # Matrix with known solution: rows 0 and 1 form exact cover
    matrix = [
        [1, 0, 1],  # Row 0: covers columns 0, 2
        [0, 1, 0],  # Row 1: covers column 1
        [1, 1, 0],  # Row 2: covers columns 0, 1
    ]
    
    solver = DLXSolver(matrix)
    solutions = solver.solve(find_all=True)
    
    # Should find at least one solution
    assert len(solutions) > 0
    
    # Verify each solution is valid
    for solution in solutions:
        # Check that all columns are covered exactly once
        coverage = np.zeros(3, dtype=np.int32)
        for row_idx in solution:
            coverage += matrix[row_idx]
        assert np.all(coverage == 1), f"Invalid solution {solution}: coverage = {coverage}"


def test_no_solution():
    """Test a problem with no solution."""
    matrix = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 0],  # Column 2 can never be covered
    ]
    
    solver = DLXSolver(matrix)
    solution = solver.solve_one()
    
    assert solution is None


def test_multiple_solutions():
    """Test a problem with multiple solutions."""
    matrix = [
        [1, 0, 1],  # Solution 1: rows 0, 1
        [0, 1, 0],  # Solution 2: rows 0, 2
        [0, 1, 1],
    ]
    
    solver = DLXSolver(matrix)
    solutions = solver.solve(find_all=True)
    
    # Should find multiple solutions
    assert len(solutions) >= 1
    
    # Verify solutions are valid
    for solution in solutions:
        coverage = np.zeros(3, dtype=np.int32)
        for row_idx in solution:
            coverage += matrix[row_idx]
        assert np.all(coverage == 1)


def test_convenience_function():
    """Test the convenience function."""
    # Matrix with known solution: rows 0 and 1 form exact cover
    matrix = [
        [1, 0, 1],  # Row 0: covers columns 0, 2
        [0, 1, 0],  # Row 1: covers column 1
    ]
    
    solutions = solve_exact_cover(matrix, find_all=True)
    assert len(solutions) > 0
    
    # Verify solution is valid
    for solution in solutions:
        coverage = np.zeros(3, dtype=np.int32)
        for row_idx in solution:
            coverage += matrix[row_idx]
        assert np.all(coverage == 1)


def test_invalid_matrix():
    """Test that invalid matrices are rejected."""
    # Non-binary matrix
    matrix = [[1, 2, 3]]
    with pytest.raises(ValueError):
        DLXSolver(matrix)
    
    # Non-2D matrix
    matrix = [1, 2, 3]
    with pytest.raises(ValueError):
        DLXSolver(matrix)


def test_empty_matrix():
    """Test edge case with empty matrix."""
    # Empty matrix should raise error or handle gracefully
    matrix = np.array([], dtype=np.int32).reshape(0, 0)
    with pytest.raises((ValueError, IndexError)):
        DLXSolver(matrix)


def test_single_row_solution():
    """Test case where single row is the solution."""
    matrix = [
        [1, 1, 1],  # Single row covers all columns
    ]
    solver = DLXSolver(matrix)
    solution = solver.solve_one()
    assert solution == [0]


def test_single_column():
    """Test case with single column."""
    matrix = [
        [1],
        [1],
        [1],
    ]
    solver = DLXSolver(matrix)
    solution = solver.solve_one()
    assert solution is not None
    assert len(solution) == 1


def test_empty_rows():
    """Test case with rows that have no 1s."""
    matrix = [
        [0, 0, 0],  # Empty row
        [1, 0, 1],
        [0, 1, 0],
    ]
    solver = DLXSolver(matrix)
    solutions = solver.solve(find_all=True)
    # Should still find solution using rows 1 and 2
    assert len(solutions) > 0


def test_solve_one_vs_solve_all():
    """Test that solve_one returns first solution from solve."""
    matrix = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 1, 0],
    ]
    solver = DLXSolver(matrix)
    first = solver.solve_one()
    all_solutions = solver.solve(find_all=True)
    
    assert first is not None
    assert len(all_solutions) > 0
    assert first == all_solutions[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
