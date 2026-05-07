"""
analyze.py
==========
Runs Greedy, 2-opt, and Held-Karp DP on all 15 real-world Amazon delivery
routes across 5 US cities and produces a full metrics report.

Outputs:
  - Console summary table
  - results.json  (machine-readable full results)
  - report.csv    (importable into Excel / Google Sheets)

Author: Amey Hengle | MSML606 Spring 2026
"""

import math
import json
import csv
import time
from algorithms import greedy_nearest_neighbor, two_opt, held_karp, route_cost, build_distance_matrix
from real_routes import ROUTES


# ── Haversine distance (km) ──────────────────────────────────────────────────
def haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def route_km(stops_with_depot, route):
    total = 0.0
    n = len(route)
    for i in range(n):
        a, b = stops_with_depot[route[i]], stops_with_depot[route[(i+1)%n]]
        total += haversine(a["lat"], a["lng"], b["lat"], b["lng"])
    return total

# ── Project lat/lng to flat 2D for algorithm input ──────────────────────────
def to_points(stops_with_depot):
    """
    Simple equirectangular projection: treat (lat, lng) as (y, x) scaled
    so that distances are proportional to real km distances.
    We multiply lng by cos(mean_lat) to account for meridian convergence.
    """
    lats = [s["lat"] for s in stops_with_depot]
    lngs = [s["lng"] for s in stops_with_depot]
    mean_lat = sum(lats) / len(lats)
    cos_lat = math.cos(math.radians(mean_lat))
    # Scale to make coordinates numerically similar to km (~111 km per degree)
    return [(s["lat"] * 111.0, s["lng"] * 111.0 * cos_lat) for s in stops_with_depot]


# ── Main analysis ────────────────────────────────────────────────────────────
def analyze_route(route_data):
    depot = route_data["depot"]
    stops = route_data["stops"]

    # Build full stop list: depot first, then delivery stops
    all_stops = [{"id": 0, "lat": depot["lat"], "lng": depot["lng"], "address": depot["name"]}]
    for s in stops:
        all_stops.append({"id": s["id"], "lat": s["lat"], "lng": s["lng"], "address": s["address"]})

    n = len(all_stops)
    pts = to_points(all_stops)

    results = {}

    # Greedy
    t0 = time.perf_counter()
    gr_route, _ = greedy_nearest_neighbor(pts, start=0)
    gr_time = (time.perf_counter() - t0) * 1000
    gr_km = route_km(all_stops, gr_route)

    # 2-opt
    t0 = time.perf_counter()
    op_route, _ = two_opt(pts, initial_route=gr_route)
    op_time = (time.perf_counter() - t0) * 1000
    op_km = route_km(all_stops, op_route)

    # Held-Karp (exact, n <= 20)
    hk_km, hk_time, hk_route = None, None, None
    if n <= 20:
        t0 = time.perf_counter()
        hk_route, _ = held_karp(pts, start=0)
        hk_time = (time.perf_counter() - t0) * 1000
        hk_km = route_km(all_stops, hk_route)

    return {
        "route_id":   route_data["route_id"],
        "city":       route_data["city"],
        "zone":       route_data["zone"],
        "n_stops":    n - 1,
        "n_nodes":    n,
        "greedy": {
            "route":   gr_route,
            "dist_km": round(gr_km, 3),
            "time_ms": round(gr_time, 3),
        },
        "two_opt": {
            "route":        op_route,
            "dist_km":      round(op_km, 3),
            "time_ms":      round(op_time, 3),
            "improvement_pct": round((gr_km - op_km) / gr_km * 100, 2),
            "dist_saved_km":   round(gr_km - op_km, 3),
        },
        "held_karp": {
            "route":        hk_route,
            "dist_km":      round(hk_km, 3) if hk_km else None,
            "time_ms":      round(hk_time, 3) if hk_time else None,
            "improvement_pct": round((gr_km - hk_km) / gr_km * 100, 2) if hk_km else None,
            "dist_saved_km":   round(gr_km - hk_km, 3) if hk_km else None,
        },
    }


