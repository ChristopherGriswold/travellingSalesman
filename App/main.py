import math
import datetime

# Todo: Import node data and use that to create a graph. Use an adjacency matrix to store distances between nodes.
zones = {}
zones.update(dict.fromkeys(["84104", "84103", "84111", "84102"], "North"))
zones.update(dict.fromkeys(["84124", "84117", "84107", "84121"], "South"))
zones.update(dict.fromkeys(["84115", "84106", "84105"], "East"))
zones.update(dict.fromkeys(["84119", "84129", "84123", "84118"], "West"))

MINS_SINCE_MIDNIGHT = 480
global_time = 1349


class Node:
    name = None
    address = None
    node_id = None
    zone = None

    def __init__(self, name="", address="", node_id=0):
        self.name = name
        self.address = address
        self.node_id = node_id
        zip_start = address.index("(") + 1
        self.zone = str(zones[address[zip_start: zip_start + 5]])


class Graph:
    node_list = None
    adj_matrix = None

    def __init__(self, node_list, adj_matrix):
        self.node_list = node_list
        self.adj_matrix = adj_matrix

    def get_node(self, node_id):
        return self.node_list[node_id]

    def find_node_id(self, address):
        node_id = 0
        for node in self.node_list:
            if address in node.address:
                return node.node_id


