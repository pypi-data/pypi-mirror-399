"""
Python wrapper for the DLX Cython implementation.

This provides a more Pythonic interface to the DLX solver.
"""

import numpy as np
from dlx import DLX as CythonDLX


class DLXSolver:
    """
    High-level Python interface for the DLX solver.
    
    Example:
    --------
    >>> matrix = [
    ...     [1, 0, 0, 1, 0, 0, 1],
    ...     [1, 0, 0, 1, 0, 0, 0],
    ...     [0, 0, 0, 1, 1, 0, 1],
    ...     [0, 0, 1, 0, 1, 1, 0],
    ...     [0, 1, 1, 0, 0, 1, 1],
    ...     [0, 1, 0, 0, 0, 0, 1],
    ... ]
    >>> solver = DLXSolver(matrix)
    >>> solutions = solver.solve()
    """
    
    def __init__(self, matrix):
        """
        Initialize the DLX solver with a constraint matrix.
        
        Parameters:
        -----------
        matrix : array-like, shape (n_rows, n_cols)
            Binary matrix where matrix[i][j] = 1 means row i covers column j.
            Can be a list of lists, numpy array, etc.
        """
        matrix = np.asarray(matrix, dtype=np.int32)
        if matrix.ndim != 2:
            raise ValueError("Matrix must be 2-dimensional")
        
        self.matrix = matrix
        self.n_rows, self.n_cols = matrix.shape
        
        # Validate matrix is not empty
        if self.n_rows == 0 or self.n_cols == 0:
            raise ValueError("Matrix must have at least one row and one column")
        
        # Validate binary matrix
        if not np.all((matrix == 0) | (matrix == 1)):
            raise ValueError("Matrix must contain only 0s and 1s")
        
        self._solver = CythonDLX(self.n_rows, self.n_cols, matrix)
    
    def solve(self, find_all=True):
        """
        Solve the exact cover problem.
        
        Parameters:
        -----------
        find_all : bool, optional
            If True (default), find all solutions.
            If False, return only the first solution.
        
        Returns:
        --------
        list of lists
            List of solutions. Each solution is a list of row indices
            that form an exact cover.
        """
        return self._solver.solve(find_all=find_all)
    
    def solve_one(self):
        """
        Find the first solution.
        
        Returns:
        --------
        list or None
            First solution as a list of row indices, or None if no solution exists.
        """
        return self._solver.solve_one()
    
    def get_solution_rows(self, solution):
        """
        Get the actual rows for a solution.
        
        Parameters:
        -----------
        solution : list
            List of row indices (as returned by solve())
        
        Returns:
        --------
        numpy.ndarray
            The rows of the matrix corresponding to the solution.
        """
        return self.matrix[solution, :]


def solve_exact_cover(matrix, find_all=True):
    """
    Convenience function to solve an exact cover problem.
    
    Parameters:
    -----------
    matrix : array-like
        Binary constraint matrix
    find_all : bool, optional
        Whether to find all solutions (default: True)
    
    Returns:
    --------
    list of lists
        Solutions to the exact cover problem.
    
    Example:
    --------
    >>> matrix = [[1, 0, 1], [0, 1, 1], [1, 1, 0]]
    >>> solutions = solve_exact_cover(matrix)
    """
    solver = DLXSolver(matrix)
    return solver.solve(find_all=find_all)
