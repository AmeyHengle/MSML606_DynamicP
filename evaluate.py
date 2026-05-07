"""
evaluate.py
===========
Comprehensive evaluation of all routing algorithms across increasing
problem sizes, using the 100-stop College Park / DC metro dataset.

Algorithms evaluated
--------------------
  1. Random permutation    -- absolute baseline
  2. Greedy nearest neighbor
  3. 2-opt local search
  4. Or-opt (segment reinsertion)
  5. Held-Karp DP (exact, n <= 15 only)

Plots generated (saved to results/)
------------------------------------
  1. distance_vs_n.png         -- route distance vs number of stops (all algs)
  2. runtime_vs_n.png          -- runtime vs number of stops (log scale)
  3. approximation_ratio.png   -- heuristic quality vs exact DP (n <= 15)
  4. improvement_over_greedy.png -- % distance saved at fixed N values
  5. trial_variance.png        -- box plots showing consistency across trials

CSV output
----------
  results/eval_results.csv    -- raw numbers for all experiments

Usage
-----
    python evaluate.py                  # full evaluation (may take 2-3 min)
    python evaluate.py --fast           # fewer trials, fewer N values
    python evaluate.py --no-random      # skip random baseline (speeds up plots)

Author: Amey Hengle
Course: MSML606, Spring 2026
"""

import argparse
import csv
import json
import math
import os
import random
import time
from copy import deepcopy

import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from algorithms import (
    random_route,
    greedy_nearest_neighbor,
    two_opt,
    or_opt,
    held_karp,
    route_cost,
    build_distance_matrix,
)
from dataset import load_sample_route, stops_to_points, project_to_canvas

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "full_route.json")

# N values to evaluate (number of stops including depot)
N_VALUES_FULL = [5, 8, 10, 12, 15, 20, 30, 40, 50, 60, 75, 100]
N_VALUES_FAST = [5, 10, 15, 20, 30, 50]

# N values where Held-Karp DP is feasible (n^2 * 2^n must be tractable)
HK_LIMIT = 15

# Number of random subset trials per N value
K_TRIALS_FULL = 10
K_TRIALS_FAST = 5

# N values for box plots (trial variance analysis)
BOX_N_VALUES = [20, 50, 100]

# Visual style
ALGO_COLORS = {
    "random":     "#B4B2A9",
    "greedy":     "#E24B4A",
    "two_opt":    "#EF9F27",
    "or_opt":     "#378ADD",
    "held_karp":  "#3B6D11",
}
ALGO_LABELS = {
    "random":     "Random",
    "greedy":     "Greedy (nearest neighbor)",
    "two_opt":    "2-opt local search",
    "or_opt":     "Or-opt (segment reinsertion)",
    "held_karp":  "Held-Karp DP (exact)",
}
ALGO_ORDER = ["random", "greedy", "two_opt", "or_opt", "held_karp"]

matplotlib.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "figure.dpi": 150,
})


# ---------------------------------------------------------------------------
# Data loading and point conversion
# ---------------------------------------------------------------------------

def load_full_dataset():
    """Load the 100-stop dataset, regenerating if missing."""
    if not os.path.exists(DATA_PATH):
        print("full_route.json not found — regenerating...")
        import generate_dataset
        generate_dataset  # triggers __main__ via generate_dataset.py
    with open(DATA_PATH) as f:
        return json.load(f)["stops"]


def sample_subset(stops, n, seed=None):
    """
    Sample n stops from the full dataset (always including the depot at index 0).
    Returns the list of stops AND the Euclidean (x,y) points for algorithm input.

    We use lat/lng directly as (x, y) for Euclidean distance — valid at
    neighborhood scale where the earth is effectively flat.
    """
    if seed is not None:
        random.seed(seed)
    depot = stops[0]
    others = stops[1:]
    chosen = random.sample(others, min(n - 1, len(others)))
    subset = [depot] + chosen
    points = [(s["lat"], s["lng"]) for s in subset]
    return subset, points


# ---------------------------------------------------------------------------
# Core evaluation loop
# ---------------------------------------------------------------------------

