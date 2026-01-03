"""
Simple example demonstrating DLX usage.
"""

from dlxsolver import DLXSolver, solve_exact_cover

# Example exact cover problem
# We want to cover columns 0, 1, 2, 3, 4, 5, 6 using rows
matrix = [
    [1, 0, 0, 1, 0, 0, 1],  # Row 0 covers columns 0, 3, 6
    [1, 0, 0, 1, 0, 0, 0],  # Row 1 covers columns 0, 3
    [0, 0, 0, 1, 1, 0, 1],  # Row 2 covers columns 3, 4, 6
    [0, 0, 1, 0, 1, 1, 0],  # Row 3 covers columns 2, 4, 5
    [0, 1, 1, 0, 0, 1, 1],  # Row 4 covers columns 1, 2, 5, 6
    [0, 1, 0, 0, 0, 0, 1],  # Row 5 covers columns 1, 6
]

print("Constraint matrix:")
for i, row in enumerate(matrix):
    print(f"Row {i}: {row}")

print("\nFinding all solutions...")
solver = DLXSolver(matrix)
solutions = solver.solve(find_all=True)

print(f"\nFound {len(solutions)} solution(s):")
for i, solution in enumerate(solutions):
    print(f"Solution {i + 1}: rows {solution}")
    print(f"  Covers: {[sum(matrix[r]) for r in solution]}")

print("\nFinding first solution only...")
first_solution = solver.solve_one()
print(f"First solution: rows {first_solution}")

# Using convenience function
print("\nUsing convenience function...")
solutions2 = solve_exact_cover(matrix, find_all=False)
print(f"Solutions: {solutions2}")
