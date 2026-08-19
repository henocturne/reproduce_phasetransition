"""
Main simulation driver for the directed network evolution model.

Imports graph structures from graph.py and analysis functions from analysis.py.
Usage: python org.py <alpha> <beta> <N>
"""

import random
import sys

from graph import Graph
from network import *

# triangle, proportion_0, corr_kinkout, update_indegree, WeaklyConnectedComponent


MAX_T = 100
STEP_T = 0.1
STEP_CUT = 0.1
MAX_CUT = 1

def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <alpha> <beta> <N>", file=sys.stderr)
        sys.exit(1)

    alpha = float(sys.argv[1])
    beta  = float(sys.argv[2])
    N     = int(sys.argv[3])

    # -------------------------------------------------------------------
    # Input and Init
    # -------------------------------------------------------------------

    dt   = 0.1
    gamma = 1.0

    g = Graph()
    g.resize(N)

    for i in range(g.size()):
        _node = g[i]
        _node.flag = False
        _node.count = 0

    
    name = f"out_{N}_{alpha}_{beta}.dat"
    with open(name, "w") as out:
        out.write(  "# t  <k>  <k^2>  <k>/N  <k^2>/N^2  "
                    "corr_kinkout  triangle  proportion_0  giant_frac  avg_cluster_size\n")

        t = 0.0
        t_next = 0.0


        while t < MAX_T:
            avgk    = 0.0
            avgk2   = 0.0
            max_cut = 0.0
            update_indegree(g)

            for i in range(g.size()):
                _node = g[i]
                new_node = []

                # --- Mark out-neighbors and accumulate two-step counts ----
                for j in range(_node.size()):
                    _mid = _node.at(j)
                    _mid.flag = True
                    for k in range(_mid.size()):
                        _mid.at(k).count += 1

                # --- Edge creation ----------------------------------------
                for j in range(g.size()):
                    _mid = g[j]
                    if _mid is _node or _mid.flag:
                        continue
                    cut = (alpha / N + beta * _mid.count) * dt
                    max_cut = max(max_cut, cut)

                    if cut > MAX_CUT:
                        print(  f"Warning! - cut = {cut} > 1 at node {j}, "
                                f"count = {_mid.count}")
                        sys.exit(1)
                    if random.random() < cut:
                        new_node.append(_mid)

                # --- Clear flags and counts --------------------------------
                for j in range(_node.size()):
                    _mid = _node.at(j)
                    _mid.flag = False
                    for k in range(_mid.size()):
                        _mid.at(k).count = 0

                # --- Edge removal (stochastic) -----------------------------
                j = 0
                while j < _node.size():
                    if random.random() < gamma * dt:
                        _node.out_edges[j] = _node.back()
                        _node.pop_back()
                    else:
                        j += 1

                # --- Add new edges -----------------------------------------
                for j in range(len(new_node)):
                    _node.push_back(new_node[j])

                avgk  += _node.size()
                avgk2 += _node.size() * _node.size()

            # --- Adaptive time step ----------------------------------------
            if max_cut > STEP_CUT:
                dt *= STEP_CUT / max_cut

            avgk  /= N
            avgk2 /= N

            # --- Output statistics every 0.1 time units --------------------
            if t >= t_next:
                update_indegree(g)
                wc = WeaklyConnectedComponent(g)

                # print(f"t={t:.3f}  <k>={avek:.4f}  <k^2>={avek2:.4f}")

                out.write(  f"{t} {avgk} {avgk2} {avgk/N} {avgk2/N/N} "
                            f"{corr_kinkout(g)} {triangle(g)} {proportion_0(g)} "
                            f"{wc.giant_cluster_fraction} "
                            f"{wc.average_cluster_sizes}\n")
                out.flush()

                # --- Save network snapshot ---------------------------------
                name = f"net_{N}_{alpha}_{beta}_{t:.3f}.dat"
                if int(t * 10  ) % 10 == 0:
                    with open(name, "w") as save:
                        for ii in range(g.size()):
                            _source = g[ii]
                            for jj in range(_source.size()):
                                _target = _source.at(jj)
                                target_idx = None
                                for kk in range(g.size()):
                                    if g[kk] is _target:
                                        target_idx = kk
                                        break
                                save.write(f"{ii} {target_idx}\n")

                t_next += STEP_T

            t += dt

    # -------------------------------------------------------------------
    # Save final network
    # -------------------------------------------------------------------
    name = f"net_{N}_{alpha}_{beta}.dat"
    with open(name, "w") as save_final:
        for ii in range(g.size()):
            _source = g[ii]
            for jj in range(_source.size()):
                _target = _source.at(jj)
                target_idx = None
                for kk in range(g.size()):
                    if g[kk] is _target:
                        target_idx = kk
                        break
                save_final.write(f"{ii} {target_idx}\n")

    print(f"Done. Output written to out_{N}_{alpha}_{beta}.dat")
    print(f"Final network saved to net_{N}_{alpha}_{beta}.dat")


if __name__ == "__main__":
    main()