def run_single(points, n, include_hk=True):
    """
    Run all algorithms on a single set of points. Returns a dict of results.
    """
    results = {}

    # Random baseline (single run is enough for comparison)
    t0 = time.perf_counter()
    r_route, r_cost = random_route(points, start=0)
    results["random"] = {"cost": r_cost, "time_ms": (time.perf_counter() - t0) * 1000}

    # Greedy
    t0 = time.perf_counter()
    g_route, g_cost = greedy_nearest_neighbor(points, start=0)
    results["greedy"] = {"cost": g_cost, "time_ms": (time.perf_counter() - t0) * 1000}

    # 2-opt (warm from greedy)
    t0 = time.perf_counter()
    o_route, o_cost = two_opt(points, initial_route=g_route)
    results["two_opt"] = {"cost": o_cost, "time_ms": (time.perf_counter() - t0) * 1000}

    # Or-opt (warm from 2-opt)
    t0 = time.perf_counter()
    oo_route, oo_cost = or_opt(points, initial_route=o_route)
    results["or_opt"] = {"cost": oo_cost, "time_ms": (time.perf_counter() - t0) * 1000}

    # Held-Karp (only for small n)
    if include_hk and n <= HK_LIMIT:
        t0 = time.perf_counter()
        hk_route, hk_cost = held_karp(points, start=0)
        results["held_karp"] = {"cost": hk_cost, "time_ms": (time.perf_counter() - t0) * 1000}
    else:
        results["held_karp"] = {"cost": None, "time_ms": None}

    return results


def run_evaluation(stops, n_values, k_trials):
    """
    Run K trials at each N value. Returns aggregated results dict and raw rows.

    Returns
    -------
    agg  : {n: {algo: {mean_cost, std_cost, mean_time, costs_list}}}
    rows : list of dicts for CSV export
    """
    agg = {}
    rows = []

    for n in n_values:
        print(f"  N = {n:3d}  ({k_trials} trials) ...", end="", flush=True)
        algo_costs = {a: [] for a in ALGO_ORDER}
        algo_times = {a: [] for a in ALGO_ORDER}

        for trial in range(k_trials):
            seed = n * 1000 + trial
            _, points = sample_subset(stops, n, seed=seed)
            res = run_single(points, n, include_hk=(n <= HK_LIMIT))

            for algo in ALGO_ORDER:
                c = res[algo].get("cost")
                t = res[algo].get("time_ms")
                if c is not None:
                    algo_costs[algo].append(c)
                if t is not None:
                    algo_times[algo].append(t)

            # Save raw row
            row = {"n": n, "trial": trial, "seed": seed}
            for algo in ALGO_ORDER:
                row[f"{algo}_cost"] = res[algo].get("cost", "")
                row[f"{algo}_time_ms"] = res[algo].get("time_ms", "")
            rows.append(row)

        # Aggregate
        agg[n] = {}
        for algo in ALGO_ORDER:
            costs = algo_costs[algo]
            times = algo_times[algo]
            agg[n][algo] = {
                "mean_cost": float(np.mean(costs)) if costs else None,
                "std_cost":  float(np.std(costs))  if costs else None,
                "mean_time": float(np.mean(times)) if times else None,
                "costs":     costs,
                "times":     times,
            }

        # Quick progress summary
        g_mean = agg[n]["greedy"]["mean_cost"]
        oo_mean = agg[n]["or_opt"]["mean_cost"]
        pct = (g_mean - oo_mean) / g_mean * 100 if g_mean else 0
        print(f"  greedy={g_mean:.4f}  or_opt={oo_mean:.4f}  ({pct:.1f}% saved)")

    return agg, rows


# ---------------------------------------------------------------------------
# Plot 1: Distance vs N
# ---------------------------------------------------------------------------

