"""
generate_dataset.py
===================
Generates a realistic 100-stop delivery dataset spread across 8 neighborhood
clusters in the College Park / Hyattsville / DC metro area.

Each cluster represents a real delivery zone. Stop coordinates are sampled
with Gaussian noise around real neighborhood centroids, giving geographically
authentic spatial structure (clusters far apart, stops dense within clusters).

This structure deliberately creates hard cases for greedy routing: a greedy
driver exhausts one cluster, then must make an expensive cross-cluster leap.

Run this once to regenerate data/full_route.json:
    python generate_dataset.py

Author: Amey Hengle
Course: MSML606, Spring 2026
"""

import json
import random
import math
import os

# Reproducible generation
random.seed(2026)


# ---------------------------------------------------------------------------
# Neighborhood cluster definitions
# Real centroids of delivery-dense areas in the DC/MD metro region
# ---------------------------------------------------------------------------

CLUSTERS = [
    {
        "name": "Beltsville / Laurel",
        "lat":  39.0350,
        "lng": -76.9150,
        "spread_lat": 0.018,
        "spread_lng": 0.022,
        "n_stops": 13,
    },
    {
        "name": "College Park",
        "lat":  38.9890,
        "lng": -76.9390,
        "spread_lat": 0.012,
        "spread_lng": 0.015,
        "n_stops": 12,
    },
    {
        "name": "Greenbelt",
        "lat":  39.0060,
        "lng": -76.8980,
        "spread_lat": 0.012,
        "spread_lng": 0.014,
        "n_stops": 12,
    },
    {
        "name": "Hyattsville",
        "lat":  38.9560,
        "lng": -76.9560,
        "spread_lat": 0.013,
        "spread_lng": 0.016,
        "n_stops": 13,
    },
    {
        "name": "Lanham / Seabrook",
        "lat":  38.9700,
        "lng": -76.8680,
        "spread_lat": 0.014,
        "spread_lng": 0.017,
        "n_stops": 12,
    },
    {
        "name": "Landover / Cheverly",
        "lat":  38.9270,
        "lng": -76.9060,
        "spread_lat": 0.013,
        "spread_lng": 0.015,
        "n_stops": 12,
    },
    {
        "name": "Riverdale / Bladensburg",
        "lat":  38.9570,
        "lng": -76.9280,
        "spread_lat": 0.011,
        "spread_lng": 0.013,
        "n_stops": 13,
    },
    {
        "name": "Capitol Heights / Seat Pleasant",
        "lat":  38.8910,
        "lng": -76.9100,
        "spread_lat": 0.014,
        "spread_lng": 0.016,
        "n_stops": 12,
    },
]

DEPOT = {
    "id": 0,
    "name": "Depot",
    "address": "Amazon DSP Station — 4400 Powder Mill Rd, Beltsville, MD 20705",
    "lat": 39.0197,
    "lng": -76.9228,
    "cluster": "Depot",
    "type": "depot",
}

STREET_TYPES = ["Ave", "Blvd", "Rd", "Dr", "St", "Ct", "Pkwy", "Ln", "Way", "Pl"]
STREET_NAMES = [
    "Maple", "Oak", "Cedar", "Pine", "Elm", "Washington", "Lincoln",
    "Jefferson", "Madison", "Adams", "Maryland", "Virginia", "Columbia",
    "University", "College", "Greenbelt", "Kenilworth", "Annapolis",
    "Baltimore", "Adelphi", "Powder Mill", "Edmonston", "Decatur",
    "Riggs", "Hamilton", "Sheridan", "Buchanan", "Merrimac", "Varnum",
]

CITY_FOR_CLUSTER = {
    "Beltsville / Laurel": ("Beltsville", "MD", "20705"),
    "College Park": ("College Park", "MD", "20742"),
    "Greenbelt": ("Greenbelt", "MD", "20770"),
    "Hyattsville": ("Hyattsville", "MD", "20782"),
    "Lanham / Seabrook": ("Lanham", "MD", "20706"),
    "Landover / Cheverly": ("Landover", "MD", "20785"),
    "Riverdale / Bladensburg": ("Riverdale", "MD", "20737"),
    "Capitol Heights / Seat Pleasant": ("Capitol Heights", "MD", "20743"),
}


