# ---------------------------------------------------------------------------
# Node class (A node in the directed graph.)
# ---------------------------------------------------------------------------
class Node:
    """
    Attributes:
        out_edges: list[int]
            list of Node objects that this node points to.
        indegree: int
            number of incoming edges (recomputed each time step)
        flag: bool
            boolean marker (used in triangle counting and edge probability computation).
        count: int    
            counter (used to accumulate two-step neighbor counts during edge probability computation).
    """
    def __init__(self):
        self.out_edges = []
        self.indegree = 0
        self.flag = False
        self.count = 0
    
    def size(self):
        return len(self.out_edges)
    
    def back(self):
        return self.out_edges[-1]
    
    def at(self, idx):
        return self.out_edges[idx]

    def push_back(self, node):
        self.out_edges.append(node)

    def pop_back(self):
        if self.out_edges:
            self.out_edges.pop()


# ---------------------------------------------------------------------------
# Graph class (container of nodes)
# ---------------------------------------------------------------------------
class Graph:
    def __init__(self):
        self._nodes = []

    def resize(self, n):
        self._nodes = [Node() for _ in range(n)]

    def size(self):
        return len(self._nodes)

    def __getitem__(self, idx):
        return self._nodes[idx]

    def __setitem__(self, idx, val):
        self._nodes[idx] = val

    def __iter__(self):
        return iter(self._nodes)