def plot_distance_vs_n(agg, n_values, output_path):
    """
    Main comparison plot: average route distance vs number of delivery stops.
    Shows how each algorithm's total distance grows with problem size.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for algo in ALGO_ORDER:
        ns, means, stds = [], [], []
        for n in n_values:
            m = agg[n][algo]["mean_cost"]
            s = agg[n][algo]["std_cost"]
            if m is not None:
                ns.append(n)
                means.append(m)
                stds.append(s if s else 0)

        if not ns:
            continue

        means_arr = np.array(means)
        stds_arr = np.array(stds)
        color = ALGO_COLORS[algo]
        lw = 2.5 if algo in ("or_opt", "held_karp") else 1.8
        ls = "--" if algo == "held_karp" else "-"

        ax.plot(ns, means_arr, color=color, linewidth=lw, linestyle=ls,
                label=ALGO_LABELS[algo], zorder=3)
        ax.fill_between(ns, means_arr - stds_arr, means_arr + stds_arr,
                        color=color, alpha=0.10, zorder=2)
        ax.scatter(ns, means_arr, color=color, s=28, zorder=4)

    ax.set_xlabel("Number of delivery stops (N)", fontsize=12)
    ax.set_ylabel("Average total route distance (degrees)", fontsize=12)
    ax.set_title("Route Distance vs Number of Delivery Stops\nAmazon Last-Mile Delivery, College Park / DC Metro",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    # Annotate the gap at max N
    max_n = max(n for n in n_values if agg[n]["greedy"]["mean_cost"] and agg[n]["or_opt"]["mean_cost"])
    g = agg[max_n]["greedy"]["mean_cost"]
    oo = agg[max_n]["or_opt"]["mean_cost"]
    pct = (g - oo) / g * 100
    ax.annotate(f"{pct:.0f}% gap\nat N={max_n}",
                xy=(max_n, (g + oo) / 2), xytext=(max_n - 20, (g + oo) / 2 * 1.05),
                arrowprops=dict(arrowstyle="-", color="#444"), fontsize=9, color="#444")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Plot 2: Runtime vs N
# ---------------------------------------------------------------------------

def plot_runtime_vs_n(agg, n_values, output_path):
    """
    Runtime comparison on a log scale. Shows which algorithms remain
    practical at large N and why Held-Karp is infeasible beyond ~15 stops.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for algo in ALGO_ORDER:
        ns, times = [], []
        for n in n_values:
            t = agg[n][algo]["mean_time"]
            if t is not None:
                ns.append(n)
                times.append(max(t, 0.001))  # floor to avoid log(0)

        if not ns:
            continue

        color = ALGO_COLORS[algo]
        lw = 2.5 if algo in ("or_opt", "held_karp") else 1.8
        ls = "--" if algo == "held_karp" else "-"
        ax.plot(ns, times, color=color, linewidth=lw, linestyle=ls,
                label=ALGO_LABELS[algo], marker="o", markersize=4, zorder=3)

    ax.set_yscale("log")
    ax.set_xlabel("Number of delivery stops (N)", fontsize=12)
    ax.set_ylabel("Average runtime (milliseconds, log scale)", fontsize=12)
    ax.set_title("Algorithm Runtime vs Problem Size\n(log scale — Held-Karp becomes infeasible rapidly beyond N=15)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)

    # Annotate HK limit
    ax.axvline(x=HK_LIMIT, color="#B4B2A9", linestyle=":", linewidth=1.5, zorder=1)
    ax.text(HK_LIMIT + 0.5, ax.get_ylim()[0] * 2, "Held-Karp\nlimit",
            fontsize=8, color="#888", va="bottom")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Plot 3: Approximation ratio vs exact Held-Karp (n ≤ 15 only)
# ---------------------------------------------------------------------------

def plot_approximation_ratio(agg, n_values, output_path):
    """
    For n values where Held-Karp gives the exact optimal cost, compute
    how close each heuristic gets (approximation ratio = heuristic / optimal).
    Ratio = 1.0 means the heuristic found the exact optimal route.
    """
    hk_ns = [n for n in n_values if agg[n]["held_karp"]["mean_cost"] is not None]
    if not hk_ns:
        print("  Skipping approximation_ratio.png — no Held-Karp data available")
        return

    fig, ax = plt.subplots(figsize=(9, 5))

    for algo in ["random", "greedy", "two_opt", "or_opt"]:
        ratios = []
        for n in hk_ns:
            hk = agg[n]["held_karp"]["mean_cost"]
            h  = agg[n][algo]["mean_cost"]
            if hk and h:
                ratios.append(h / hk)
            else:
                ratios.append(None)

        valid = [(n, r) for n, r in zip(hk_ns, ratios) if r is not None]
        if not valid:
            continue
        ns_v, rs_v = zip(*valid)
        color = ALGO_COLORS[algo]
        ax.plot(ns_v, rs_v, color=color, linewidth=2.2, marker="o", markersize=5,
                label=ALGO_LABELS[algo], zorder=3)

    ax.axhline(y=1.0, color=ALGO_COLORS["held_karp"], linewidth=1.5,
               linestyle="--", label="Held-Karp DP (exact optimal = 1.0)", zorder=2)

    ax.set_xlabel("Number of delivery stops (N)", fontsize=12)
    ax.set_ylabel("Approximation ratio (heuristic cost / optimal cost)", fontsize=12)
    ax.set_title("Approximation Quality vs Exact Optimal (Held-Karp DP)\nLower = closer to the true optimal route",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax.set_ylim(bottom=0.95)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Plot 4: % improvement over greedy at fixed N values
# ---------------------------------------------------------------------------

def plot_improvement_over_greedy(agg, n_values, output_path):
    """
    Bar chart showing how much each algorithm improves over greedy baseline
    at a selection of representative N values. Most readable for non-CS audiences.
    """
    # Pick 5 representative N values spread across the range
    target_ns = [n for n in [10, 20, 40, 75, 100] if n in agg]
    if not target_ns:
        target_ns = n_values[-5:]

    algos_to_show = ["two_opt", "or_opt", "held_karp"]
    bar_labels = [ALGO_LABELS[a].split("(")[0].strip() for a in algos_to_show]

    x = np.arange(len(target_ns))
    width = 0.25
    offsets = np.linspace(-(width * (len(algos_to_show) - 1)) / 2,
                           (width * (len(algos_to_show) - 1)) / 2,
                           len(algos_to_show))

    fig, ax = plt.subplots(figsize=(10, 5.5))

    for i, algo in enumerate(algos_to_show):
        pcts = []
        for n in target_ns:
            g = agg[n]["greedy"]["mean_cost"]
            h = agg[n][algo]["mean_cost"]
            if g and h:
                pcts.append((g - h) / g * 100)
            else:
                pcts.append(0)

        bars = ax.bar(x + offsets[i], pcts, width,
                      color=ALGO_COLORS[algo], label=bar_labels[i],
                      alpha=0.88, zorder=3, edgecolor="white", linewidth=0.5)

        for bar, pct in zip(bars, pcts):
            if pct > 0.5:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                        f"{pct:.1f}%", ha="center", va="bottom", fontsize=8.5,
                        color=ALGO_COLORS[algo], fontweight="bold")

    ax.set_xlabel("Number of delivery stops (N)", fontsize=12)
    ax.set_ylabel("% distance saved vs greedy baseline", fontsize=12)
    ax.set_title("Distance Savings Over Greedy Nearest Neighbor\nPositive = shorter route than greedy finds",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f"N={n}" for n in target_ns])
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_ylim(bottom=0)
    ax.axhline(y=0, color="#888", linewidth=0.7, zorder=1)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Plot 5: Trial variance box plots
