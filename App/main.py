# Christopher Griswold - 001164982
# Note: Unless otherwise stated, all methods are understood to require constant O(1) time and auxiliary space.
import structures
import dataloader
import local


# Orchestrates the entire truck loading and delivery operation. Simulate the passage of time by continuously
# checking to see if the time that both trucks have been in service is less than the simulated current time,
# as specified by the user. As soon as the the simulated current time is reached all truck loading and
# delivery operations cease and a full report is made available.
# Time complexity: O(n). Auxiliary space complexity: O(n).
def simulate_to_curr_time(packages, locations):
    packages.sort_keys("deadline")
    truck_one = structures.Truck(1, locations)
    truck_two = structures.Truck(2, locations)
    while len(packages.keys) > 0 or len(truck_one.payload.keys) > 0 or len(truck_two.payload.keys) > 0:
        if local.global_time <= truck_one.curr_time and local.global_time <= truck_two.curr_time:
            break
        if len(truck_one.payload.keys) == 0 and len(packages.keys) > 0:
            if truck_one.curr_location != locations.node_list[0]:
                truck_one.goto_location(locations.node_list[0])
            load_truck(truck_one, packages)
        if len(truck_two.payload.keys) == 0 and len(packages.keys) > 0:
            if truck_two.curr_location != locations.node_list[0]:
                truck_two.goto_location(locations.node_list[0])
            load_truck(truck_two, packages)
        if truck_one.curr_time <= truck_two.curr_time or len(truck_one.payload.keys) == 1:
            truck_one.deliver_package()
        else:
            truck_two.deliver_package()
    if len(packages.keys) == 0 and len(truck_one.payload.keys) == 0 and len(truck_two.payload.keys) == 0:
        local.global_status_msg = "Status: All packages have been delivered on schedule."
    out_packages = structures.HashTable(40)
    out_packages.merge(truck_one.delivered)
    out_packages.merge(truck_one.payload)
    out_packages.merge(truck_two.delivered)
    out_packages.merge(truck_two.payload)
    out_packages.merge(packages)
    out_packages.sort_keys("package_id")
    print(local.global_status_msg)
    print("Total miles driven = " + str(truck_one.miles_driven + truck_two.miles_driven))
    return out_packages


# A simple greedy algorithm that loads a truck with the preference of keeping packages destined
# for the same zone together. A truck will not load packages destined for different zones unless
# all priority packages have been delivered or as required by a package's special-notes.
# Time complexity: O(n). Auxiliary space complexity O(1).
def load_truck(truck, packages):
    index = 0
    zone = ""
    while len(packages.keys) > 0:
        if index >= len(packages.keys):
            if len(packages.keys) > index and packages.find(packages.keys[index]).deadline == 1439 and zone != "":
                index = 0
                zone = ""
                continue
            break
        if len(truck.payload.keys) == truck.MAX_PAYLOAD:
            break
        else:
            # Check if the current package is a member of a set
            if "set" in packages.find(packages.keys[index]).value.special_notes:
                set_id = packages.find(packages.keys[index]).value.special_notes.split()[-1]
                set_count = 0
                for k in packages.keys:
                    if "set " + set_id in packages.find(k).value.special_notes:
                        set_count += 1
                if len(truck.payload.keys) + set_count <= truck.MAX_PAYLOAD:
                    i = 0
                    while i < len(packages.keys):
                        if "set " + set_id in packages.find(packages.keys[i]).value.special_notes:
                            if zone == "":
                                zone = packages.find(packages.keys[i]).value.zone
                            truck.load(packages.remove(packages.keys[i]).value)
                            continue
                        else:
                            i += 1
                    continue
            # Check if package is restricted to certain truck
            elif "Restricted" in packages.find(packages.keys[index]).value.special_notes:
                if truck.truck_id == int(packages.find(packages.keys[index]).value.special_notes.split()[-1]):
                    if zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                        zone = packages.find(packages.keys[index]).value.zone
                        truck.load(packages.remove(packages.keys[index]).value)
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            # Check if package is delayed
            elif "Delayed" in packages.find(packages.keys[index]).value.special_notes:
                time_delay = int(
                    int(packages.find(packages.keys[index]).value.special_notes.split()[-1].split(":")[0]) * 60) \
                             + int(packages.find(packages.keys[index]).value.special_notes.split()[-1].split(":")[1])
                if truck.curr_time >= time_delay:
                    if zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                        zone = packages.find(packages.keys[index]).value.zone
                        truck.load(packages.remove(packages.keys[index]).value)
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            # Check if package is going to the same zone as the other packages on the truck
            elif zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                zone = packages.find(packages.keys[index]).value.zone
                truck.load(packages.remove(packages.keys[index]).value)
            else:
                index += 1


# Parse package and location data from CSV files located in the project's root directory.
# Query the user for the time of day to be used for the simulation.
# Run the simulation and return a hashtable containing all packages.
def start():
    packages = dataloader.load_package_data("packages_csv.csv")
    locations = dataloader.load_location_data("locations_csv.csv")
    time_input = input("Enter the simulated current time in the 24-hour format HH:MM\n")
    local.global_status_msg = "Status: Some packages are still en route."
    try:
        local.global_time = int(time_input.split(":")[0]) * 60 + int(time_input.split(":")[1])
        if int(time_input.split(":")[0]) > 23 or int(time_input.split(":")[1]) > 59 or \
                int(time_input.split(":")[0]) < 0 or int(time_input.split(":")[1]) < 0:
            raise ValueError("Time out of range")
    except ValueError:
        print("Error: Invalid time\n")
        return start()
    except IndexError:
        print("Error: Invalid time\n")
        start()
        return None
    return simulate_to_curr_time(packages, locations)


# The main entry point and user interface of the program.
if __name__ == '__main__':
    main_packages = start()
    user_input = ""
    while user_input != "q" and user_input != "Q":
        print("Select from the following:")
        print("[L] - Lookup package by ID")
        print("[P] - Print all packages")
        print("[S] - Set current time")
        print("[Q] - Quit")
        user_input = input()
        if user_input == "L" or user_input == "l":
            user_input = input("Enter a package ID to lookup\n")
            if main_packages.keys.count(user_input) == 0:
                print("Error: A package with that ID does not exist in the database\n")
                continue
            print(str(main_packages.find(user_input).value))
        elif user_input == "P" or user_input == "p":
            for key in main_packages.keys:
                print(str(main_packages.find(key).value))
            print("")
        elif user_input == "S" or user_input == "s":
            main_packages = start()
        elif user_input != "q" and user_input != "Q":
            print("Error: Invalid input\n")
