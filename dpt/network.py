"""
Network analysis functions for the directed network evolution model.
All functions operate on a graph object (from graph module) and compute
various structural statistics.
"""

import math
from collections import deque


# ---------------------------------------------------------------------------
# Triangle density (clustering measure)
# ---------------------------------------------------------------------------
def triangle(g):
    """Compute fraction of two-step (length-2) paths that form a directed
    triangle with the starting node.

    For each node i, we count:
        count = number of pairs (j, k) such that i->j, j->k, and i->k exist.
        kinkout = total number of two-step paths i->j->k.

    Returns count / kinkout (ratio of completed triangles).
    """
    count = 0.0
    kinkout = 0.0
    for i in range(g.size()):
        start = g[i]
        # select
        for j in range(start.size()):
            end = start.at(j)
            end.flag = True

        # match
        for j in range(start.size()):
            mid = start.at(j)
            for k in range(mid.size()):
                if mid.at(k).flag:
                    count += 1
                kinkout += 1

        # reset
        for j in range(start.size()):
            start.at(j).flag = False

    return count / kinkout if kinkout > 0 else 0.0


# ---------------------------------------------------------------------------
# Fraction of isolated nodes
# ---------------------------------------------------------------------------
def proportion_0(g):
    """Fraction of nodes with out-degree == 0."""
    c = 0.0
    for i in range(g.size()):
        if g[i].size() == 0:
            c += 1.0
    return c / g.size()


# ---------------------------------------------------------------------------
# Degree-degree correlation (Pearson-like, directed version)
# ---------------------------------------------------------------------------
def corr_kinkout(g):
    """Compute the Pearson correlation between out-degree and in-degree
    across directed edges.

    Let k_out(i) and k_in(i) be the out- and in-degrees of node i.
    This computes:
        r = (E[k_out * k_in] - E[k_out] * E[k_in])
            / sqrt((E[k_out^2] - E[k_out]^2) * (E[k_in^2] - E[k_in]^2))
    where expectations are over all directed edges (i->j), using the out-
    degree of the source and in-degree of the target.
    """
    kinkout = 0.0
    kout = 0.0
    kout2 = 0.0
    kint2 = 0.0
    for i in range(g.size()):
        kinkout += g[i].size() * g[i].indegree
        kout += g[i].size()
        kout2 += g[i].size() * g[i].size()
        kint2 += g[i].indegree * g[i].indegree
    n = g.size()
    kinkout /= n
    kout /= n
    kout2 /= n
    kint2 /= n
    k2 = kout * kout
    denom = math.sqrt((kout2 - k2) * (kint2 - k2))
    return (kinkout - k2) / denom if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Update indegree for all nodes
# ---------------------------------------------------------------------------
def update_indegree(g):
    """Recalculate indegree for every node by scanning all directed edges."""
    for i in range(g.size()):
        g[i].indegree = 0
        
    for i in range(g.size()):
        p = g[i]
        for j in range(p.size()):
            p.at(j).indegree += 1


# ---------------------------------------------------------------------------
# Weakly connected components analysis
# ---------------------------------------------------------------------------
class WeaklyConnectedComponent:
    """Compute weakly connected components (ignoring edge direction)
    and return statistics.

    Attributes:
        giant_cluster_fraction: fraction of nodes in the largest component.
        average_cluster_sizes:  average size of all components.
    """
    def __init__(self, g):
        n = g.size()
        visited = [False] * n
        # create adjacent list
        adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(g[i].size()):
                _neigh = g[i].at(j)
                for k in range(n):
                    if g[k] is _neigh:
                        adj[i].append(k)
                        adj[k].append(i)
                        break
        # bfs gcc
        components = []
        for i in range(n):
            if not visited[i]:
                q = deque([i])
                visited[i] = True
                size = 0
                while q:
                    v = q.popleft()
                    size += 1
                    for nb in adj[v]:
                        if not visited[nb]:
                            visited[nb] = True
                            q.append(nb)
                components.append(size)
        
        components.sort(reverse=True)
        self.giant_cluster_fraction = components[0] / n if components else 0.0
        self.average_cluster_sizes = sum(components) / len(components) if components else 0.0
