# ============================================
# SPIDER-MAN COMMAND CENTRE
# ============================================

incidents = []          # the list that holds everything
next_number = 1         # used to make IDs like INC-001

STATUSES = ["REPORTED", "IN_PROGRESS", "RESOLVED"]

DISTANCES = {
    "queens street": 3,
    "city hospital": 6,
    "brooklyn bridge": 9,
}


# ---------- ASKING QUESTIONS ----------

def ask_text(question):
    while True:
        answer = input(question).strip()
        if answer == "":
            print("This cannot be empty.")
        else:
            return answer


def ask_number(question, low, high):
    while True:
        answer = input(question).strip()
        if answer.isdigit() and low <= int(answer) <= high:
            return int(answer)
        print("Please enter a number between", low, "and", high)


# ---------- CALCULATIONS ----------

def get_priority(incident):
    return incident["severity"] * 10 + incident["people"]


def get_distance(location):
    return DISTANCES.get(location.lower(), 10)


def get_mission_score(incident):
    return get_priority(incident) - get_distance(incident["location"]) * 2


def get_active():
    return [i for i in incidents if i["status"] != "RESOLVED"]


def find_by_id(wanted_id):
    for incident in incidents:
        if incident["id"] == wanted_id.upper():
            return incident
    return None


# ---------- SHOWING THINGS ----------

def show_menu():
    print("\n=== SPIDER-MAN COMMAND CENTRE ===")
    print("1. Report Incident")
    print("2. View Active Incidents")
    print("3. View Response Priority")
    print("4. Get Next Mission")
    print("5. Update Incident")
    print("6. View Dashboard")
    print("7. Exit")


def show_incident_line(incident):
    print(incident["id"],
          "|", incident["type"],
          "|", incident["location"],
          "| severity", incident["severity"],
          "| people", incident["people"],
          "|", incident["status"])


# ---------- THE SEVEN JOBS ----------

def report_incident():
    global next_number

    print("\n--- REPORT INCIDENT ---")
    kind = ask_text("Type of incident: ")
    location = ask_text("Location: ")
    severity = ask_number("Severity (1-10): ", 1, 10)
    people = ask_number("People affected (0-1000): ", 0, 1000)
    description = ask_text("Description: ")

    new_id = "INC-" + str(next_number).zfill(3)
    next_number = next_number + 1

    incidents.append({
        "id": new_id,
        "type": kind,
        "location": location,
        "severity": severity,
        "people": people,
        "description": description,
        "status": "REPORTED",
    })

    print("Incident created. ID:", new_id)


def view_active():
    print("\n--- ACTIVE INCIDENTS ---")
    active = get_active()

    if len(active) == 0:
        print("No active incidents.")
        return

    for incident in active:
        show_incident_line(incident)


def view_priority():
    print("\n--- RESPONSE PRIORITY ---")
    active = get_active()

    if len(active) == 0:
        print("No active incidents.")
        return

    ordered = sorted(active, key=get_priority, reverse=True)

    for incident in ordered:
        print(incident["id"],
              "| severity", incident["severity"],
              "|", incident["location"],
              "| priority", get_priority(incident))


def next_mission():
    print("\n--- NEXT MISSION ---")
    active = get_active()

    if len(active) == 0:
        print("No available mission.")
        return

    best = max(active, key=get_mission_score)

    print("Incident :", best["id"])
    print("Location :", best["location"])
    print("Priority :", get_priority(best))
    print("Distance :", get_distance(best["location"]), "km")
    print("Score    :", get_mission_score(best))
    print("Route    : Base ->", best["location"])


def update_incident():
    print("\n--- UPDATE INCIDENT ---")

    if len(incidents) == 0:
        print("No incidents to update.")
        return

    wanted_id = ask_text("Enter incident ID: ")
    incident = find_by_id(wanted_id)

    if incident is None:
        print("No incident found with that ID.")
        return

    print("Current status:", incident["status"])
    print("Allowed:", ", ".join(STATUSES))

    new_status = ask_text("New status: ").upper()

    if new_status not in STATUSES:
        print("Invalid status. Not changed.")
        return

    old_status = incident["status"]
    incident["status"] = new_status
    print(incident["id"], "changed:", old_status, "->", new_status)


def view_dashboard():
    print("\n--- DASHBOARD ---")

    active = 0
    in_progress = 0
    resolved = 0
    critical = 0

    for incident in incidents:
        if incident["status"] == "RESOLVED":
            resolved = resolved + 1
        else:
            active = active + 1

        if incident["status"] == "IN_PROGRESS":
            in_progress = in_progress + 1

        if incident["severity"] >= 8 and incident["status"] != "RESOLVED":
            critical = critical + 1

    print("Total incidents :", len(incidents))
    print("Active          :", active)
    print("In progress     :", in_progress)
    print("Resolved        :", resolved)
    print("Critical active :", critical)


# ---------- THE MAIN LOOP ----------

def main():
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            report_incident()
        elif choice == "2":
            view_active()
        elif choice == "3":
            view_priority()
        elif choice == "4":
            next_mission()
        elif choice == "5":
            update_incident()
        elif choice == "6":
            view_dashboard()
        elif choice == "7":
            print("Shutting down. Stay safe.")
            break
        else:
            print("INVALID OPTION. Please choose 1 to 7.")


main()
