"""
SPIDER-MAN COMMAND CENTRE
Final Main File
Combines:
1. Incident reporting and validation
2. Duplicate incident checking
3. Incident search and viewing
4. Priority scoring
5. Response priority queue
6. City graph + Dijkstra shortest path
7. Next mission recommendation
8. Incident status updates
9. Dashboard
10. Mission route display

Pure Python - no external libraries required.
"""

from dataclasses import dataclass, field
from datetime import datetime
import heapq


# ============================================================
# 1. CONSTANTS AND DATA
# ============================================================

INCIDENT_TYPES = [
    "Robbery",
    "Accident",
    "Fire",
    "Medical Emergency",
    "Missing Person",
    "Suspicious Activity",
]

LOCATIONS = [
    "Queens Street",
    "Midtown School",
    "City Hospital",
    "Park Avenue",
    "Queens Residence",
    "Central Mall",
    "Police Station",
    "Metro Station",
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

STATUSES = ["REPORTED", "IN_PROGRESS", "RESOLVED"]

SEVERITY_SCORES = {
    "LOW": 10,
    "MEDIUM": 20,
    "HIGH": 30,
    "CRITICAL": 40,
}

LOCATION_IMPORTANCE = {
    "Midtown School": 4,
    "City Hospital": 4,
    "Queens Residence": 3,
    "Central Mall": 2,
    "Police Station": 2,
    "Metro Station": 2,
    "Queens Street": 1,
    "Park Avenue": 1,
}


# ============================================================
# 2. CITY GRAPH
# ============================================================

LOCATION_NAMES = {
    1: "Queens Street",
    2: "Midtown School",
    3: "City Hospital",
    4: "Park Avenue",
    5: "Queens Residence",
    6: "Central Mall",
    7: "Police Station",
    8: "Metro Station",
}

NAME_TO_ID = {
    name.lower(): location_id
    for location_id, name in LOCATION_NAMES.items()
}

# (start, end, distance in km)
DIRECT_ROADS = [
    (1, 2, 4),
    (1, 3, 6),
    (1, 5, 3),
    (2, 4, 3),
    (2, 3, 5),
    (4, 5, 2),
    (4, 6, 4),
    (3, 7, 5),
    (6, 7, 2),
    (6, 8, 3),
    (7, 8, 4),
]


def build_city_graph():
    """Create an adjacency list for the city."""
    graph = {location_id: [] for location_id in LOCATION_NAMES}

    for start, end, distance in DIRECT_ROADS:
        graph[start].append((end, distance))
        graph[end].append((start, distance))

    return graph


CITY_GRAPH = build_city_graph()


# ============================================================
# 3. DATA MODEL
# ============================================================

@dataclass
class Incident:
    id: str
    type: str
    location: str
    severity: str
    people: int
    description: str
    time: datetime = field(default_factory=datetime.now)
    status: str = "REPORTED"

    @property
    def location_id(self):
        return NAME_TO_ID.get(self.location.lower())


@dataclass
class RouteResult:
    found: bool
    distance: int = 0
    path: list = field(default_factory=list)
    path_names: list = field(default_factory=list)

    def __str__(self):
        if not self.found:
            return "No valid route"

        if not self.path:
            return "Already at location (0 km)"

        route = " -> ".join(self.path_names)
        return f"{route} ({self.distance} km)"


# ============================================================
# 4. GLOBAL INCIDENT STORAGE
# ============================================================

incidents = {}
next_number = 1


# ============================================================
# 5. INPUT VALIDATION
# ============================================================

def get_value(message, valid_list):
    """Get a value that must exist in a given list."""
    while True:
        value = input(message).strip()

        for item in valid_list:
            if value.lower() == item.lower():
                return item

        print("Invalid input. Please try again.")


def ask_text(question):
    """Get non-empty text."""
    while True:
        answer = input(question).strip()

        if answer:
            return answer

        print("This cannot be empty.")


def ask_number(question, low, high):
    """Get an integer inside a given range."""
    while True:
        answer = input(question).strip()

        try:
            number = int(answer)

            if low <= number <= high:
                return number

        except ValueError:
            pass

        print(f"Please enter a number between {low} and {high}.")


# ============================================================
# 6. INCIDENT FUNCTIONS
# ============================================================

def get_active_incidents():
    """Return all incidents that are not resolved."""
    return [
        incident
        for incident in incidents.values()
        if incident.status != "RESOLVED"
    ]


def find_by_id(wanted_id):
    """Find an incident using its ID."""
    return incidents.get(wanted_id.strip().upper())


def report_incident():
    """Create and store a new incident."""
    global next_number

    print("\n--- REPORT INCIDENT ---")

    incident_type = get_value(
        "Incident type: ",
        INCIDENT_TYPES
    )

    location = get_value(
        "Location: ",
        LOCATIONS
    )

    severity = get_value(
        "Severity (LOW/MEDIUM/HIGH/CRITICAL): ",
        SEVERITIES
    )

    people = ask_number(
        "People affected (0-1000): ",
        0,
        1000
    )

    description = ask_text("Description: ")

    # Duplicate check
    for old in incidents.values():
        if (
            old.type.lower() == incident_type.lower()
            and old.location.lower() == location.lower()
            and old.status != "RESOLVED"
        ):
            print("\nWARNING: POSSIBLE DUPLICATE")
            print("Existing ID:", old.id)

            answer = input(
                "Continue anyway? (yes/no): "
            ).strip().lower()

            if answer != "yes":
                print("Incident cancelled.")
                return

            break

    incident_id = "INC-" + str(next_number).zfill(3)
    next_number += 1

    incident = Incident(
        id=incident_id,
        type=incident_type,
        location=location,
        severity=severity,
        people=people,
        description=description,
    )

    incidents[incident_id] = incident

    print("\nINCIDENT CREATED")
    print("ID:", incident.id)
    print("Priority Score:", get_priority_score(incident))
    print("Status:", incident.status)
    print("Time:", incident.time)


def find_incident():
    """Search for one incident and display its details."""
    print("\n--- FIND INCIDENT ---")

    wanted_id = ask_text("Enter Incident ID: ")
    incident = find_by_id(wanted_id)

    if incident is None:
        print("Incident not found.")
        return

    print("\n--- INCIDENT DETAILS ---")
    print("ID:", incident.id)
    print("Type:", incident.type)
    print("Location:", incident.location)
    print("Severity:", incident.severity)
    print("People affected:", incident.people)
    print("Description:", incident.description)
    print("Time:", incident.time)
    print("Status:", incident.status)
    print("Priority Score:", get_priority_score(incident))


def view_all_incidents():
    """Display every stored incident."""
    print("\n--- ALL INCIDENTS ---")

    if not incidents:
        print("No incidents found.")
        return

    for incident in incidents.values():
        print("\n-----------------------------")
        print("ID:", incident.id)
        print("Type:", incident.type)
        print("Location:", incident.location)
        print("Severity:", incident.severity)
        print("People:", incident.people)
        print("Status:", incident.status)
        print("Priority:", get_priority_score(incident))


def view_active():
    """Display all active incidents."""
    print("\n--- ACTIVE INCIDENTS ---")

    active = get_active_incidents()

    if not active:
        print("No active incidents.")
        return

    for incident in active:
        print(
            f"{incident.id} | "
            f"{incident.type} | "
            f"{incident.location} | "
            f"Severity: {incident.severity} | "
            f"People: {incident.people} | "
            f"{incident.status}"
        )


# ============================================================
# 7. PRIORITY SCORE
# ============================================================

def get_priority_score(incident):
    """
    Priority Score =
        Severity Score
        + (People Affected x 2)
        + Location Importance
    """

    severity_score = SEVERITY_SCORES.get(
        incident.severity,
        10
    )

    people_score = incident.people * 2

    location_score = LOCATION_IMPORTANCE.get(
        incident.location,
        1
    )

    return severity_score + people_score + location_score


def view_priority():
    """Display active incidents in priority order."""
    print("\n--- RESPONSE PRIORITY QUEUE ---")

    active = get_active_incidents()

    if not active:
        print("No active incidents.")
        return

    # Highest priority first.
    # If priorities are equal, more affected people first.
    # If still equal, older incident first.
    active.sort(
        key=lambda incident: (
            get_priority_score(incident),
            incident.people,
            -incident.time.timestamp(),
        ),
        reverse=True,
    )

    for incident in active:
        print(
            f"{incident.id} | "
            f"Priority: {get_priority_score(incident)} | "
            f"Severity: {incident.severity} | "
            f"People: {incident.people} | "
            f"{incident.location}"
        )


# ============================================================
# 8. DISTANCE / DIJKSTRA
# ============================================================

def resolve_location(location):
    """Convert a location name or ID into a valid node ID."""
    if isinstance(location, int):
        if location in LOCATION_NAMES:
            return location
        return None

    return NAME_TO_ID.get(
        str(location).strip().lower()
    )


def dijkstra(start, goal):
    """
    Find the shortest route using Dijkstra's algorithm.
    Returns both distance and actual route.
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

    priority_queue = [(0, start)]
    distances = {start: 0}
    previous = {start: None}
    visited = set()

    while priority_queue:
        current_distance, current_node = heapq.heappop(
            priority_queue
        )

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == goal:
            break

        for neighbour, road_distance in CITY_GRAPH[current_node]:
            if neighbour in visited:
                continue

            new_distance = (
                current_distance + road_distance
            )

            if (
                neighbour not in distances
                or new_distance < distances[neighbour]
            ):
                distances[neighbour] = new_distance
                previous[neighbour] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour),
                )

    if goal not in distances:
        return RouteResult(found=False)

    # Reconstruct path
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = previous.get(current)

    path.reverse()

    return RouteResult(
        found=True,
        distance=distances[goal],
        path=path,
        path_names=[
            LOCATION_NAMES[node]
            for node in path
        ],
    )


def choose_current_location():
    """Ask Spider-Man for his current location."""
    return get_value(
        "Spider-Man's current location: ",
        LOCATIONS
    )


# ============================================================
# 9. MISSION PLANNER
# ============================================================

def get_mission_score(incident, distance):
    """
    Mission Score =
        Priority Score - Shortest Distance
    """
    return get_priority_score(incident) - distance


def evaluate_mission(incident, current_location):
    """Calculate route and mission score for one incident."""

    start_id = resolve_location(current_location)
    goal_id = resolve_location(incident.location)

    if start_id is None or goal_id is None:
        return None, None

    route = dijkstra(start_id, goal_id)

    if not route.found:
        return route, None

    score = get_mission_score(
        incident,
        route.distance
    )

    return route, score


def get_best_mission(current_location):
    """
    Find the best reachable active incident.

    Selection:
    1. Highest mission score
    2. Higher priority
    3. Shorter distance
    4. Older incident
    """

    active = get_active_incidents()

    if not active:
        return None

    evaluations = []

    for incident in active:
        route, score = evaluate_mission(
            incident,
            current_location
        )

        if route is not None and route.found:
            evaluations.append(
                (incident, route, score)
            )

    if not evaluations:
        return None

    evaluations.sort(
        key=lambda item: (
            item[2],                          # score
            get_priority_score(item[0]),      # priority
            -item[1].distance,                # shorter distance
            -item[0].time.timestamp(),        # older first
        ),
        reverse=True,
    )

    return evaluations[0]


def next_mission():
    """Display Spider-Man's recommended next mission."""

    print("\n--- NEXT MISSION ---")

    active = get_active_incidents()

    if not active:
        print("No available mission.")
        return

    current_location = choose_current_location()

    result = get_best_mission(current_location)

    if result is None:
        print("No reachable missions.")
        return

    best, route, score = result

    print("\nSPIDER-MAN'S NEXT TARGET")
    print("-----------------------------")
    print("Incident :", best.id)
    print("Type     :", best.type)
    print("Location :", best.location)
    print("Severity :", best.severity)
    print("People   :", best.people)
    print("Priority :", get_priority_score(best))
    print("Distance :", route.distance, "km")
    print("Score    :", score)
    print("Route    :", route)


def view_mission_analysis():
    """Show route and mission score for every active incident."""

    print("\n--- MISSION ANALYSIS ---")

    active = get_active_incidents()

    if not active:
        print("No active incidents.")
        return

    current_location = choose_current_location()

    print("\nCurrent location:", current_location)
    print("---------------------------------------------")

    evaluations = []

    for incident in active:
        route, score = evaluate_mission(
            incident,
            current_location
        )

        if route is None or not route.found:
            print(
                f"{incident.id} | "
                f"{incident.location} | "
                f"UNREACHABLE"
            )
            continue

        evaluations.append(
            (incident, route, score)
        )

    evaluations.sort(
        key=lambda item: item[2],
        reverse=True
    )

    for incident, route, score in evaluations:
        print(
            f"{incident.id} | "
            f"Priority: {get_priority_score(incident)} | "
            f"Distance: {route.distance} km | "
            f"Mission Score: {score}"
        )


# ============================================================
# 10. UPDATE INCIDENT
# ============================================================

def update_incident():
    """Update the status of an incident."""

    print("\n--- UPDATE INCIDENT ---")

    if not incidents:
        print("No incidents to update.")
        return

    wanted_id = ask_text("Enter Incident ID: ")
    incident = find_by_id(wanted_id)

    if incident is None:
        print("No incident found with that ID.")
        return

    print("Current status:", incident.status)
    print("Allowed statuses:", ", ".join(STATUSES))

    new_status = ask_text(
        "New status: "
    ).upper()

    if new_status not in STATUSES:
        print("Invalid status. Not changed.")
        return

    old_status = incident.status
    incident.status = new_status

    print(
        f"{incident.id} changed: "
        f"{old_status} -> {new_status}"
    )


# ============================================================
# 11. DASHBOARD
# ============================================================

def view_dashboard():
    """Display overall system statistics."""

    print("\n--- DASHBOARD ---")

    total = len(incidents)
    active = 0
    in_progress = 0
    resolved = 0
    critical = 0

    for incident in incidents.values():

        if incident.status == "RESOLVED":
            resolved += 1
        else:
            active += 1

        if incident.status == "IN_PROGRESS":
            in_progress += 1

        if (
            incident.severity == "CRITICAL"
            and incident.status != "RESOLVED"
        ):
            critical += 1

    print("Total incidents :", total)
    print("Active          :", active)
    print("In progress     :", in_progress)
    print("Resolved        :", resolved)
    print("Critical active :", critical)


# ============================================================
# 12. CITY MAP / ROUTE TEST
# ============================================================

def view_city_map():
    """Display all city locations and direct roads."""

    print("\n--- CITY MAP ---")

    print("\nLocations:")
    for location_id, name in LOCATION_NAMES.items():
        print(f"{location_id}. {name}")

    print("\nDirect Roads:")
    for start, end, distance in DIRECT_ROADS:
        print(
            f"{LOCATION_NAMES[start]} <-> "
            f"{LOCATION_NAMES[end]} : "
            f"{distance} km"
        )


def find_route():
    """Find the shortest route between two locations."""

    print("\n--- FIND SHORTEST ROUTE ---")

    start = choose_current_location()

    destination = get_value(
        "Destination: ",
        LOCATIONS
    )

    start_id = resolve_location(start)
    destination_id = resolve_location(destination)

    route = dijkstra(
        start_id,
        destination_id
    )

    print("\nRoute Result:")
    print(route)


# ============================================================
# 13. SAMPLE DATA FOR DEMONSTRATION
# ============================================================

def load_demo_data():
    """
    Add sample incidents so the project can be demonstrated
    immediately.
    """

    global next_number

    if incidents:
        print("Demo data was not loaded because incidents already exist.")
        return

    sample_data = [
        (
            "INC-001",
            "Fire",
            "City Hospital",
            "CRITICAL",
            20,
            "Fire reported near the hospital.",
        ),
        (
            "INC-002",
            "Accident",
            "Midtown School",
            "HIGH",
            10,
            "Vehicle accident near school.",
        ),
        (
            "INC-003",
            "Robbery",
            "Central Mall",
            "MEDIUM",
            5,
            "Robbery reported at the mall.",
        ),
        (
            "INC-004",
            "Missing Person",
            "Queens Residence",
            "HIGH",
            2,
            "Missing person reported.",
        ),
    ]

    for data in sample_data:
        incident = Incident(*data)
        incidents[incident.id] = incident

    next_number = 5

    print("Demo incidents loaded successfully.")


# ============================================================
# 14. MAIN MENU
# ============================================================

def show_menu():
    print("\n")
    print("==============================================")
    print("       SPIDER-MAN COMMAND CENTRE")
    print("   NEIGHBOURHOOD RESPONSE SYSTEM")
    print("==============================================")
    print("1.  Report Incident")
    print("2.  Find Incident by ID")
    print("3.  View All Incidents")
    print("4.  View Active Incidents")
    print("5.  View Response Priority")
    print("6.  Get Next Mission")
    print("7.  View Mission Analysis")
    print("8.  Update Incident Status")
    print("9.  View Dashboard")
    print("10. View City Map")
    print("11. Find Shortest Route")
    print("12. Load Demo Data")
    print("13. Exit")
    print("==============================================")


def main():
    """Main program loop."""

    while True:
        show_menu()

        choice = input(
            "Choose an option (1-13): "
        ).strip()

        if choice == "1":
            report_incident()

        elif choice == "2":
            find_incident()

        elif choice == "3":
            view_all_incidents()

        elif choice == "4":
            view_active()

        elif choice == "5":
            view_priority()

        elif choice == "6":
            next_mission()

        elif choice == "7":
            view_mission_analysis()

        elif choice == "8":
            update_incident()

        elif choice == "9":
            view_dashboard()

        elif choice == "10":
            view_city_map()

        elif choice == "11":
            find_route()

        elif choice == "12":
            load_demo_data()

        elif choice == "13":
            print("\nShutting down. Stay safe, Spider-Man!")
            break

        else:
            print(
                "\nINVALID OPTION. "
                "Please choose a number from 1 to 13."
            )


# ============================================================
# 15. PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()
