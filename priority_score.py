from datetime import datetime

# ============================================
# SPIDER-MAN COMMAND CENTRE 
# ============================================

# --- CONSTANTS & DATA ---
TYPES = ["Robbery", "Accident", "Fire", "Medical Emergency", "Missing Person", "Suspicious Activity"]
LOCATIONS = ["Queens Street", "Midtown School", "City Hospital", "Park Avenue", "Queens Residence", "Central Mall", "Police Station", "Metro Station"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
STATUSES = ["REPORTED", "IN_PROGRESS", "RESOLVED"]

# Scoring Maps (From original Threat Assessment Rules)
SEVERITY_SCORES = {"LOW": 10, "MEDIUM": 20, "HIGH": 30, "CRITICAL": 40}
LOCATION_IMPORTANCE = {
    "Midtown School": 4, "City Hospital": 4,
    "Queens Residence": 3,
    "Central Mall": 2, "Police Station": 2, "Metro Station": 2,
    "Queens Street": 1, "Park Avenue": 1
}
# Distance Map (From Code 3)
DISTANCES = {
    "queens street": 3, "midtown school": 5, "city hospital": 6,
    "park avenue": 4, "queens residence": 2, "central mall": 7,
    "police station": 5, "metro station": 8
}

incidents = {}       # Stores Incident objects
next_number = 1      # ID counter

# --- INCIDENT CLASS ---
class Incident:
    def __init__(self, id, type, location, severity, people, description):
        self.id = id
        self.type = type
        self.location = location
        self.severity = severity
        self.people = people
        self.description = description
        self.time = datetime.now()
        self.status = "REPORTED"

# --- HELPER FUNCTIONS ---
def get_value(message, valid_list):
    while True:
        value = input(message).strip()
        for item in valid_list:
            if value.lower() == item.lower():
                return item
        print("Invalid input. Please try again.")

def ask_text(question):
    while True:
        answer = input(question).strip()
        if answer != "":
            return answer
        print("This cannot be empty.")

def ask_number(question, low, high):
    while True:
        answer = input(question).strip()
        if answer.isdigit() and low <= int(answer) <= high:
            return int(answer)
        print(f"Please enter a number between {low} and {high}.")

# --- CALCULATIONS ---
def get_priority_score(incident):
    """Calculates: SEVERITY + (PEOPLE * 2) + LOCATION IMPORTANCE"""
    sev_score = SEVERITY_SCORES.get(incident.severity, 10)
    ppl_score = incident.people * 2
    loc_score = LOCATION_IMPORTANCE.get(incident.location, 1)
    return sev_score + ppl_score + loc_score

def get_distance(location):
    return DISTANCES.get(location.lower(), 10)

def get_mission_score(incident):
    """Combines Code 2 logic: Priority Score minus Distance penalty"""
    return get_priority_score(incident) - get_distance(incident.location)

def get_active():
    return [inc for inc in incidents.values() if inc.status != "RESOLVED"]

def find_by_id(wanted_id):
    return incidents.get(wanted_id.upper())

# --- MENU ACTIONS ---
def report_incident():
    global next_number
    print("\n--- REPORT INCIDENT ---")
    
    type = get_value("Incident type: ", TYPES)
    location = get_value("Location: ", LOCATIONS)
    severity = get_value("Severity: ", SEVERITIES)
    people = ask_number("People affected (0-1000): ", 0, 1000)
    description = ask_text("Description: ")

    # Duplicate check (from Code 1)
    for old in incidents.values():
        if old.type.lower() == type.lower() and old.location.lower() == location.lower():
            print("\n⚠ POSSIBLE DUPLICATE")
            print("Existing ID:", old.id)
            answer = input("Continue anyway? (yes/no): ").strip().lower()
            if answer != "yes":
                print("Incident cancelled.")
                return
            break

    id = "INC-" + str(next_number).zfill(3)
    next_number += 1
    
    incident = Incident(id, type, location, severity, people, description)
    incidents[id] = incident

    print("\n✓ INCIDENT CREATED")
    print(f"ID: {incident.id} | Priority Score: {get_priority_score(incident)}")

def find_incident():
    print("\n--- FIND INCIDENT ---")
    wanted_id = ask_text("Enter Incident ID: ")
    x = find_by_id(wanted_id)
    
    if x:
        print("\n--- INCIDENT DETAILS ---")
        print(f"ID: {x.id}\nType: {x.type}\nLocation: {x.location}")
        print(f"Severity: {x.severity}\nPeople: {x.people}")
        print(f"Description: {x.description}\nTime: {x.time}\nStatus: {x.status}")
    else:
        print("Incident not found.")

def view_active():
    print("\n--- ACTIVE INCIDENTS ---")
    active = get_active()
    if not active:
        print("No active incidents.")
        return
    for x in active:
        print(f"{x.id} | {x.type} | {x.location} | Sev: {x.severity} | Ppl: {x.people} | {x.status}")

def view_priority():
    print("\n--- RESPONSE PRIORITY QUEUE ---")
    active = get_active()
    if not active:
        print("No active incidents.")
        return
    
    # Sort by: 1. Score (desc), 2. People (desc), 3. Time (asc - older first)
    active.sort(key=lambda x: x.time)
    active.sort(key=lambda x: (get_priority_score(x), x.people), reverse=True)
    
    for inc in active:
        print(f"{inc.id} | Score: {get_priority_score(inc)} | Sev: {inc.severity} | Ppl: {inc.people} | {inc.location}")

def next_mission():
    """From Code 2 & 3: Finds best mission based on Priority vs Distance"""
    print("\n--- NEXT MISSION ---")
    active = get_active()
    if not active:
        print("No available mission.")
        return
        
    best = max(active, key=get_mission_score)
    
    print("🕷️ SPIDER-MAN'S NEXT TARGET 🕷️")
    print(f"Incident : {best.id}")
    print(f"Location : {best.location}")
    print(f"Priority : {get_priority_score(best)}")
    print(f"Distance : {get_distance(best.location)} km")
    print(f"Score    : {get_mission_score(best)} (Priority - Distance)")
    print(f"Route    : Base -> {best.location}")

def update_incident():
    print("\n--- UPDATE INCIDENT ---")
    if not incidents:
        print("No incidents to update.")
        return
        
    wanted_id = ask_text("Enter incident ID: ")
    inc = find_by_id(wanted_id)
    
    if not inc:
        print("No incident found with that ID.")
        return
        
    print(f"Current status: {inc.status}")
    print(f"Allowed: {', '.join(STATUSES)}")
    
    new_status = ask_text("New status: ").upper()
    if new_status not in STATUSES:
        print("Invalid status. Not changed.")
        return
        
    old_status = inc.status
    inc.status = new_status
    print(f"{inc.id} changed: {old_status} -> {new_status}")

def view_dashboard():
    print("\n--- DASHBOARD ---")
    active = 0
    resolved = 0
    critical = 0
    
    for inc in incidents.values():
        if inc.status == "RESOLVED":
            resolved += 1
        else:
            active += 1
        if inc.severity == "CRITICAL" and inc.status != "RESOLVED":
            critical += 1
            
    print(f"Total incidents : {len(incidents)}")
    print(f"Active          : {active}")
    print(f"Resolved        : {resolved}")
    print(f"Critical active : {critical}")

# --- MAIN LOOP ---
def main():
    while True:
        print("\n==============================")
        print("  SPIDER-MAN COMMAND CENTRE")
        print("==============================")
        print("1. Report Incident")
        print("2. Find Incident by ID")
        print("3. View Active Incidents")
        print("4. View Response Priority")
        print("5. Get Next Mission")
        print("6. Update Incident Status")
        print("7. View Dashboard")
        print("8. Exit")
        
        choice = input("Choose an option (1-8): ").strip()
        
        if choice == "1": report_incident()
        elif choice == "2": find_incident()
        elif choice == "3": view_active()
        elif choice == "4": view_priority()
        elif choice == "5": next_mission()
        elif choice == "6": update_incident()
        elif choice == "7": view_dashboard()
        elif choice == "8":
            print("Shutting down. Stay safe, Spider-Man!")
            break
        else:
            print("INVALID OPTION. Please choose 1 to 8.")

if __name__ == "__main__":
    main()