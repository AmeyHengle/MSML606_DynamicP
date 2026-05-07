"""
dataset.py
==========
Data loading and coordinate utilities for the delivery route optimizer.

Supports two modes:
  1. Load from the bundled sample_route.json (15 stops near College Park, MD)
  2. Load from the Amazon Last Mile Routing Research Challenge dataset
     (available on HuggingFace -- requires `datasets` library)

Lat/long coordinates are projected onto a 2D canvas using a simple
equirectangular projection, which is accurate enough for neighborhood-scale
distances (< 10 km).

Author: Amey Hengle
Course: MSML606, Spring 2026
"""

import json
import math
import os
import random


# ---------------------------------------------------------------------------
# Load bundled sample data
# ---------------------------------------------------------------------------

SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_route.json")


def load_sample_route():
    """
    Load the bundled 15-stop delivery route near College Park, MD.

    Returns
    -------
    stops : list of dicts, each with keys:
        id       : int, stop index (0 = depot)
        name     : str, human-readable label
        address  : str, street address
        lat      : float, latitude
        lng      : float, longitude
    """
    with open(SAMPLE_DATA_PATH, "r") as f:
        data = json.load(f)
    return data["stops"]


def stops_to_points(stops):
    """
    Convert a list of stop dicts to (lat, lng) tuples for algorithm input.

    Parameters
    ----------
    stops : list of dicts (from load_sample_route or load_amazon_route)

    Returns
    -------
    list of (lat, lng) tuples -- algorithms treat these as (x, y) directly.
    Note: because distances at neighborhood scale in degrees are proportional
    to real distances, raw lat/lng works as input to Euclidean algorithms.
    For display purposes, use project_to_canvas() instead.
    """
    return [(s["lat"], s["lng"]) for s in stops]


# ---------------------------------------------------------------------------
# Coordinate projection: lat/long -> canvas (x, y)
# ---------------------------------------------------------------------------

def project_to_canvas(stops, canvas_width=800, canvas_height=600, padding=60):
    """
    Project geographic coordinates onto a 2D canvas using an equirectangular
    (plate carrée) projection scaled to fit the canvas.

    Equirectangular projection:
      x = (lng - lng_min) / lng_range * canvas_width
      y = (lat_max - lat) / lat_range * canvas_height   (y flipped: north = up)

    Parameters
    ----------
    stops        : list of stop dicts with lat/lng fields
    canvas_width : int, target pixel width
    canvas_height: int, target pixel height
    padding      : int, margin in pixels on each side

    Returns
    -------
    projected : list of (x, y) pixel tuples, one per stop
    bounds    : dict with lat_min, lat_max, lng_min, lng_max (for reference)
    """
    lats = [s["lat"] for s in stops]
    lngs = [s["lng"] for s in stops]

    lat_min, lat_max = min(lats), max(lats)
    lng_min, lng_max = min(lngs), max(lngs)

    # Avoid division by zero if all points are identical
    lat_range = lat_max - lat_min if lat_max != lat_min else 1.0
    lng_range = lng_max - lng_min if lng_max != lng_min else 1.0

    # Available canvas area after padding
    w = canvas_width - 2 * padding
    h = canvas_height - 2 * padding

    # Maintain aspect ratio: scale uniformly so the map isn't distorted
    # Longitude spans are shorter in distance than latitude at higher latitudes
    lat_center = (lat_min + lat_max) / 2
    lng_scale = math.cos(math.radians(lat_center))  # correction factor

    scale_x = w / (lng_range * lng_scale) if lng_range > 0 else w
    scale_y = h / lat_range if lat_range > 0 else h
    scale = min(scale_x, scale_y)

    # Center the projected map within the canvas
    proj_w = lng_range * lng_scale * scale
    proj_h = lat_range * scale
    offset_x = padding + (w - proj_w) / 2
    offset_y = padding + (h - proj_h) / 2

    projected = []
    for s in stops:
        x = offset_x + (s["lng"] - lng_min) * lng_scale * scale
        y = offset_y + (lat_max - s["lat"]) * scale  # flip y: north = top
        projected.append((round(x, 2), round(y, 2)))

    bounds = {
        "lat_min": lat_min, "lat_max": lat_max,
        "lng_min": lng_min, "lng_max": lng_max,
    }

    return projected, bounds


