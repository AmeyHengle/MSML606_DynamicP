"""
main.py
=======
Command-line demo for the Amazon Last-Mile Delivery Route Optimizer.

Runs all three algorithms (Greedy, 2-opt, Held-Karp DP) on the bundled
15-stop delivery route near College Park, MD and prints a side-by-side
comparison of routes, costs, and runtimes.

Usage
-----
    python main.py                        # run on sample route (15 stops)
    python main.py --stops 10             # random route with 10 stops
    python main.py --stops 12 --seed 42   # reproducible random route
    python main.py --no-hk                # skip Held-Karp (for large n)

Author: Amey Hengle
Course: MSML606, Spring 2026
"""

import argparse
import sys

from algorithms import compare_all, greedy_nearest_neighbor
from dataset import (
    load_sample_route,
    stops_to_points,
    generate_random_stops,
    total_route_distance_km,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_header(title):
    width = 62
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(label):
    print(f"\n  -- {label} --")


def print_route(route, stops=None):
    """Print route as a readable arrow chain."""
    if stops:
        labels = [stops[i]["name"] for i in route]
    else:
        labels = [str(i) for i in route]
    # Wrap back to depot
    labels.append(labels[0])
    print("  " + " -> ".join(labels))


def print_comparison_table(results, stops=None):
    """Print a formatted comparison table of all algorithm results."""
    algs = ["greedy", "two_opt", "held_karp"]
    labels = {
        "greedy": "Greedy (nearest neighbor)",
        "two_opt": "2-opt (local search)",
        "held_karp": "Held-Karp DP (exact)",
    }

    print()
    print(f"  {'Algorithm':<28} {'Distance':>12} {'Time (ms)':>10}  {'vs Greedy':>10}")
    print("  " + "-" * 64)

    greedy_cost = results["greedy"]["cost"]

    for alg in algs:
        r = results.get(alg, {})
        if not r or r.get("cost") is None:
            note = r.get("note", "not available")
            print(f"  {labels[alg]:<28} {'—':>12} {'—':>10}  {note}")
            continue

        cost = r["cost"]
        ms = r["time_ms"]
        pct = ((greedy_cost - cost) / greedy_cost * 100) if alg != "greedy" else 0.0
        pct_str = f"{pct:+.1f}%" if alg != "greedy" else "baseline"
        print(f"  {labels[alg]:<28} {cost:>12.2f} {ms:>10.2f}  {pct_str:>10}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Amazon Last-Mile Delivery Route Optimizer"
    )
    parser.add_argument(
        "--stops", type=int, default=None,
        help="Number of random stops to generate (default: use sample route)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility (used with --stops)"
    )
    parser.add_argument(
        "--no-hk", action="store_true",
        help="Skip Held-Karp DP (useful for n > 20)"
    )
    args = parser.parse_args()

    # Load data
    if args.stops is not None:
        n = args.stops
        if n < 3:
            print("Error: need at least 3 stops.", file=sys.stderr)
            sys.exit(1)
        if n > 20 and not args.no_hk:
            print(f"Warning: n={n} is large for Held-Karp. Adding --no-hk automatically.")
            args.no_hk = True

        print_header(f"Amazon Delivery Route Optimizer  |  {n} random stops")
        stops = generate_random_stops(n, seed=args.seed)
        source = f"randomly generated ({n} stops, seed={args.seed})"
    else:
        print_header("Amazon Delivery Route Optimizer  |  College Park, MD route")
        stops = load_sample_route()
        n = len(stops)
        source = "sample_route.json (15 stops, College Park / Hyattsville MD)"

    print(f"\n  Dataset  : {source}")
    print(f"  Depot    : {stops[0]['name']} -- {stops[0]['address']}")
    print(f"  Stops    : {n - 1} delivery stops + 1 depot = {n} nodes total")

    # Convert to coordinate pairs for algorithm input
    points = stops_to_points(stops)

    # Run all algorithms
    print_section("Running algorithms...")
    results = compare_all(points, start=0)
    if args.no_hk:
        results["held_karp"] = {"route": None, "cost": None, "time_ms": None,
                                 "note": "skipped via --no-hk flag"}

    # Print routes
    print_section("Routes")
    for alg, label in [("greedy", "Greedy"), ("two_opt", "2-opt"),
                        ("held_karp", "Held-Karp")]:
        r = results.get(alg, {})
        if r.get("route"):
            print(f"\n  {label}:")
            print_route(r["route"], stops)

    # Print comparison table
    print_section("Performance comparison")
    print_comparison_table(results, stops)

    # Real-world distances (km) using haversine
    print_section("Real-world distances (haversine)")
    for alg, label in [("greedy", "Greedy"), ("two_opt", "2-opt"),
                        ("held_karp", "Held-Karp")]:
        r = results.get(alg, {})
        if r.get("route"):
            km = total_route_distance_km(stops, r["route"])
            print(f"  {label:<22}: {km:.2f} km  (~{km * 0.621:.2f} miles)")

    # Summary insight
    print()
    print_section("Key insight")
    g_cost = results["greedy"]["cost"]
    best_alg = "held_karp" if results.get("held_karp", {}).get("cost") else "two_opt"
    best_cost = results[best_alg]["cost"]
    savings_pct = (g_cost - best_cost) / g_cost * 100

    print(f"  The optimized route saves {savings_pct:.1f}% distance over greedy.")
    print(f"  At scale (1000 drivers x 80 stops/day), that compounds into")
    print(f"  millions of dollars in fuel and hours of driver time per year.")
    print()
    print(f"  Open app/index.html in a browser to see the visual interactive demo.")
    print()


if __name__ == "__main__":
    main()