# ---------------------------------------------------------------------------

def plot_trial_variance(agg, n_values, output_path):
    """
    Box plots showing the distribution of route distances across trials
    at three representative N values. Answers: is the algorithm consistently
    good, or does it sometimes get lucky?
    """
    box_ns = [n for n in BOX_N_VALUES if n in agg]
    if not box_ns:
        box_ns = [n_values[len(n_values) // 4], n_values[len(n_values) // 2], n_values[-1]]

    algos_to_show = [a for a in ["greedy", "two_opt", "or_opt"] if
                     agg[box_ns[0]][a]["costs"]]

    fig, axes = plt.subplots(1, len(box_ns), figsize=(4.5 * len(box_ns), 5.5), sharey=False)
    if len(box_ns) == 1:
        axes = [axes]

    for ax, n in zip(axes, box_ns):
        data = []
        labels = []
        colors = []
        for algo in algos_to_show:
            costs = agg[n][algo]["costs"]
            if costs:
                data.append(costs)
                labels.append(ALGO_LABELS[algo].split("(")[0].strip())
                colors.append(ALGO_COLORS[algo])

        bp = ax.boxplot(data, patch_artist=True, notch=False,
                        medianprops=dict(color="white", linewidth=2),
                        whiskerprops=dict(linewidth=1.2),
                        capprops=dict(linewidth=1.2),
                        flierprops=dict(marker="o", markersize=4, alpha=0.5))

        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)

        ax.set_title(f"N = {n} stops", fontsize=11, fontweight="bold")
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Total route distance" if ax == axes[0] else "", fontsize=10)
        ax.set_ylim(bottom=0)

    fig.suptitle("Route Distance Variability Across 10 Random Trials\n(narrower box = more consistent algorithm)",
                 fontsize=12, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Plot 6 (bonus): Route map comparison at N=20
# ---------------------------------------------------------------------------

def plot_route_map_comparison(stops, agg_raw_routes, n_demo, output_path):
    """
    Side-by-side geographic map showing the actual routes taken by each
    algorithm on the same set of 20 stops. Makes the efficiency difference
    visually obvious for a non-CS audience.
    """
    _, demo_points = sample_subset(stops, n_demo, seed=n_demo * 1000)
    demo_stops = [stops[0]] + random.sample(stops[1:], n_demo - 1)

    # Run algorithms on this demo set
    g_route, _ = greedy_nearest_neighbor(demo_points)
    o_route, _ = two_opt(demo_points, initial_route=g_route)
    oo_route, _ = or_opt(demo_points, initial_route=o_route)

    routes = {
        "Greedy":  (g_route,  ALGO_COLORS["greedy"]),
        "2-opt":   (o_route,  ALGO_COLORS["two_opt"]),
        "Or-opt":  (oo_route, ALGO_COLORS["or_opt"]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(13, 5))

    lats = [p[0] for p in demo_points]
    lngs = [p[1] for p in demo_points]
    lat_pad = (max(lats) - min(lats)) * 0.12 or 0.005
    lng_pad = (max(lngs) - min(lngs)) * 0.12 or 0.005

    def local_cost(pts, route):
        dm = build_distance_matrix(pts)
        n = len(route)
        return sum(dm[route[i]][route[(i+1)%n]] for i in range(n))

    for ax, (title, (route, color)) in zip(axes, routes.items()):
        # Draw route edges
        for i in range(len(route)):
            a = demo_points[route[i]]
            b = demo_points[route[(i + 1) % len(route)]]
            ax.annotate("", xy=(b[1], b[0]), xytext=(a[1], a[0]),
                        arrowprops=dict(arrowstyle="-|>", color=color,
                                        lw=1.4, mutation_scale=12))

        # Draw stops
        for i, p in enumerate(demo_points):
            is_depot = (i == 0)
            ax.scatter(p[1], p[0], s=80 if is_depot else 45,
                       color="#185FA5" if is_depot else color,
                       zorder=5, edgecolors="white", linewidths=0.8)
            ax.text(p[1], p[0] + lat_pad * 0.18,
                    "D" if is_depot else str(i),
                    ha="center", va="bottom", fontsize=7,
                    color="#185FA5" if is_depot else "#333")

        cost = local_cost(demo_points, route)
        g_cost = local_cost(demo_points, g_route)
        pct = (g_cost - cost) / g_cost * 100
        subtitle = f"distance: {cost:.4f}" + (f"\n({pct:.1f}% vs greedy)" if title != "Greedy" else "")

        ax.set_title(f"{title}\n{subtitle}", fontsize=10, fontweight="bold", color=color)
        ax.set_xlim(min(lngs) - lng_pad, max(lngs) + lng_pad)
        ax.set_ylim(min(lats) - lat_pad, max(lats) + lat_pad)
        ax.set_xlabel("Longitude", fontsize=8)
        ax.set_ylabel("Latitude", fontsize=8)
        ax.tick_params(labelsize=7)

    fig.suptitle(f"Actual Route Maps — {n_demo} Delivery Stops, College Park / DC Metro",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def save_csv(rows, n_values, agg, output_path):
    """Save raw trial data and aggregate statistics to CSV."""
    # Raw trials
    raw_path = output_path.replace(".csv", "_raw.csv")
    if rows:
        fieldnames = list(rows[0].keys())
        with open(raw_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  Saved: {raw_path}")

    # Aggregated summary
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["n"]
        for algo in ALGO_ORDER:
            header += [f"{algo}_mean_cost", f"{algo}_std_cost", f"{algo}_mean_time_ms"]
        writer.writerow(header)
        for n in n_values:
            row = [n]
            for algo in ALGO_ORDER:
                d = agg[n][algo]
                row += [
                    f"{d['mean_cost']:.6f}" if d["mean_cost"] else "",
                    f"{d['std_cost']:.6f}"  if d["std_cost"]  else "",
                    f"{d['mean_time']:.3f}" if d["mean_time"] else "",
                ]
            writer.writerow(row)
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Print summary table
# ---------------------------------------------------------------------------

def print_summary(agg, n_values):
    print()
    print("=" * 72)
    print("  EVALUATION SUMMARY")
    print("=" * 72)

    # Header
    print(f"\n  {'N':>4}  {'Random':>9}  {'Greedy':>9}  {'2-opt':>9}  {'Or-opt':>9}  {'HK DP':>9}  {'Best saves':>10}")
    print("  " + "-" * 68)

    for n in n_values:
        vals = []
        for algo in ALGO_ORDER:
            m = agg[n][algo]["mean_cost"]
            vals.append(f"{m:.4f}" if m else "  N/A  ")

        g = agg[n]["greedy"]["mean_cost"]
        oo = agg[n]["or_opt"]["mean_cost"]
        saves = f"{(g - oo) / g * 100:.1f}%" if g and oo else "—"
        print(f"  {n:>4}  {'  '.join(vals)}  {saves:>10}")

    print()
    # Key takeaway
    max_n = max(n for n in n_values if agg[n]["or_opt"]["mean_cost"])
    g = agg[max_n]["greedy"]["mean_cost"]
    oo = agg[max_n]["or_opt"]["mean_cost"]
    pct = (g - oo) / g * 100
    print(f"  At N={max_n}: Or-opt saves {pct:.1f}% over greedy.")
    print(f"  At Amazon scale (1M deliveries/day), that is roughly")
    print(f"  {pct:.0f}% fewer miles driven — millions in annual fuel savings.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Route optimizer evaluation")
    parser.add_argument("--fast", action="store_true", help="Fewer trials and N values")
    parser.add_argument("--no-random", action="store_true", help="Skip random baseline")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    n_values = N_VALUES_FAST if args.fast else N_VALUES_FULL
    k_trials = K_TRIALS_FAST if args.fast else K_TRIALS_FULL

    print()
    print("=" * 60)
    print("  MSML606 Route Optimizer — Evaluation Suite")
    print("=" * 60)
    print(f"\n  Mode     : {'fast' if args.fast else 'full'}")
    print(f"  N values : {n_values}")
    print(f"  Trials/N : {k_trials}")
    print(f"  Algorithms: Random, Greedy, 2-opt, Or-opt, Held-Karp")
    print(f"  HK limit : N ≤ {HK_LIMIT}")
    print()

    # Load dataset
    print("Loading dataset...")
    stops = load_full_dataset()
    print(f"  Loaded {len(stops)} stops (incl. depot) from full_route.json")
    print()

    # Run evaluation
    print("Running algorithms across all N values...")
    agg, rows = run_evaluation(stops, n_values, k_trials)

    # Print summary
    print_summary(agg, n_values)

    # Save CSV
    print("Saving results...")
    csv_path = os.path.join(RESULTS_DIR, "eval_results.csv")
    save_csv(rows, n_values, agg, csv_path)

    # Generate plots
    print("\nGenerating plots...")
    plot_distance_vs_n(agg, n_values,
                       os.path.join(RESULTS_DIR, "1_distance_vs_n.png"))
    plot_runtime_vs_n(agg, n_values,
                      os.path.join(RESULTS_DIR, "2_runtime_vs_n.png"))
    plot_approximation_ratio(agg, n_values,
                             os.path.join(RESULTS_DIR, "3_approximation_ratio.png"))
    plot_improvement_over_greedy(agg, n_values,
                                 os.path.join(RESULTS_DIR, "4_improvement_over_greedy.png"))
    plot_trial_variance(agg, n_values,
                        os.path.join(RESULTS_DIR, "5_trial_variance.png"))
    plot_route_map_comparison(stops, agg, n_demo=20,
                              output_path=os.path.join(RESULTS_DIR, "6_route_map_n20.png"))

    print()
    print(f"  All results saved to: {RESULTS_DIR}/")
    print(f"  Open results/ folder to view plots and CSV.")
    print()


if __name__ == "__main__":
    main()
