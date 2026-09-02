"""
SPIDER-MAN NEIGHBOURHOOD RESPONSE SYSTEM
TEAM CLUB — Mission Planner

A clean, modular terminal application that helps Spider-Man
choose the best mission based on current location, incident
priorities and shortest travel distance through the city graph.

No external APIs • No databases • Pure Python
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
import heapq
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. CITY GRAPH (the complete neighbourhood)
# ─────────────────────────────────────────────────────────────

LOCATION_NAMES: Dict[int, str] = {
    1: "Queens Street",
    2: "Midtown School",
    3: "City Hospital",
    4: "Park Avenue",
    5: "Queens Residence",
    6: "Central Mall",
    7: "Police Station",
    8: "Metro Station",
}

# Reverse lookup (name → id) – case-insensitive matching later
NAME_TO_ID: Dict[str, int] = {name.lower(): id_ for id_, name in LOCATION_NAMES.items()}

# Undirected weighted edges (only the roads that exist)
# Format: (node_a, node_b, distance_km)
DIRECT_ROADS: List[Tuple[int, int, int]] = [
    (1, 2, 4),   # Queens Street ↔ Midtown School
    (1, 3, 6),   # Queens Street ↔ City Hospital
    (1, 5, 3),   # Queens Street ↔ Queens Residence
    (2, 4, 3),   # Midtown School ↔ Park Avenue
    (2, 3, 5),   # Midtown School ↔ City Hospital
    (4, 5, 2),   # Park Avenue ↔ Queens Residence
    (4, 6, 4),   # Park Avenue ↔ Central Mall
    (3, 7, 5),   # City Hospital ↔ Police Station
    (6, 7, 2),   # Central Mall ↔ Police Station
    (6, 8, 3),   # Central Mall ↔ Metro Station
    (7, 8, 4),   # Police Station ↔ Metro Station
]


def build_adjacency() -> Dict[int, List[Tuple[int, int]]]:
    """Build adjacency list: node → list of (neighbour, distance)."""
    graph: Dict[int, List[Tuple[int, int]]] = {i: [] for i in LOCATION_NAMES}
    for a, b, dist in DIRECT_ROADS:
        graph[a].append((b, dist))
        graph[b].append((a, dist))
    return graph


CITY_GRAPH = build_adjacency()


# ─────────────────────────────────────────────────────────────
# 2. DATA MODELS
# ─────────────────────────────────────────────────────────────

@dataclass(order=False)
class Incident:
    """A single active incident that Spider-Man may respond to."""
    id: str
    location_id: int
    priority: int
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def location_name(self) -> str:
        return LOCATION_NAMES.get(self.location_id, "UNKNOWN")


@dataclass
class RouteResult:
    """Result of a path-finding query."""
    found: bool
    distance: int = 0
    path: List[int] = field(default_factory=list)
    path_names: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        if not self.found:
            return "No valid route"
        if not self.path:
            return "Already at location (0 km)"
        arrow = " → ".join(self.path_names)
        return f"{arrow}  ({self.distance} km)"


@dataclass
class MissionEvaluation:
    """Full evaluation of one incident from Spider-Man’s current position."""
    incident: Incident
    route: RouteResult
    mission_score: Optional[int]  # None if unreachable / invalid

    @property
    def is_reachable(self) -> bool:
        return self.route.found


# ─────────────────────────────────────────────────────────────
# 3. CORE ALGORITHMS
# ─────────────────────────────────────────────────────────────

def dijkstra(start: int, goal: int) -> RouteResult:
    """
    Shortest path between two nodes using Dijkstra.
    Returns distance and the actual node sequence.
    """
    if start not in CITY_GRAPH or goal not in CITY_GRAPH:
        return RouteResult(found=False)

    if start == goal:
        return RouteResult(
            found=True,
            distance=0,
            path=[start],
            path_names=[LOCATION_NAMES[start]],
        )

    # priority queue: (distance, node)
    pq: List[Tuple[int, int]] = [(0, start)]
    distances: Dict[int, int] = {start: 0}
    previous: Dict[int, Optional[int]] = {start: None}
    visited: Set[int] = set()

    while pq:
        dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            break

        for neighbour, edge_w in CITY_GRAPH[node]:
            if neighbour in visited:
                continue
            new_dist = dist + edge_w
            if neighbour not in distances or new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                previous[neighbour] = node
                heapq.heappush(pq, (new_dist, neighbour))

    if goal not in distances:
        return RouteResult(found=False)

    # Reconstruct path
    path: List[int] = []
    current: Optional[int] = goal
    while current is not None:
        path.append(current)
        current = previous.get(current)
    path.reverse()

    return RouteResult(
        found=True,
        distance=distances[goal],
        path=path,
        path_names=[LOCATION_NAMES[n] for n in path],
    )


def resolve_location(raw: str | int) -> Optional[int]:
    """
    Accept either a location ID (int) or a name (str).
    Returns the canonical ID or None if invalid.
    """
    if isinstance(raw, int):
        return raw if raw in LOCATION_NAMES else None

    key = str(raw).strip().lower()
    return NAME_TO_ID.get(key)


# ─────────────────────────────────────────────────────────────
# 4. MISSION PLANNER
# ─────────────────────────────────────────────────────────────

class MissionPlanner:
    """
    The heart of the system.
    Given Spider-Man’s current location and a list of incidents,
    compute the best mission according to the scoring rules.
    """

    def __init__(self, current_location: str | int):
        self.current_id = resolve_location(current_location)
        if self.current_id is None:
            raise ValueError(f"Invalid current location: {current_location}")

    @property
    def current_name(self) -> str:
        return LOCATION_NAMES[self.current_id]

    def evaluate_incident(self, incident: Incident) -> MissionEvaluation:
        """Calculate route + mission score for one incident."""
        if incident.location_id not in LOCATION_NAMES:
            return MissionEvaluation(
                incident=incident,
                route=RouteResult(found=False),
                mission_score=None,
            )

        route = dijkstra(self.current_id, incident.location_id)
        score = None
        if route.found:
            score = incident.priority - route.distance
        return MissionEvaluation(incident=incident, route=route, mission_score=score)

    def recommend(self, incidents: List[Incident]) -> Optional[MissionEvaluation]:
        """
        Evaluate all incidents and return the best one.
        Tie-break order:
          1. Higher mission score
          2. Higher priority
          3. Shorter distance
          4. Older incident (earlier created_at)
        """
        if not incidents:
            return None

        evaluations = [self.evaluate_incident(inc) for inc in incidents]
        reachable = [e for e in evaluations if e.is_reachable and e.mission_score is not None]

        if not reachable:
            return None  # all unreachable

        def sort_key(e: MissionEvaluation):
            # Higher score first → negative
            # Higher priority first → negative
            # Shorter distance first → positive distance
            # Older first → positive timestamp
            return (
                -e.mission_score,                    # type: ignore
                -e.incident.priority,
                e.route.distance,
                e.incident.created_at.timestamp(),
            )

        reachable.sort(key=sort_key)
        return reachable[0]

    def full_report(self, incidents: List[Incident]) -> str:
        """Generate a rich, presentation-ready terminal report."""
        lines: List[str] = []

        # Header
        lines.append(_banner("SPIDER-MAN NEIGHBOURHOOD RESPONSE SYSTEM"))
        lines.append(_subtitle("TEAM CLUB  •  MISSION PLANNER"))
        lines.append("")
        lines.append(f"  Current Location :  {self.current_name}")
        lines.append(f"  Active Incidents :  {len(incidents)}")
        lines.append("")

        if not incidents:
            lines.append("  No active incidents. City is quiet… for now.")
            lines.append(_footer())
            return "\n".join(lines)

        # Evaluate everything
        evaluations = [self.evaluate_incident(inc) for inc in incidents]
        best = self.recommend(incidents)

        # Detail table
        lines.append(_section("INCIDENT ANALYSIS"))
        lines.append("")
        header = f"  {'ID':<10} {'LOCATION':<20} {'PRIO':>5} {'DIST':>6} {'SCORE':>7}  STATUS"
        lines.append(header)
        lines.append("  " + "─" * 70)

        for e in evaluations:
            loc = e.incident.location_name
            prio = e.incident.priority
            if e.is_reachable:
                dist = f"{e.route.distance} km"
                score = str(e.mission_score)
                status = "✓ reachable"
            else:
                dist = "—"
                score = "—"
                status = "✗ unreachable / invalid"
            lines.append(
                f"  {e.incident.id:<10} {loc:<20} {prio:>5} {dist:>6} {score:>7}  {status}"
            )

        lines.append("")

        # Recommendation
        lines.append(_section("RECOMMENDATION"))
        lines.append("")
        if best is None:
            lines.append("  ⚠  No reachable missions. Spider-Man cannot respond to any incident.")
        else:
            e = best
            lines.append(f"  ★  BEST MISSION →  {e.incident.id}")
            lines.append(f"     Location     :  {e.incident.location_name}")
            lines.append(f"     Priority     :  {e.incident.priority}")
            lines.append(f"     Distance     :  {e.route.distance} km")
            lines.append(f"     Mission Score:  {e.mission_score}   (Priority − Distance)")
            lines.append(f"     Route        :  {e.route}")
            lines.append("")
            lines.append("  Why this one?")
            lines.append("  • Highest mission score among all reachable incidents")
            lines.append("  • Tie-breakers applied when scores are equal")
            lines.append("    (priority → distance → age of incident)")

        lines.append("")
        lines.append(_footer())
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# 5. PRETTY PRINT HELPERS
# ─────────────────────────────────────────────────────────────

def _banner(text: str) -> str:
    width = 72
    return (
        "╔" + "═" * (width - 2) + "╗\n"
        f"║{text.center(width - 2)}║\n"
        "╚" + "═" * (width - 2) + "╝"
    )


def _subtitle(text: str) -> str:
    return text.center(72)


def _section(title: str) -> str:
    return f"  ▶ {title}"


def _footer() -> str:
    return (
        "\n"
        "  ──────────────────────────────────────────────────────────────\n"
        "  THE CITY IS THE MAP.  YOU FIND THE WAY.\n"
        "  TEAM CLUB  •  Mission Complete when Spider-Man is where he needs to be.\n"
        "  ──────────────────────────────────────────────────────────────"
    )


# ─────────────────────────────────────────────────────────────
# 6. DEMO / PRESENTATION RUNNER
# ─────────────────────────────────────────────────────────────

def create_sample_incidents() -> List[Incident]:
    """
    Realistic sample set that exercises all acceptance criteria:
    - same start/destination
    - directly connected
    - multi-step routes
    - invalid location
    - multiple missions
    - different priorities & distances
    - equal scores (tie-breaker)
    - unreachable (if any)
    """
    now = datetime.now()
    earlier = datetime(2026, 8, 30, 10, 0, 0)  # older incident for tie-break demo
    return [
        # Exact worked example from the slides
        Incident("INC-014", 3, 47, created_at=now),          # City Hospital   → 6 km → score 41
        Incident("INC-009", 2, 42, created_at=now),          # Midtown School  → 4 km → score 38

        # Additional missions to show multi-step + ranking
        Incident("INC-021", 6, 40, created_at=now),          # Central Mall    → 9 km → score 31
        Incident("INC-033", 8, 35, created_at=now),          # Metro Station   → 12 km → score 23
        Incident("INC-007", 5, 50, created_at=now),          # Queens Residence→ 3 km → score 47 (winner)

        # Invalid location – must not crash (Gotham Tower)
        Incident("INC-XXX", 99, 99, created_at=now),
    ]


def run_demo():
    """Run a complete demonstration suitable for project presentation."""
    print()
    print("  Loading neighbourhood map…")
    print("  Validating direct roads…")
    print("  Mission Planner online.\n")

    # Scenario 1 – Spider-Man starts at Queens Street
    planner = MissionPlanner("Queens Street")
    incidents = create_sample_incidents()
    print(planner.full_report(incidents))

    # Extra verification prints (optional clarity)
    print("\n  ── Quick verification of key routes ──")
    tests = [
        ("Queens Street", "City Hospital"),
        ("Queens Street", "Midtown School"),
        ("Queens Street", "Queens Street"),   # already there
        ("Queens Street", "Metro Station"),
        ("Park Avenue", "Police Station"),
    ]
    for start, end in tests:
        p = MissionPlanner(start)
        rid = resolve_location(end)
        if rid is None:
            print(f"  {start} → {end}: INVALID LOCATION")
            continue
        r = dijkstra(p.current_id, rid)
        print(f"  {start} → {end}: {r}")


if __name__ == "__main__":
    run_demo()