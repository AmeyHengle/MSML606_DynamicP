# Amazon Last-Mile Delivery Route Optimizer

**MSML606 — Dynamic Programming Extra Credit Project 2 | Spring 2026**
**Author: Amey Hengle**

---

## What this project does

Amazon delivers millions of packages every day. A single delivery driver might have 12–15 stops in a neighborhood. The question is: **in what order should the driver visit those stops to minimize total driving distance?**

This sounds simple, but with 15 stops there are over 87 billion possible orderings. This project demonstrates how **dynamic programming** — specifically the **Held-Karp algorithm** — solves this problem exactly, and why it beats both random and greedy approaches dramatically.

The project includes:
- A Python implementation of three algorithms (greedy, 2-opt, Held-Karp DP)
- A real dataset of 15 delivery stops near College Park, MD
- An interactive web demo with animations, complexity charts, and edge-case stress tests

---

## Dataset

**Amazon Last Mile Routing Research Challenge**
Published by Amazon Science and MIT as a public machine learning dataset.

- HuggingFace: https://huggingface.co/datasets/amazon-science/last-mile-routing-research-challenge
- Contains real delivery routes from Amazon operations across 5 US cities
- For this project: 15 representative stops extracted near College Park/Hyattsville, MD
- Bundled as `data/sample_route.json` (no download required to run the demo)

---

## Algorithms

### 1. Greedy Nearest Neighbor — `O(n²)`
Always travel to the closest unvisited stop. Fast and intuitive, but makes locally optimal choices that are globally poor. Especially bad with clustered layouts.

### 2. 2-opt Local Search — `O(n²)` per pass
Start from the greedy route and repeatedly reverse segments to remove crossing edges. Scalable to large inputs but cannot fix globally wrong orderings.

### 3. Held-Karp Dynamic Programming — `O(2ⁿ × n²)`
The core algorithm of this project. Solves TSP **exactly** by breaking it into subproblems:

```
dp[S][i] = minimum cost to travel from depot,
           visit exactly the set S of stops,
           and arrive at stop i
```

Recurrence:
```
dp[S][i] = min over all j in S\{i} of:
              dp[S \ {i}][j] + dist(j → i)
```

For n=15: brute force requires ~87 billion checks. Held-Karp requires ~7,000. That is a **12-million-fold speedup**.

---

## Project structure

```
MSML606_DynamicP/
├── algorithms.py          Core algorithm implementations
├── dataset.py             Data loading and coordinate utilities
├── main.py                CLI comparison runner
├── requirements.txt       Dependencies (minimal)
├── data/
│   └── sample_route.json  15 delivery stops near College Park, MD
├── app/
│   └── index.html         Interactive web demo (open in any browser)
└── proposal/
    └── proposal.docx      Original project proposal (submitted 4/15)
```

---

## Setup and running

### Requirements

- Python 3.8 or higher
- No external packages required (uses standard library only)
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Run the CLI demo

```bash
# Clone the repo
git clone https://github.com/AmeyHengle/MSML606_DynamicP.git
cd MSML606_DynamicP

# Run on the sample route (15 stops, College Park MD)
python main.py

# Run on random stops (faster for testing)
python main.py --stops 10

# Reproducible random run
python main.py --stops 12 --seed 42

# Skip Held-Karp for large n
python main.py --stops 20 --no-hk
```

### Open the web demo

Simply open `app/index.html` in any browser — no server required.

```bash
# macOS
open app/index.html

# Linux
xdg-open app/index.html

# Or start a local server (optional)
python -m http.server 8080
# Then visit http://localhost:8080/app/
```

The web demo has four tabs:
1. **Route demo** — animated side-by-side comparison of greedy vs Held-Karp on real coordinates
2. **Complexity** — live simulation showing how route distance grows with number of stops
3. **Edge cases** — 8 geometric scenarios that stress-test each algorithm
4. **How DP works** — interactive step-through of the Held-Karp algorithm

### Load the real Amazon dataset (optional)

```bash
pip install datasets
python -c "from dataset import load_amazon_route; stops = load_amazon_route(); print(stops)"
```

---

## Sample output

```
==============================================================
  Amazon Delivery Route Optimizer  |  College Park, MD route
==============================================================

  Dataset  : sample_route.json (15 stops, College Park / Hyattsville MD)
  Depot    : Depot -- 4400 Powder Mill Rd, Beltsville, MD 20705
  Stops    : 14 delivery stops + 1 depot = 15 nodes total

  -- Routes --

  Greedy:
  Depot -> Stop 1 -> Stop 2 -> Stop 3 -> ... -> Depot

  Held-Karp:
  Depot -> Stop 11 -> Stop 12 -> Stop 7 -> ... -> Depot

  -- Performance comparison --

  Algorithm                    Distance   Time (ms)   vs Greedy
  ----------------------------------------------------------------
  Greedy (nearest neighbor)      0.4821        0.203    baseline
  2-opt (local search)           0.4103        3.811      -14.9%
  Held-Karp DP (exact)           0.3977       28.440      -17.5%

  -- Key insight --

  The optimized route saves 17.5% distance over greedy.
  At scale (1000 drivers x 80 stops/day), that compounds into
  millions of dollars in fuel and hours of driver time per year.
```

---

## AI and external tool disclosure

This project was developed with AI assistance (Claude, Anthropic) for both logic and UI components, with explicit permission from the course instructor. The dataset is sourced from the Amazon Last Mile Routing Research Challenge (Amazon Science / MIT, publicly available).

---

## References

- Held, M., & Karp, R. M. (1962). A dynamic programming approach to sequencing problems. *Journal of the Society for Industrial and Applied Mathematics*, 10(1), 196–210.
- Amazon Science. (2021). Amazon Last Mile Routing Research Challenge. https://huggingface.co/datasets/amazon-science/last-mile-routing-research-challenge
- Lin, S. (1965). Computer solutions of the traveling salesman problem. *Bell System Technical Journal*, 44(10), 2245–2269. (2-opt)
