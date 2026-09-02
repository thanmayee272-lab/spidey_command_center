from datetime import datetime

# Valid data
types = ["Robbery", "Accident", "Fire", "Medical Emergency",
         "Missing Person", "Suspicious Activity"]

locations = ["Queens Street", "Midtown School", "City Hospital",
             "Park Avenue", "Queens Residence", "Central Mall",
             "Police Station", "Metro Station"]

severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Store all incidents
incidents = {}


# Incident object
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


# Get a valid value
def get_value(message, valid_list):
    while True:
        value = input(message).strip()

        for item in valid_list:
            if value.lower() == item.lower():
                return item

        print("Invalid input. Please try again.")


# Report incident
def report():
    print("\n--- REPORT INCIDENT ---")

    type = get_value("Incident type: ", types)
    location = get_value("Location: ", locations)
    severity = get_value("Severity: ", severities)

    # People affected
    while True:
        try:
            people = int(input("People affected: "))

            if people >= 0:
                break

            print("Enter 0 or a positive number.")

        except ValueError:
            print("Please enter a number.")

    # Description
    while True:
        description = input("Description: ").strip()

        if description != "":
            break

        print("Description cannot be empty.")

    # Check duplicate
    for old in incidents.values():
        if old.type.lower() == type.lower() and old.location.lower() == location.lower():

            print("\n⚠ POSSIBLE DUPLICATE")
            print("Existing ID:", old.id)

            answer = input("Continue anyway? (yes/no): ").strip().lower()

            if answer != "yes":
                print("Incident cancelled.")
                return

            break

    # Create ID
    id = "INC-" + str(len(incidents) + 1).zfill(3)

    # Create object
    incident = Incident(
        id, type, location, severity, people, description
    )

    # Store incident
    incidents[id] = incident

    print("\n✓ INCIDENT CREATED")
    print("ID:", incident.id)
    print("Status:", incident.status)
    print("Time:", incident.time)


# Find incident
def find_incident():
    id = input("\nEnter Incident ID: ").strip().upper()

    if id in incidents:
        x = incidents[id]

        print("\n--- INCIDENT DETAILS ---")
        print("ID:", x.id)
        print("Type:", x.type)
        print("Location:", x.location)
        print("Severity:", x.severity)
        print("People:", x.people)
        print("Description:", x.description)
        print("Time:", x.time)
        print("Status:", x.status)

    else:
        print("Incident not found.")


# Main menu
while True:

    print("\n==========================")
    print(" SPIDER-MAN INCIDENT SYSTEM")
    print("==========================")
    print("1. Report Incident")
    print("2. Find Incident")
    print("3. View All Incidents")
    print("4. Exit")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        report()

    elif choice == "2":
        find_incident()

    elif choice == "3":

        if len(incidents) == 0:
            print("No incidents found.")

        else:
            for x in incidents.values():
                print("\n----------------")
                print("ID:", x.id)
                print("Type:", x.type)
                print("Location:", x.location)
                print("Severity:", x.severity)
                print("People:", x.people)
                print("Description:", x.description)
                print("Status:", x.status)

    elif choice == "4":
        print("System closed.")
        break

    else:
        print("Invalid choice.")
        