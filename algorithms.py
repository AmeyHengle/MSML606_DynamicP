"""
algorithms.py
=============
routing algorithms for the amazon last-mile delivery optimizer.

algorithms implemented (weakest to strongest):
  1. random permutation       -- absolute baseline
  2. greedy nearest neighbor  -- o(n^2), intuitive but locally optimal only
  3. 2-opt local search       -- o(n^2) per pass, fixes edge crossings
  4. or-opt                   -- o(k*n^2) per pass, fixes insertion order
  5. held-karp dp             -- exact, o(2^n * n^2), feasible up to n~15

all algorithms accept a list of (x, y) coordinate tuples and a starting
index (default 0, the depot), and return (route, cost).

author: amey hengle | msml606, spring 2026
"""

import math
import time
from itertools import combinations


def euclidean(p1, p2):
    """straight-line distance between two 2d points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def build_distance_matrix(points):
    """precompute all pairwise euclidean distances into an n x n matrix."""
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i][j] = euclidean(points[i], points[j])
    return dist


def route_cost(route, dist):
    """sum all edge weights along a route including the return to start."""
    total = 0.0
    n = len(route)
    for i in range(n):
        total += dist[route[i]][route[(i + 1) % n]]
    return total


def random_route(points, start=0, seed=None):
    """
    visit stops in a random order. serves as the absolute baseline to show
    how much worse an unguided approach is compared to any algorithm.
    """
    import random as _random
    if seed is not None:
        _random.seed(seed)
    dist = build_distance_matrix(points)
    n = len(points)
    others = list(range(n))
    others.remove(start)
    _random.shuffle(others)
    route = [start] + others
    return route, route_cost(route, dist)


def greedy_nearest_neighbor(points, start=0):
    """
    from the current stop, always travel to the closest unvisited stop.
    runs in o(n^2). fast but makes locally optimal decisions that can be
    globally poor, especially with clustered stop layouts.
    """
    n = len(points)
    dist = build_distance_matrix(points)
    visited = [False] * n
    route = [start]
    visited[start] = True

    for _ in range(n - 1):
        current = route[-1]
        nearest, nearest_dist = None, float("inf")
        for j in range(n):
            if not visited[j] and dist[current][j] < nearest_dist:
                nearest_dist = dist[current][j]
                nearest = j
        route.append(nearest)
        visited[nearest] = True

    return route, route_cost(route, dist)


def two_opt(points, initial_route=None, start=0, max_iterations=None):
    """
    iteratively reverse segments of the route to remove edge crossings.
    any time two route edges cross on a map, reversing the segment between
    the crossing points shortens the total route. repeats until no improving
    swap exists. o(n^2) per pass, multiple passes until convergence.
    defaults to using the greedy route as its starting point.
    """
    dist = build_distance_matrix(points)

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
                if i == 0 and j == len(route) - 1:
                    continue
                a, b = route[i], route[i + 1]
                c, d = route[j], route[(j + 1) % len(route)]
                if dist[a][c] + dist[b][d] < dist[a][b] + dist[c][d] - 1e-10:
                    route[i + 1:j + 1] = route[i + 1:j + 1][::-1]
                    improved = True

    return route, route_cost(route, dist)


def or_opt(points, initial_route=None, start=0, segment_sizes=(1, 2, 3)):
    """
    remove a segment of 1, 2, or 3 consecutive stops and reinsert it at the
    best position elsewhere in the route. fixes cases that 2-opt misses:
    stops that are in the wrong position but whose edges do not cross.
    o(k * n^2) per pass where k = number of segment sizes tried.
    warm-started from the 2-opt result for incremental improvement.
    """
    dist = build_distance_matrix(points)

    if initial_route is None:
        route, _ = greedy_nearest_neighbor(points, start)
    else:
        route = list(initial_route)

    improved = True
    while improved:
        improved = False

        for k in segment_sizes:
            i = 1
            while i < len(route) - k + 1:
                segment = route[i:i + k]
                skeleton = route[:i] + route[i + k:]

                removal_gain = (
                    dist[route[i - 1]][segment[0]]
                    + dist[segment[-1]][route[i + k] if i + k < len(route) else route[0]]
                    - dist[route[i - 1]][route[i + k] if i + k < len(route) else route[0]]
                )

                best_gain, best_j = 0, -1

                for j in range(len(skeleton)):
                    if j == i - 1 or j == i - 2:
                        continue
                    a = skeleton[j]
                    b = skeleton[(j + 1) % len(skeleton)]
                    insertion_cost = dist[a][segment[0]] + dist[segment[-1]][b] - dist[a][b]
                    gain = removal_gain - insertion_cost
                    if gain > best_gain + 1e-10:
                        best_gain = gain
                        best_j = j

                if best_j != -1:
                    route = skeleton[:best_j + 1] + segment + skeleton[best_j + 1:]
                    improved = True
                    break
                else:
                    i += 1

            if improved:
                break

    return route, route_cost(route, dist)


def held_karp(points, start=0):
    """
    exact dp solution to tsp using the held-karp algorithm.

    defines dp[s][i] = minimum cost to travel from the depot, visit exactly
    the set s of stops, and end at stop i. fills the table bottom-up from
    single-hop base cases to the full route, then reconstructs the optimal
    path via parent pointers.

    time: o(2^n * n^2), space: o(2^n * n).
    exact and optimal, but infeasible beyond n ~ 20 nodes.
    """
    n = len(points)
    dist = build_distance_matrix(points)

    nodes = list(range(n))
    if start != 0:
        nodes[0], nodes[start] = nodes[start], nodes[0]

    dp = {}
    parent = {}

    depot = 0
    for i in range(1, n):
        S = (1 << depot) | (1 << i)
        dp[(S, i)] = dist[nodes[depot]][nodes[i]]
        parent[(S, i)] = depot

    for size in range(3, n + 1):
        for S in _subsets_of_size(n, size, must_include=depot):
            for i in range(n):
                if i == depot or not (S & (1 << i)):
                    continue
                S_prev = S ^ (1 << i)
                best_cost, best_prev = float("inf"), -1
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

    full_set = (1 << n) - 1
    best_cost, best_last = float("inf"), -1
    for i in range(1, n):
        if (full_set, i) not in dp:
            continue
        total = dp[(full_set, i)] + dist[nodes[i]][nodes[depot]]
        if total < best_cost:
            best_cost = total
            best_last = i

    route_internal = _reconstruct_route(parent, full_set, best_last, depot, n)
    route = [nodes[i] for i in route_internal]
    return route, best_cost


def _subsets_of_size(n, size, must_include):
    """generate all bitmasks of size `size` over {0..n-1} that include must_include."""
    remaining = [x for x in range(n) if x != must_include]
    for combo in combinations(remaining, size - 1):
        S = 1 << must_include
        for node in combo:
            S |= (1 << node)
        yield S


def _reconstruct_route(parent, S, last, depot, n):
    """trace parent pointers from the full set back to depot to recover the route."""
    route = []
    current, current_S = last, S
    while current != depot:
        route.append(current)
        prev = parent[(current_S, current)]
        current_S = current_S ^ (1 << current)
        current = prev
    route.append(depot)
    route.reverse()
    return route


def compare_all(points, start=0, include_random=True, held_karp_limit=15):
    """
    run all five algorithms on the same point set and return a results dict.
    held-karp is only run when n <= held_karp_limit to avoid infeasible runtimes.
    each entry has keys: route, cost, time_ms.
    """
    n = len(points)
    results = {}

    if include_random:
        t0 = time.perf_counter()
        r_route, r_cost = random_route(points, start)
        results["random"] = {"route": r_route, "cost": round(r_cost, 4),
                             "time_ms": round((time.perf_counter() - t0) * 1000, 3)}

    t0 = time.perf_counter()
    g_route, g_cost = greedy_nearest_neighbor(points, start)
    results["greedy"] = {"route": g_route, "cost": round(g_cost, 4),
                         "time_ms": round((time.perf_counter() - t0) * 1000, 3)}

    t0 = time.perf_counter()
    o_route, o_cost = two_opt(points, initial_route=g_route, start=start)
    results["two_opt"] = {"route": o_route, "cost": round(o_cost, 4),
                          "time_ms": round((time.perf_counter() - t0) * 1000, 3)}

    t0 = time.perf_counter()
    oo_route, oo_cost = or_opt(points, initial_route=o_route, start=start)
    results["or_opt"] = {"route": oo_route, "cost": round(oo_cost, 4),
                         "time_ms": round((time.perf_counter() - t0) * 1000, 3)}

    if n <= held_karp_limit:
        t0 = time.perf_counter()
        hk_route, hk_cost = held_karp(points, start)
        results["held_karp"] = {"route": hk_route, "cost": round(hk_cost, 4),
                                "time_ms": round((time.perf_counter() - t0) * 1000, 3)}
    else:
        results["held_karp"] = {"route": None, "cost": None, "time_ms": None,
                                "note": f"skipped: n={n} > held_karp_limit={held_karp_limit}"}

    return results
