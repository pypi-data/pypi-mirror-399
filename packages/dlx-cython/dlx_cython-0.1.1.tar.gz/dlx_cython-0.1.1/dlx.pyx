# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True

"""
DLX (Dancing Links) implementation in Cython.

DLX is an algorithm for solving exact cover problems using a technique
called "dancing links" which efficiently implements backtracking.
"""

cimport numpy as np
import numpy as np
from libc.stdint cimport uint64_t

cdef class Node:
    """A node in the DLX sparse matrix representation."""
    cdef public Node left, right, up, down
    cdef public Column column
    cdef public int row_id
    
    def __init__(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None
        self.row_id = -1

cdef class Column(Node):
    """A column header node in the DLX matrix."""
    cdef public int size
    cdef public str name
    cdef public int index  # Column index for bitmask optimization
    
    def __init__(self, str name, int index=-1):
        Node.__init__(self)
        self.column = self
        self.size = 0
        self.name = name
        self.index = index

cdef class DLX:
    """Dancing Links implementation for solving exact cover problems."""
    
    cdef Column header
    cdef list columns
    cdef list nodes
    cdef list solution
    cdef list solutions
    cdef int num_rows
    cdef int num_cols
    cdef bool find_all
    # Bitmask optimization for ≤64 columns
    cdef bool use_mask
    cdef uint64_t active_mask
    cdef int[64] col_sizes_mask  # Column sizes when using mask
    cdef uint64_t[64] row_masks  # Bitmask for each row (constraint set)
    
    def __init__(self, int num_rows, int num_cols, object matrix):
        """
        Initialize DLX solver.
        
        Parameters:
        -----------
        num_rows : int
            Number of rows in the constraint matrix
        num_cols : int
            Number of columns in the constraint matrix
        matrix : array-like
            Binary matrix where matrix[i][j] = 1 means row i covers column j
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.find_all = False
        self.columns = []
        self.nodes = []
        self.solution = []
        self.solutions = []
        
        # Declare variables
        cdef Column col
        cdef int i, j
        
        # Use bitmask optimization for ≤64 columns
        self.use_mask = (num_cols <= 64)
        
        # Always create header node (needed for some code paths)
        self.header = Column("header", -1)
        
        if self.use_mask:
            # Initialize bitmask: all columns active (bits 0 to num_cols-1 set)
            self.active_mask = ((<uint64_t>1 << num_cols) - 1)
            # Initialize column sizes array
            for i in range(64):
                self.col_sizes_mask[i] = 0
            # Initialize row masks (one bitmask per row)
            for i in range(64):
                self.row_masks[i] = 0
        
        # Create column headers (still needed for up/down node linking)
        
        for i in range(num_cols):
            col = Column("col_%d" % i, i)  # Store index
            if not self.use_mask:
                # Only link columns in standard mode
                col.left = self.header.left
                col.right = self.header
                self.header.left.right = col
                self.header.left = col
            self.columns.append(col)
        
        # Convert matrix to numpy array if needed
        cdef np.ndarray[np.int32_t, ndim=2] mat
        if not isinstance(matrix, np.ndarray):
            mat = np.array(matrix, dtype=np.int32)
        else:
            mat = np.asarray(matrix, dtype=np.int32)
        
        # Create nodes for each 1 in the matrix
        cdef Node node
        cdef Node prev_node
        cdef list row_nodes
        
        for i in range(num_rows):
            row_nodes = []
            
            # Build bitmask for this row if using mask optimization
            if self.use_mask and i < 64:
                self.row_masks[i] = 0
            
            for j in range(num_cols):
                if mat[i, j] == 1:
                    node = Node()
                    node.row_id = i
                    node.column = self.columns[j]
                    
                    # Update row bitmask if using mask optimization
                    if self.use_mask and i < 64:
                        self.row_masks[i] |= (<uint64_t>1 << j)
                    
                    # Link to column
                    node.up = self.columns[j].up
                    node.down = self.columns[j]
                    self.columns[j].up.down = node
                    self.columns[j].up = node
                    self.columns[j].size += 1
                    if self.use_mask:
                        self.col_sizes_mask[j] += 1
                    
                    # Link to row
                    if len(row_nodes) > 0:
                        prev_node = row_nodes[len(row_nodes) - 1]
                        node.left = prev_node
                        node.right = prev_node.right
                        prev_node.right.left = node
                        prev_node.right = node
                    
                    row_nodes.append(node)
                    self.nodes.append(node)
            
            # Close the row (circular)
            row_len = len(row_nodes)
            if row_len > 0:
                row_nodes[0].left = row_nodes[row_len - 1]
                row_nodes[row_len - 1].right = row_nodes[0]
    
    cdef void cover(self, Column col):
        """Cover a column."""
        cdef int col_idx
        cdef Node i, j
        
        if self.use_mask:
            # Remove column from active mask using stored index
            col_idx = col.index
            self.active_mask &= ~(<uint64_t>1 << col_idx)
        else:
            # Standard linked list removal
            col.right.left = col.left
            col.left.right = col.right
        
        i = col.down
        while i != col:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                if self.use_mask:
                    col_idx = j.column.index
                    self.col_sizes_mask[col_idx] -= 1
                j = j.right
            i = i.down
    
    cdef void uncover(self, Column col):
        """Uncover a column."""
        cdef int col_idx
        cdef Node i, j
        
        i = col.up
        while i != col:
            j = i.left
            while j != i:
                j.column.size += 1
                if self.use_mask:
                    col_idx = j.column.index
                    self.col_sizes_mask[col_idx] += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        
        if self.use_mask:
            # Restore column to active mask using stored index
            col_idx = col.index
            self.active_mask |= (<uint64_t>1 << col_idx)
        else:
            # Standard linked list restoration
            col.right.left = col
            col.left.right = col
    
    cdef Column choose_column(self):
        """Choose the column with the smallest size (S heuristic)."""
        cdef int i, col_idx, min_size, best_idx
        cdef uint64_t mask, temp_mask
        cdef Column best, c
        
        if self.use_mask:
            # Use bitmask to find active columns
            mask = self.active_mask
            if mask == 0:
                return None
            
            # Find column with smallest size among active columns
            best_idx = -1
            min_size = 999999  # Large number
            
            for i in range(self.num_cols):
                if (mask >> i) & 1:  # Column i is active
                    # Use col_sizes_mask when using mask mode
                    if self.col_sizes_mask[i] < min_size:
                        min_size = self.col_sizes_mask[i]
                        best_idx = i
            
            if best_idx == -1 or min_size == 0:
                return None
            
            return self.columns[best_idx]
        else:
            # Standard linked list traversal
            if self.header.right == self.header:
                return None
            
            c = <Column>self.header.right
            best = c
            min_size = c.size
            
            while c != self.header:
                if c.size < min_size:
                    min_size = c.size
                    best = c
                c = <Column>c.right
            
            return best if best.size > 0 else None
    
    cdef void cover_row_columns(self, int row_id, int exclude_col_idx=-1):
        """Cover all columns for a given row using row mask (optimized)."""
        if not self.use_mask or row_id >= 64:
            return
        
        cdef uint64_t row_mask = self.row_masks[row_id]
        cdef int col_idx
        
        # Cover all columns in the row mask, excluding the specified column
        # (which is already covered)
        for col_idx in range(self.num_cols):
            if col_idx == exclude_col_idx:
                continue
            if (row_mask >> col_idx) & 1:
                # Only cover if column is still active (not already covered)
                if (self.active_mask >> col_idx) & 1:
                    self.cover(self.columns[col_idx])
    
    cdef void uncover_row_columns(self, int row_id, int exclude_col_idx=-1):
        """Uncover all columns for a given row using row mask (optimized)."""
        if not self.use_mask or row_id >= 64:
            return
        
        cdef uint64_t row_mask = self.row_masks[row_id]
        cdef int col_idx
        
        # Uncover in reverse order for proper backtracking, excluding the specified column
        col_idx = self.num_cols - 1
        while col_idx >= 0:
            if col_idx == exclude_col_idx:
                col_idx -= 1
                continue
            if (row_mask >> col_idx) & 1:
                self.uncover(self.columns[col_idx])
            col_idx -= 1
    
    cdef bint is_row_valid(self, int row_id, int exclude_col_idx=-1):
        """Check if a row is still valid (at least one column it covers is still active)."""
        if not self.use_mask or row_id >= 64:
            return True  # Fall back to standard validation
        
        cdef uint64_t row_mask = self.row_masks[row_id]
        # If exclude_col_idx is specified, temporarily add it back to active_mask for checking
        # This is because we're checking validity AFTER covering column c, but column c
        # is part of the row, so we should consider it as "active" for validity purposes
        cdef uint64_t check_mask = self.active_mask
        if exclude_col_idx >= 0 and exclude_col_idx < self.num_cols:
            check_mask |= (<uint64_t>1 << exclude_col_idx)
        
        # Row is valid if at least one column it covers is still active
        # (including the excluded column, since it's part of the row)
        return (row_mask & check_mask) != 0
    
    cdef void search(self, int k):
        """Recursive search for solutions."""
        # Check if solution found
        cdef bint solution_found = False
        if self.use_mask:
            solution_found = (self.active_mask == 0)
        else:
            solution_found = (self.header.right == self.header)
        
        if solution_found:
            # Found a solution
            self.solutions.append(list(self.solution))
            if not self.find_all:
                return
            return
        
        cdef Column c = self.choose_column()
        if c is None:
            return
        
        self.cover(c)
        
        cdef Node r = c.down
        cdef Node j
        cdef int row_id
        
        while r != c:
            row_id = r.row_id
            
            # Early validation: skip rows that are no longer valid (optimization)
            # A row is invalid if none of its columns are still active
            # Note: We pass c.index because column c is already covered, but it's part of the row
            # so we should consider it when checking validity
            if self.use_mask and row_id < 64:
                if not self.is_row_valid(row_id, c.index):
                    r = r.down
                    continue
            
            self.solution.append(row_id)
            
            # Cover columns using row mask (optimized) or standard traversal
            if self.use_mask and row_id < 64:
                # Exclude column c (already covered) from row mask coverage
                self.cover_row_columns(row_id, c.index)
            else:
                # Standard linked list traversal
                j = r.right
                while j != r:
                    self.cover(j.column)
                    j = j.right
            
            self.search(k + 1)
            
            if not self.find_all and len(self.solutions) > 0:
                # Uncover all columns covered in this iteration before returning
                if self.use_mask and row_id < 64:
                    self.uncover_row_columns(row_id, c.index)
                else:
                    j = r.left
                    while j != r:
                        self.uncover(j.column)
                        j = j.left
                self.solution.pop()
                self.uncover(c)
                return
            
            self.solution.pop()
            
            # Uncover columns using row mask (optimized) or standard traversal
            if self.use_mask and row_id < 64:
                self.uncover_row_columns(row_id, c.index)
            else:
                j = r.left
                while j != r:
                    self.uncover(j.column)
                    j = j.left
            
            r = r.down
        
        self.uncover(c)
    
    def solve(self, bool find_all=True):
        """
        Solve the exact cover problem.
        
        Parameters:
        -----------
        find_all : bool
            If True, find all solutions. If False, find first solution only.
        
        Returns:
        --------
        list of lists
            List of solutions, where each solution is a list of row indices.
        """
        self.find_all = find_all
        self.solutions = []
        self.solution = []
        
        self.search(0)
        
        return self.solutions
    
    def solve_one(self):
        """Find the first solution."""
        solutions = self.solve(find_all=False)
        return solutions[0] if solutions else None
