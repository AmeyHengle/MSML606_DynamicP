"""
algorithms.py
=============
Core routing algorithms for the Amazon Last-Mile Delivery Optimizer.

Three algorithms are implemented, ordered from least to most sophisticated:

  1. Greedy (Nearest Neighbor) -- intuitive but suboptimal
  2. 2-opt Local Search         -- heuristic improvement, scalable
  3. Held-Karp DP               -- exact optimal solution, O(2^n * n^2)

All algorithms accept a list of (x, y) coordinate tuples and a starting
index (default 0, the depot), and return:
  - route  : list of node indices in visit order, ending back at start
  - cost   : total Euclidean distance of that route

Author: Amey Hengle
Course: MSML606, Spring 2026
"""

import math
import time
from itertools import combinations


# ---------------------------------------------------------------------------
# Shared utility: Euclidean distance between two points
# ---------------------------------------------------------------------------

def euclidean(p1, p2):
    """
    Compute straight-line distance between two 2D points.

    Parameters
    ----------
    p1 : tuple (x, y)
    p2 : tuple (x, y)

    Returns
    -------
    float : Euclidean distance
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def build_distance_matrix(points):
    """
    Pre-compute all pairwise distances into an n x n matrix.

    Pre-computing avoids redundant sqrt calls during route evaluation,
    which matters when the same edge is queried thousands of times in
    the DP table.

    Parameters
    ----------
    points : list of (x, y) tuples

    Returns
    -------
    dist : list of lists, dist[i][j] = Euclidean distance from i to j
    """
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i][j] = euclidean(points[i], points[j])
    return dist


def route_cost(route, dist):
    """
    Sum all edge weights along a complete route (including return to start).

    Parameters
    ----------
    route : list of node indices (does NOT need to repeat start at end)
    dist  : precomputed distance matrix

    Returns
    -------
    float : total route distance
    """
    total = 0.0
    n = len(route)
    for i in range(n):
        total += dist[route[i]][route[(i + 1) % n]]
    return total


# ---------------------------------------------------------------------------
# Algorithm 1: Greedy Nearest Neighbor
# ---------------------------------------------------------------------------

def greedy_nearest_neighbor(points, start=0):
    """
    Greedy nearest-neighbor heuristic for TSP.

    Strategy: from the current location, always travel to the closest
    unvisited stop. Simple and fast (O(n^2)), but makes locally optimal
    choices that can be globally poor -- especially with clustered layouts
    where it exhausts a cluster then makes an expensive cross-cluster jump.

    Parameters
    ----------
    points : list of (x, y) tuples, points[0] is the depot by convention
    start  : int, index of the starting node (depot)

    Returns
    -------
    route : list of node indices, full round-trip
    cost  : float, total travel distance
    """
    n = len(points)
    dist = build_distance_matrix(points)

    visited = [False] * n
    route = [start]
    visited[start] = True

    for _ in range(n - 1):
        current = route[-1]
        nearest = None
        nearest_dist = float("inf")

        for j in range(n):
            if not visited[j] and dist[current][j] < nearest_dist:
                nearest_dist = dist[current][j]
                nearest = j

        route.append(nearest)
        visited[nearest] = True

    cost = route_cost(route, dist)
    return route, cost


# ---------------------------------------------------------------------------
# Algorithm 2: 2-opt Local Search
# ---------------------------------------------------------------------------

def two_opt(points, initial_route=None, start=0, max_iterations=None):
    """
    2-opt local search improvement for TSP.

    Starting from an initial route (defaults to greedy if not provided),
    repeatedly checks every pair of edges (i, i+1) and (j, j+1). If
    reversing the segment between them reduces total distance, that reversal
    is applied. Repeats until no improvement is found.

    Key insight: 2-opt fixes route crossings. Any time two edges cross on a
    map, reversing the middle segment removes the crossing and shortens the
    route. It cannot fix globally wrong orderings -- only local crossings.

    Time complexity: O(n^2) per pass, multiple passes until convergence.
    Practical for n up to ~200 nodes.

    Parameters
    ----------
    points        : list of (x, y) tuples
    initial_route : list of node indices to start from (optional)
    start         : depot index (used if initial_route not provided)
    max_iterations: cap on improvement passes (None = run to convergence)

    Returns
    -------
    route : improved list of node indices
    cost  : float, improved total distance
    """
    n = len(points)
    dist = build_distance_matrix(points)

    # Use greedy route as starting point if none provided
    if initial_route is None:
        route, _ = greedy_nearest_neighbor(points, start)
    else:
        route = list(initial_route)

    improved = True
    iteration = 0

    while improved:
        if max_iterations is not None and iteration >= max_iterations:
            break
        improved = False
        iteration += 1

        for i in range(len(route) - 1):
            for j in range(i + 2, len(route)):
                # Skip the wrap-around edge (last node back to first)
                if i == 0 and j == len(route) - 1:
                    continue

                # Edge weights before reversal
                a, b = route[i], route[i + 1]
                c, d = route[j], route[(j + 1) % len(route)]
                before = dist[a][b] + dist[c][d]

                # Edge weights after reversing the segment [i+1 .. j]
                after = dist[a][c] + dist[b][d]

                if after < before - 1e-10:
                    # Reverse the segment between i+1 and j (inclusive)
                    route[i + 1:j + 1] = route[i + 1:j + 1][::-1]
                    improved = True

    cost = route_cost(route, dist)
    return route, cost


# ---------------------------------------------------------------------------
# Algorithm 3: Held-Karp Dynamic Programming (Exact TSP)
# ---------------------------------------------------------------------------

def held_karp(points, start=0):
    """
    Held-Karp exact dynamic programming solution to TSP.

    This is the core DP algorithm for this project. It solves TSP optimally
    by decomposing the problem into overlapping subproblems:

      dp[S][i] = minimum distance to travel from the depot, visit exactly
                 the set of nodes S, and end at node i (where i in S).

    The recurrence is:
      dp[S][i] = min over all j in S\{i} of:
                    dp[S \ {i}][j] + dist[j][i]

    Base cases (single-hop from depot):
      dp[{depot, i}][i] = dist[depot][i]  for all i != depot

    After filling the table, the optimal tour cost is:
      min over all i != depot of:  dp[all_nodes][i] + dist[i][depot]

    Route reconstruction uses a parent pointer table stored alongside dp.

    Time complexity:  O(2^n * n^2)
    Space complexity: O(2^n * n)

    Practical limit: n <= 20 nodes (n=15 runs in milliseconds in Python).

    Parameters
    ----------
    points : list of (x, y) tuples, points[start] is the depot
    start  : int, depot index (default 0)

    Returns
    -------
    route : list of node indices, optimal round-trip starting and ending
            at the depot (depot is NOT repeated at the end)
    cost  : float, optimal total distance
    """
    n = len(points)
    dist = build_distance_matrix(points)

    # Remap so depot is always node 0 internally for bitmask simplicity
    # (We restore original indices at the end)
    nodes = list(range(n))
    if start != 0:
        nodes[0], nodes[start] = nodes[start], nodes[0]

    # dp[(S_bitmask, i)] = min cost to reach node i having visited set S
    # S is represented as an integer bitmask over the n nodes.
    # Bit k is set if node k has been visited.
    dp = {}
    parent = {}  # For route reconstruction

    # Base cases: travel directly from depot (node 0) to each other node
    depot = 0
    for i in range(1, n):
        S = (1 << depot) | (1 << i)  # visited = {depot, i}
        dp[(S, i)] = dist[nodes[depot]][nodes[i]]
        parent[(S, i)] = depot

    # Fill DP table for subsets of increasing size
    # We iterate over subset sizes from 3 up to n
    for size in range(3, n + 1):
        # Generate all subsets of {0..n-1} of this size that include the depot
        for S in _subsets_of_size(n, size, must_include=depot):
            # For each possible endpoint i in this subset (not the depot)
            for i in range(n):
                if i == depot or not (S & (1 << i)):
                    continue

                # Remove i from the subset to get the "previous" subset
                S_prev = S ^ (1 << i)

                best_cost = float("inf")
                best_prev = -1

                # Try every possible previous stop j in S_prev (not depot endpoint)
                for j in range(n):
                    if j == i or not (S_prev & (1 << j)):
                        continue
                    if (S_prev, j) not in dp:
                        continue

                    candidate = dp[(S_prev, j)] + dist[nodes[j]][nodes[i]]
                    if candidate < best_cost:
                        best_cost = candidate
                        best_prev = j

                if best_prev != -1:
                    dp[(S, i)] = best_cost
                    parent[(S, i)] = best_prev

    # Find the optimal last stop before returning to depot
    full_set = (1 << n) - 1  # bitmask with all nodes visited
    best_cost = float("inf")
    best_last = -1

    for i in range(1, n):
        if (full_set, i) not in dp:
            continue
        total = dp[(full_set, i)] + dist[nodes[i]][nodes[depot]]
        if total < best_cost:
            best_cost = total
            best_last = i

    # Reconstruct the optimal route by tracing parent pointers
    route_internal = _reconstruct_route(parent, full_set, best_last, depot, n)

    # Map internal indices back to original node indices
    route = [nodes[i] for i in route_internal]

    return route, best_cost


def _subsets_of_size(n, size, must_include):
    """
    Generate all bitmasks representing subsets of {0..n-1} of a given size
    that include a required node (must_include).

    Uses itertools.combinations for clarity.
    """
    all_nodes = list(range(n))
    remaining = [x for x in all_nodes if x != must_include]

    for combo in combinations(remaining, size - 1):
        S = 1 << must_include
        for node in combo:
            S |= (1 << node)
        yield S


def _reconstruct_route(parent, S, last, depot, n):
    """
    Trace parent pointers from the full set back to the depot
    to reconstruct the optimal route in forward order.

    Parameters
    ----------
    parent : dict mapping (S, i) -> previous node j
    S      : final bitmask (all nodes visited)
    last   : last node visited before returning to depot
    depot  : depot node index (0)
    n      : total number of nodes

    Returns
    -------
    list of node indices from depot to last (depot not repeated at end)
    """
    route = []
    current = last
    current_S = S

    while current != depot:
        route.append(current)
        prev = parent[(current_S, current)]
        current_S = current_S ^ (1 << current)
        current = prev

    route.append(depot)
    route.reverse()
    return route


# ---------------------------------------------------------------------------
# Comparison utility: run all three algorithms and report results
# ---------------------------------------------------------------------------

def compare_all(points, start=0):
    """
    Run greedy, 2-opt, and Held-Karp on the same set of points
    and return a summary dictionary for easy comparison.

    Parameters
    ----------
    points : list of (x, y) tuples
    start  : depot index

    Returns
    -------
    dict with keys: greedy, two_opt, held_karp
    Each value is a dict with: route, cost, time_ms
    """
    n = len(points)
    results = {}

    # Greedy
    t0 = time.perf_counter()
    g_route, g_cost = greedy_nearest_neighbor(points, start)
    results["greedy"] = {
        "route": g_route,
        "cost": round(g_cost, 4),
        "time_ms": round((time.perf_counter() - t0) * 1000, 3),
    }

    # 2-opt (starts from greedy route)
    t0 = time.perf_counter()
    o_route, o_cost = two_opt(points, initial_route=g_route, start=start)
    results["two_opt"] = {
        "route": o_route,
        "cost": round(o_cost, 4),
        "time_ms": round((time.perf_counter() - t0) * 1000, 3),
    }

    # Held-Karp (only run for small n to keep it practical)
    if n <= 20:
        t0 = time.perf_counter()
        hk_route, hk_cost = held_karp(points, start)
        results["held_karp"] = {
            "route": hk_route,
            "cost": round(hk_cost, 4),
            "time_ms": round((time.perf_counter() - t0) * 1000, 3),
        }
    else:
        results["held_karp"] = {
            "route": None,
            "cost": None,
            "time_ms": None,
            "note": f"Skipped: n={n} exceeds safe limit for exact DP (n<=20)",
        }

    return results