# ---------------------------------------------------------------------------
# Load from HuggingFace Amazon Last Mile dataset (optional)
# ---------------------------------------------------------------------------

def load_amazon_route(route_index=0, max_stops=15):
    """
    Load a real delivery route from the Amazon Last Mile Routing Research
    Challenge dataset hosted on HuggingFace.

    Dataset: amazon-science/last-mile-routing-research-challenge
    URL: https://huggingface.co/datasets/amazon-science/last-mile-routing-research-challenge

    Requires: pip install datasets

    The dataset contains real Amazon delivery routes from 5 US cities.
    Each route has dozens of stops with lat/lng coordinates. We take the
    first `max_stops` stops from route at `route_index` and treat the
    first stop as the depot.

    Parameters
    ----------
    route_index : int, which route to load from the dataset
    max_stops   : int, cap on number of stops (keep <= 15 for Held-Karp)

    Returns
    -------
    stops : list of dicts with id, name, lat, lng fields
            (same format as load_sample_route)
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError(
            "The 'datasets' library is required to load from HuggingFace. "
            "Install it with: pip install datasets"
        )

    print("Loading Amazon Last Mile dataset from HuggingFace...")
    dataset = load_dataset(
        "amazon-science/last-mile-routing-research-challenge",
        trust_remote_code=True
    )

    # The dataset contains route sequences and stop coordinates
    # Extract stops from the requested route
    route_data = dataset["train"][route_index]
    raw_stops = route_data.get("stops", [])

    stops = []
    for i, stop in enumerate(raw_stops[:max_stops]):
        stops.append({
            "id": i,
            "name": "Depot" if i == 0 else f"Stop {i}",
            "address": stop.get("address", f"Stop {i}"),
            "lat": float(stop["lat"]),
            "lng": float(stop["lng"]),
        })

    return stops


# ---------------------------------------------------------------------------
# Random point generation (for testing and complexity simulation)
# ---------------------------------------------------------------------------

def generate_random_stops(n, lat_center=38.99, lng_center=-76.94,
                           spread=0.05, seed=None):
    """
    Generate n random delivery stops scattered around a geographic center.

    Used for the complexity simulation (testing algorithm performance
    across increasing numbers of stops without needing real data).

    Parameters
    ----------
    n          : int, number of stops (including depot at index 0)
    lat_center : float, center latitude
    lng_center : float, center longitude
    spread     : float, degrees of spread around the center
    seed       : int or None, random seed for reproducibility

    Returns
    -------
    stops : list of stop dicts
    """
    if seed is not None:
        random.seed(seed)

    stops = []
    for i in range(n):
        stops.append({
            "id": i,
            "name": "Depot" if i == 0 else f"Stop {i}",
            "address": f"Random address {i}",
            "lat": lat_center + (random.random() - 0.5) * spread,
            "lng": lng_center + (random.random() - 0.5) * spread,
        })

    return stops


# ---------------------------------------------------------------------------
# Haversine distance (for reporting real-world distances in km)
# ---------------------------------------------------------------------------

def haversine_km(lat1, lng1, lat2, lng2):
    """
    Compute the great-circle distance between two geographic points in km.

    Uses the Haversine formula, accurate for small and large distances.
    Used for human-readable distance reporting (not for algorithm input).

    Parameters
    ----------
    lat1, lng1 : float, first point coordinates in degrees
    lat2, lng2 : float, second point coordinates in degrees

    Returns
    -------
    float : distance in kilometers
    """
    R = 6371.0  # Earth's radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def total_route_distance_km(stops, route):
    """
    Compute the total real-world distance of a route in kilometers.

    Parameters
    ----------
    stops : list of stop dicts with lat/lng fields
    route : list of node indices

    Returns
    -------
    float : total route distance in km (round trip)
    """
    total = 0.0
    n = len(route)
    for i in range(n):
        a = stops[route[i]]
        b = stops[route[(i + 1) % n]]
        total += haversine_km(a["lat"], a["lng"], b["lat"], b["lng"])
    return total
