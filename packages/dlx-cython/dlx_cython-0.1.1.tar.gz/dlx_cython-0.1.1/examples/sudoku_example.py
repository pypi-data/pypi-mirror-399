"""
Example: Using DLX to solve Sudoku puzzles.

This demonstrates how to use DLX to solve Sudoku by converting
it to an exact cover problem.
"""

import numpy as np
from dlxsolver import DLXSolver


def sudoku_to_exact_cover(puzzle):
    """
    Convert a Sudoku puzzle to an exact cover problem.
    
    In Sudoku, we have 4 constraints:
    1. Each cell must contain exactly one number (81 constraints)
    2. Each row must contain each number exactly once (81 constraints)
    3. Each column must contain each number exactly once (81 constraints)
    4. Each box must contain each number exactly once (81 constraints)
    
    Total: 324 constraints
    
    We have 729 possibilities (9x9 grid x 9 numbers)
    """
    n = 9
    n_sq = n * n
    
    # Initialize constraint matrix
    # Rows: 729 possibilities (row, col, number)
    # Cols: 324 constraints
    matrix = []
    
    for row in range(n):
        for col in range(n):
            for num in range(1, n + 1):
                # Skip if this cell is already filled with a different number
                if puzzle[row, col] != 0 and puzzle[row, col] != num:
                    continue
                
                constraint_row = [0] * (4 * n_sq)
                
                # Constraint 1: Cell (row, col) must have exactly one number
                cell_constraint = row * n + col
                constraint_row[cell_constraint] = 1
                
                # Constraint 2: Row must contain number exactly once
                row_constraint = n_sq + row * n + (num - 1)
                constraint_row[row_constraint] = 1
                
                # Constraint 3: Column must contain number exactly once
                col_constraint = 2 * n_sq + col * n + (num - 1)
                constraint_row[col_constraint] = 1
                
                # Constraint 4: Box must contain number exactly once
                box = (row // 3) * 3 + (col // 3)
                box_constraint = 3 * n_sq + box * n + (num - 1)
                constraint_row[box_constraint] = 1
                
                matrix.append(constraint_row)
    
    return np.array(matrix, dtype=np.int32)


def exact_cover_to_sudoku(solution, puzzle):
    """Convert a solution back to a Sudoku grid."""
    n = 9
    result = puzzle.copy()
    
    for row_idx in solution:
        # Calculate which possibility this represents
        # Each row in the matrix represents (row, col, num)
        n_sq = n * n
        possibility = row_idx
        
        # Extract row, col, num from the possibility index
        # This requires tracking how we built the matrix
        # For simplicity, we'll reconstruct it
        idx = 0
        for r in range(n):
            for c in range(n):
                for num in range(1, n + 1):
                    if puzzle[r, c] != 0 and puzzle[r, c] != num:
                        continue
                    if idx == row_idx:
                        result[r, c] = num
                        break
                    idx += 1
                else:
                    continue
                break
            else:
                continue
            break
    
    return result


def solve_sudoku(puzzle):
    """
    Solve a Sudoku puzzle using DLX.
    
    Parameters:
    -----------
    puzzle : numpy.ndarray, shape (9, 9)
        Initial Sudoku puzzle. Use 0 for empty cells.
    
    Returns:
    --------
    numpy.ndarray or None
        Solved puzzle, or None if no solution exists.
    """
    matrix = sudoku_to_exact_cover(puzzle)
    solver = DLXSolver(matrix)
    solution = solver.solve_one()
    
    if solution is None:
        return None
    
    return exact_cover_to_sudoku(solution, puzzle)


if __name__ == "__main__":
    # Example Sudoku puzzle
    puzzle = np.array([
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ])
    
    print("Original puzzle:")
    print(puzzle)
    print("\nSolving...")
    
    solution = solve_sudoku(puzzle)
    
    if solution is not None:
        print("\nSolution:")
        print(solution)
    else:
        print("\nNo solution found!")
