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
    
    def __init__(self, str name):
        Node.__init__(self)
        self.column = self
        self.size = 0
        self.name = name

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
        
        # Create header node
        self.header = Column("header")
        
        # Create column headers
        cdef Column col
        cdef int i, j
        
        for i in range(num_cols):
            col = Column("col_%d" % i)
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
            
            for j in range(num_cols):
                if mat[i, j] == 1:
                    node = Node()
                    node.row_id = i
                    node.column = self.columns[j]
                    
                    # Link to column
                    node.up = self.columns[j].up
                    node.down = self.columns[j]
                    self.columns[j].up.down = node
                    self.columns[j].up = node
                    self.columns[j].size += 1
                    
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
        col.right.left = col.left
        col.left.right = col.right
        
        cdef Node i = col.down
        cdef Node j
        while i != col:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down
    
    cdef void uncover(self, Column col):
        """Uncover a column."""
        cdef Node i = col.up
        cdef Node j
        while i != col:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        
        col.right.left = col
        col.left.right = col
    
    cdef Column choose_column(self):
        """Choose the column with the smallest size (S heuristic)."""
        # Check if no columns remain
        if self.header.right == self.header:
            return None
        
        cdef Column c = <Column>self.header.right
        cdef Column best = c
        cdef int min_size = c.size
        
        while c != self.header:
            if c.size < min_size:
                min_size = c.size
                best = c
            c = <Column>c.right
        
        return best if best.size > 0 else None
    
    cdef void search(self, int k):
        """Recursive search for solutions."""
        if self.header.right == self.header:
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
        
        while r != c:
            self.solution.append(r.row_id)
            
            j = r.right
            while j != r:
                self.cover(j.column)
                j = j.right
            
            self.search(k + 1)
            
            if not self.find_all and len(self.solutions) > 0:
                # Uncover all columns covered in this iteration before returning
                j = r.left
                while j != r:
                    self.uncover(j.column)
                    j = j.left
                self.solution.pop()
                self.uncover(c)
                return
            
            self.solution.pop()
            
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