# Todo: Import package data. Make every package an object.
class Package:
    package_id = None
    address = None
    node_id = None
    city = None
    state = None
    zip_code = None
    zone = None
    deadline = None
    mass_kilo = None
    special_notes = None
    status = "Holding"

    def __init__(self, package_id="", address="", city="", state="", zip_code="", deadline="",
                 mass_kilo="", special_notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        if deadline == "EOD":
            deadline = "23:59"
        self.deadline = int(deadline.split(":")[0]) * 60 + int(deadline.split(":")[1])
        self.mass_kilo = mass_kilo
        self.special_notes = special_notes
        self.zone = zones[zip_code]

    def __str__(self):
        return str("Package ID: " + str(self.package_id) + "\t\tAddress: " + self.address + " - " + self.city + ", " +
                   self.state + " " + self.zip_code + "\t\tDeadline: " + str(datetime.time(self.deadline // 60,
                   self.deadline % 60).strftime("%H:%M")) + "\t\tWeight: " + str(self.mass_kilo) + " k" +
                   "\t\tStatus: " + str(self.status))


class Truck:
    truck_id = None
    AVG_SPEED = 18
    MAX_PAYLOAD = 16
    miles_driven = 0
    curr_time = MINS_SINCE_MIDNIGHT
    road_map = None
    curr_location = None
    on_board = []
    delivered = []

    def __init__(self, truck_id, on_board, road_map):
        self.truck_id = truck_id
        self.on_board = on_board
        self.delivered = []
        self.road_map = road_map
        self.curr_location = road_map.node_list[0]

    def goto_location(self, location):
        distance = self.road_map.adj_matrix[self.curr_location.node_id][location.node_id]
        self.curr_location = location
        self.miles_driven += distance
        if distance > 0:
            self.curr_time += math.ceil((distance / self.AVG_SPEED) * 60)
        # if location.node_id != 0:
        #     pass
            # print("Package delivered at: " + str(self.curr_time // 60) + ":" + str(
            #     self.curr_time % 60) + " By truck " + str(self.truck_id))
        # else:
        #     print("Truck " + str(self.truck_id) + " is back at the HUB.")

    def deliver_package(self):
        closest_index = 0
        for i in range(1, len(self.on_board)):
            currnode = self.curr_location.node_id
            nextnode = self.road_map.find_node_id(self.on_board[i].address)
            dist = self.road_map.adj_matrix[currnode][nextnode]
            if dist < self.road_map.adj_matrix[self.curr_location.node_id][self.road_map.find_node_id(self.on_board[closest_index].address)]:
                closest_index = i

        package = self.on_board.pop(closest_index)
        self.goto_location(self.road_map.node_list[self.road_map.find_node_id(package.address)])
        self.delivered.append(package)
        package.status = "Delivered at: " + str(datetime.time(int(self.curr_time / 60), (self.curr_time % 60) - 1).strftime("%H:%M"))


def load_package_data(filename):
    # Open file, read packages one line at a time,
    # create package objects and append them to a list.
    # Return the list once the entire file is processed.
    package_list = []
    with open(filename) as package_data:
        lines = package_data.readlines()
        for line in lines:
            package_info = line.split(",")
            package_list.append(Package(package_info[0], package_info[1], package_info[2], package_info[3],
                                        package_info[4], package_info[5], package_info[6], package_info[7]))
    return package_list


def load_location_data(filename):
    # Open file, read locations one line at a time,
    # Create a Graph object initialized with a node_list and adjacency matrix.
    # Populate and return graph.
    graph = Graph([], [[]])
    with open(filename) as node_data:
        lines = node_data.readlines()
        for index, line in enumerate(lines):
            node_info = line.split(",")
            graph.node_list.append(Node(node_info[0], node_info[1], index))
            graph.adj_matrix.append([])
            for i, col in enumerate(node_info):
                if i > 1:
                    graph.adj_matrix[index].append(float(node_info[i]))
    return graph


def print_matrix(matrix):
    for row in matrix:
        for entry in row:
            print(str(entry), end=" |")
        print("")


def print_packages(packages):
    for package in packages:
        print(package)


# Todo: Implement greedy algorithm to calculate a decent route.

def load_truck(truck, packages):
    payload = []
    index = 0
    zone = ""
    while len(packages) > 0:
        if index >= len(packages):
            if packages[0].deadline == 1439 and zone != "":
                index = 0
                zone = ""
                continue
            break
        if len(payload) == truck.MAX_PAYLOAD:
            break
        else:
            # Check and see if the current package is a member of a set
            if "set" in packages[index].special_notes:
                set_id = packages[index].special_notes.split()[-1]
                set_count = 0
                for package in packages:
                    if "set " + set_id in package.special_notes:
                        set_count += 1
                if len(payload) + set_count <= truck.MAX_PAYLOAD:
                    i = 0
                    while i < len(packages):
                        if "set " + set_id in packages[i].special_notes:
                            if zone == "":
                                zone = packages[i].zone
                            payload.append(packages.pop(i))
                            continue
                        else:
                            i += 1
                    continue
            # Check and see if package is restricted to certain truck
            elif "Restricted" in packages[index].special_notes:
                if truck.truck_id == int(packages[index].special_notes.split()[-1]):
                    if zone == "" or zone == packages[index].zone:
                        zone = packages[index].zone
                        payload.append(packages.pop(index))
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            # Check and see if package is delayed
            elif "Delayed" in packages[index].special_notes:
                time_delay = int(int(packages[index].special_notes.split()[-1].split(":")[0]) * 60) + int(packages[index].special_notes.split()[-1].split(":")[1])
                if truck.curr_time >= time_delay:
                    if zone == "" or zone == packages[index].zone:
                        zone = packages[index].zone
                        payload.append(packages.pop(index))
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            elif zone == "" or zone == packages[index].zone:
                zone = packages[index].zone
                payload.append(packages.pop(index))
            else:
                index += 1
    truck.on_board = payload
    for package in payload:
        package.status = "Out for Delivery"


def sort_packages_by_deadline(packages):
    for i in range(len(packages)):
        for j in range(i + 1, len(packages)):
            if packages[j].deadline < packages[i].deadline:
                packages[i], packages[j] = packages[j], packages[i]


def sort_packages_by_id(packages):
    for i in range(len(packages)):
        for j in range(i + 1, len(packages)):
            if int(packages[j].package_id) < int(packages[i].package_id):
                packages[i], packages[j] = packages[j], packages[i]


# Todo: Implement a user interface that allows the user to see the route progression at any given time.
def display_menu():
    print("Enter the current simulated time in the 24-hour format HH:MM")
    user_input = input()
    global global_time
    global_time = int(user_input.split(":")[0]) * 60 + int(user_input.split(":")[1])
    pkgs = simulate_to_time(global_time)
    while user_input != "q" and user_input != "Q":
        print("Select from the following:")
        print("[L]ookup package by ID")
        print("[P]rint all packages")
        print("[S]et current time")
        print("[Q]uit")
        user_input = input()
        if user_input == "L" or user_input == "l":
            print("Enter a package ID to lookup")
            l_input = int(input())
            print(str(pkgs[l_input - 1]))
            pass
        elif user_input == "P" or user_input == "p":
            for package in pkgs:
                print(str(package))
        elif user_input == "S" or user_input == "s":
            print("Enter the current simulated time in the 24-hour format HH:MM")
            s_input = input()
            global_time = int(s_input.split(":")[0]) * 60 + int(s_input.split(":")[1])
            pkgs = simulate_to_time(global_time)


def simulate_to_time(time):
    sort_packages_by_deadline(packages)
    truck_one = Truck(1, [], location_graph)
    truck_two = Truck(2, [], location_graph)
    while len(packages) > 0 or len(truck_one.on_board) > 0 or len(truck_two.on_board) > 0:
        if global_time < truck_one.curr_time or global_time < truck_two.curr_time:
            break
        if len(truck_one.on_board) == 0 and len(packages) > 0:
            if truck_one.curr_location != location_graph.node_list[0]:
                truck_one.goto_location(location_graph.node_list[0])
            load_truck(truck_one, packages)
        if len(truck_two.on_board) == 0 and len(packages) > 0:
            if truck_two.curr_location != location_graph.node_list[0]:
                truck_two.goto_location(location_graph.node_list[0])
            load_truck(truck_two, packages)
        if len(truck_one.on_board) > 0 and truck_one.curr_time <= truck_two.curr_time or len(truck_one.on_board) == 1:
            truck_one.deliver_package()
        if len(truck_two.on_board) > 0 and truck_two.curr_time <= truck_one.curr_time or len(truck_two.on_board) == 1:
            truck_two.deliver_package()
    out_packages = []
    out_packages.extend(truck_one.delivered)
    out_packages.extend(truck_one.on_board)
    out_packages.extend(truck_two.delivered)
    out_packages.extend(truck_two.on_board)
    out_packages.extend(packages)
    sort_packages_by_id(out_packages)
    print("Total miles driven = " + str(truck_one.miles_driven + truck_two.miles_driven))
    return out_packages


if __name__ == '__main__':
    packages = load_package_data("packages_csv.csv")
    location_graph = load_location_data("locations_csv.csv")
    display_menu()