def print_table(all_results):
    print()
    print("=" * 100)
    print(f"  {'Route':<6} {'City':<18} {'Zone':<20} {'N':>4}  {'Greedy':>9}  {'2-opt':>9}  {'HK':>9}  {'2-opt sav':>10}  {'HK sav':>8}")
    print("  " + "-" * 96)
    for r in all_results:
        hk_str   = f"{r['held_karp']['dist_km']:.2f} km" if r['held_karp']['dist_km'] else "—"
        hk_sav   = f"{r['held_karp']['improvement_pct']:.1f}%" if r['held_karp']['improvement_pct'] else "—"
        op_sav   = f"{r['two_opt']['improvement_pct']:.1f}%"
        print(f"  {r['route_id']:<6} {r['city']:<18} {r['zone']:<20} {r['n_stops']:>4}  "
              f"{r['greedy']['dist_km']:>7.2f} km  {r['two_opt']['dist_km']:>7.2f} km  "
              f"{hk_str:>9}  {op_sav:>10}  {hk_sav:>8}")
    print("=" * 100)

    # Aggregate stats
    op_imps  = [r["two_opt"]["improvement_pct"] for r in all_results]
    hk_imps  = [r["held_karp"]["improvement_pct"] for r in all_results if r["held_karp"]["improvement_pct"]]
    gr_kms   = [r["greedy"]["dist_km"] for r in all_results]
    op_kms   = [r["two_opt"]["dist_km"] for r in all_results]

    print()
    print("  AGGREGATE STATISTICS")
    print("  " + "-" * 60)
    print(f"  Routes analyzed                : {len(all_results)}")
    print(f"  Cities covered                 : {len(set(r['city'] for r in all_results))}")
    print(f"  Total stops (all routes)       : {sum(r['n_stops'] for r in all_results)}")
    print()
    print(f"  2-opt improvement — mean       : {sum(op_imps)/len(op_imps):.1f}%")
    print(f"  2-opt improvement — std dev    : {(sum((x - sum(op_imps)/len(op_imps))**2 for x in op_imps)/len(op_imps))**0.5:.1f}%")
    print(f"  2-opt improvement — range      : {min(op_imps):.1f}% to {max(op_imps):.1f}%")
    print()
    print(f"  Held-Karp improvement — mean   : {sum(hk_imps)/len(hk_imps):.1f}%")
    print(f"  Held-Karp improvement — range  : {min(hk_imps):.1f}% to {max(hk_imps):.1f}%")
    print()
    total_gr_km = sum(gr_kms)
    total_op_km = sum(op_kms)
    print(f"  Total greedy distance          : {total_gr_km:.1f} km")
    print(f"  Total optimized (2-opt)        : {total_op_km:.1f} km")
    print(f"  Total saved (2-opt)            : {total_gr_km - total_op_km:.1f} km ({(total_gr_km-total_op_km)/total_gr_km*100:.1f}%)")
    print()
    print(f"  At 1,000 drivers/day (scaled)  : ~{(total_gr_km-total_op_km)/len(all_results)*1000:.0f} km saved daily")
    print(f"  Fuel savings (0.35 L/km)       : ~{(total_gr_km-total_op_km)/len(all_results)*1000*0.35:.0f} L/day")
    print(f"  CO2 avoided (2.31 kg CO2/L)    : ~{(total_gr_km-total_op_km)/len(all_results)*1000*0.35*2.31:.0f} kg CO2/day")


def save_results(all_results):
    # JSON
    with open("results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # CSV for report
    with open("report.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Route ID", "City", "Zone", "Stops (N)",
            "Greedy (km)", "2-opt (km)", "Held-Karp (km)",
            "2-opt saving (%)", "2-opt saved (km)",
            "HK saving (%)", "HK saved (km)",
            "Greedy time (ms)", "2-opt time (ms)", "HK time (ms)"
        ])
        for r in all_results:
            w.writerow([
                r["route_id"], r["city"], r["zone"], r["n_stops"],
                r["greedy"]["dist_km"],
                r["two_opt"]["dist_km"],
                r["held_karp"]["dist_km"] or "",
                r["two_opt"]["improvement_pct"],
                r["two_opt"]["dist_saved_km"],
                r["held_karp"]["improvement_pct"] or "",
                r["held_karp"]["dist_saved_km"] or "",
                r["greedy"]["time_ms"],
                r["two_opt"]["time_ms"],
                r["held_karp"]["time_ms"] or "",
            ])

    print(f"\n  Saved: results.json, report.csv")


if __name__ == "__main__":
    print("\n  Running analysis on 15 Amazon delivery routes across 5 US cities...")
    print("  Algorithms: Greedy | 2-opt | Held-Karp DP\n")

    all_results = []
    for i, route in enumerate(ROUTES):
        print(f"  [{i+1:02d}/15] {route['route_id']} — {route['city']} ({route['zone']})  "
              f"({len(route['stops'])} stops)...", end=" ", flush=True)
        r = analyze_route(route)
        all_results.append(r)
        hk_note = f"HK: {r['held_karp']['dist_km']:.2f} km" if r['held_karp']['dist_km'] else "HK: skipped"
        print(f"Greedy: {r['greedy']['dist_km']:.2f} km | 2-opt: {r['two_opt']['dist_km']:.2f} km | {hk_note}")

    print_table(all_results)
    save_results(all_results)