def gauss_clamp(center, spread, lo, hi):
    """Sample from a Gaussian, clamped to [lo, hi]."""
    return max(lo, min(hi, random.gauss(center, spread)))


def generate_address(cluster_name):
    """Generate a plausible street address string."""
    number = random.randint(100, 9999)
    street = random.choice(STREET_NAMES)
    stype = random.choice(STREET_TYPES)
    city, state, zipcode = CITY_FOR_CLUSTER.get(cluster_name, ("College Park", "MD", "20742"))
    return f"{number} {street} {stype}, {city}, {state} {zipcode}"


def generate_stops():
    """
    Generate all delivery stops by sampling within each cluster's bounding box.
    Returns a list of stop dicts, with the depot at index 0.
    """
    stops = [DEPOT]
    stop_id = 1

    for cluster in CLUSTERS:
        lat_c = cluster["lat"]
        lng_c = cluster["lng"]
        slat = cluster["spread_lat"]
        slng = cluster["spread_lng"]

        for _ in range(cluster["n_stops"]):
            lat = gauss_clamp(lat_c, slat * 0.5, lat_c - slat, lat_c + slat)
            lng = gauss_clamp(lng_c, slng * 0.5, lng_c - slng, lng_c + slng)

            stops.append({
                "id": stop_id,
                "name": f"Stop {stop_id}",
                "address": generate_address(cluster["name"]),
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "cluster": cluster["name"],
                "type": "residential" if random.random() < 0.75 else "commercial",
            })
            stop_id += 1

    return stops


def haversine_km(lat1, lng1, lat2, lng2):
    """Haversine great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def dataset_summary(stops):
    """Print a summary of the generated dataset."""
    print(f"\nDataset summary")
    print(f"  Total stops  : {len(stops)} (including depot)")
    print(f"  Depot        : {stops[0]['address']}")
    print()
    for cluster in CLUSTERS:
        cluster_stops = [s for s in stops if s.get("cluster") == cluster["name"]]
        print(f"  {cluster['name']:<40} {len(cluster_stops):2d} stops")

    # Bounding box
    lats = [s["lat"] for s in stops]
    lngs = [s["lng"] for s in stops]
    lat_span = (max(lats) - min(lats)) * 111  # 1 deg lat ≈ 111 km
    lng_span = (max(lngs) - min(lngs)) * 111 * math.cos(math.radians(sum(lats) / len(lats)))
    print(f"\n  Geographic span: {lat_span:.1f} km N-S × {lng_span:.1f} km E-W")

    # Furthest stop from depot
    depot = stops[0]
    furthest = max(stops[1:], key=lambda s: haversine_km(depot["lat"], depot["lng"], s["lat"], s["lng"]))
    d = haversine_km(depot["lat"], depot["lng"], furthest["lat"], furthest["lng"])
    print(f"  Furthest stop: {furthest['name']} ({furthest['cluster']}) — {d:.2f} km from depot")


if __name__ == "__main__":
    stops = generate_stops()

    output_path = os.path.join(os.path.dirname(__file__), "data", "full_route.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = {
        "metadata": {
            "description": "100-stop Amazon last-mile delivery dataset, DC/MD metro area",
            "source": "Adapted from Amazon Last Mile Routing Research Challenge spatial structure",
            "dataset_url": "https://huggingface.co/datasets/amazon-science/last-mile-routing-research-challenge",
            "region": "College Park / Hyattsville / DC metro, MD",
            "depot": "Amazon DSP Station, Beltsville, MD",
            "num_stops": len(stops),
            "clusters": [c["name"] for c in CLUSTERS],
            "seed": 2026,
        },
        "stops": stops,
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    dataset_summary(stops)
    print(f"\n  Saved to: {output_path}")
