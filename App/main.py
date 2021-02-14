import math
import datetime

# Zones are used to group nearby zip codes and get a general idea of their location relative to the HUB.
# This information can be used to more efficiently load trucks and avoid having packages destined for
# opposite sides of the city on the same truck at the same time.
zones = {}
zones.update(dict.fromkeys(["84104", "84103", "84111", "84102"], "North"))
zones.update(dict.fromkeys(["84124", "84117", "84107", "84121"], "South"))
zones.update(dict.fromkeys(["84115", "84106", "84105"], "East"))
zones.update(dict.fromkeys(["84119", "84129", "84123", "84118"], "West"))

# Times are represented internally as the number of minutes since midnight. 480 and 1349 are
# representative of 08:00 and 23:59 respectively.
shift_start_time = 480
global_time = 1349
global_status_msg = "Some packages are still en route."


class HashTable:

    def __init__(self, init_capacity):
        self.capacity = init_capacity
        self.size = 0
        self.buckets = []
        self.keys = []
        for i in range(init_capacity):
            self.buckets.append([])

    def hash(self, key):
        return int(key) % self.capacity

    def insert(self, key, value):
        self.size += 1
        index = self.hash(key)
        self.keys.append(key)
        self.buckets[index].append(HashNode(key, value))

    def insert_all(self, other):
        while len(other.keys) > 0:
            self.insert(other.keys[0], other.remove(other.keys[0]).value)

    def find(self, key):
        index = self.hash(key)
        for hash_node in self.buckets[index]:
            if hash_node.key == key:
                return hash_node
        return None

    def remove(self, key):
        index = self.hash(key)
        for hash_node in self.buckets[index]:
            if hash_node.key == key:
                self.keys.remove(key)
                self.buckets[index].remove(hash_node)
                self.size -= 1
                return hash_node
        return None

    def sort_keys(self, by):
        for i in range(len(self.keys)):
            val_i = int(getattr(self.find(self.keys[i]).value, by))
            for j in range(i + 1, len(self.keys)):
                val_j = int(getattr(self.find(self.keys[j]).value, by))
                if val_j < val_i:
                    self.keys[i], self.keys[j] = self.keys[j], self.keys[i]
                    val_i = val_j
        return self.keys


class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class GraphNode:
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
    # node_list = None
    # adj_matrix = None

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
    # package_id = None
    # address = None
    # node_id = None
    # city = None
    # state = None
    # zip_code = None
    # zone = None
    # deadline = None
    # mass_kilo = None
    # special_notes = None
    # status = "On schedule"

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
        self.status = "On schedule"

    def __str__(self):
        return str("Package ID: " + str(self.package_id) + "\t\tAddress: " + self.address + " - " + self.city + ", " +
                   self.state + " " + self.zip_code + "\t\tDeadline: " +
                   str(datetime.time(self.deadline // 60, self.deadline % 60).strftime("%H:%M")) + "\t\tWeight: " +
                   str(self.mass_kilo) + " k" + "\t\tStatus: " + str(self.status))


class Truck:
    AVG_SPEED = 18
    MAX_PAYLOAD = 16

    def __init__(self, truck_id, road_map):
        self.truck_id = truck_id
        self.road_map = road_map
        self.on_board = HashTable(self.MAX_PAYLOAD)
        self.delivered = HashTable(40)
        self.curr_location = road_map.node_list[0]
        self.miles_driven = 0
        self.curr_time = shift_start_time

    def goto_location(self, location):
        distance = self.road_map.adj_matrix[self.curr_location.node_id][location.node_id]
        self.curr_location = location
        self.miles_driven += distance
        if distance > 0:
            self.curr_time += math.ceil((distance / self.AVG_SPEED) * 60)

    def deliver_package(self):
        closest_key_index = 0
        for i in range(1, len(self.on_board.keys)):
            curr_node = self.curr_location.node_id
            next_address = self.on_board.find(self.on_board.keys[i]).value.address
            next_node = self.road_map.find_node_id(next_address)
            dist = self.road_map.adj_matrix[curr_node][next_node]
            whoKnows = self.road_map.find_node_id(self.on_board.find(self.on_board.keys[closest_key_index]).value.address)
            if dist < self.road_map.adj_matrix[self.curr_location.node_id][whoKnows]:
                closest_key_index = i

        package = self.on_board.remove(self.on_board.keys[closest_key_index])
        self.goto_location(self.road_map.node_list[self.road_map.find_node_id(package.value.address)])
        self.delivered.insert(package.key, package.value)
        package.value.status = "Delivered at: " + str(
            datetime.time(int(self.curr_time / 60), (self.curr_time % 60) - 1).strftime("%H:%M"))


def load_package_data(filename):
    # Open file, read packages one line at a time,
    # create package objects and append them to a list.
    # Return the list once the entire file is processed.
    package_hash = HashTable(40)
    with open(filename) as package_data:
        lines = package_data.readlines()
        for line in lines:
            package_info = line.split(",")
            package = Package(package_info[0], package_info[1], package_info[2], package_info[3],
                              package_info[4], package_info[5], package_info[6], package_info[7])
            package_hash.insert(package.package_id, package)
    return package_hash


def load_location_data(filename):
    # Open file, read locations one line at a time,
    # Create a Graph object initialized with a node_list and adjacency matrix.
    # Populate and return graph.
    graph = Graph([], [[]])
    with open(filename) as node_data:
        lines = node_data.readlines()
        for index, line in enumerate(lines):
            node_info = line.split(",")
            graph.node_list.append(GraphNode(node_info[0], node_info[1], index))
            graph.adj_matrix.append([])
            for i, col in enumerate(node_info):
                if i > 1:
                    graph.adj_matrix[index].append(float(node_info[i]))
    return graph


def print_packages(packages):
    for package in packages:
        print(package)


# A simple greedy algorithm that loads a truck with the preference of keeping packages destined for the same
# zone together. A truck will not load packages destined for different zones unless all priority packages have
# been delivered or as required by a package's special-notes.
def load_truck(truck, packages):
    payload = HashTable(16)
    index = 0
    zone = ""
    while len(packages.keys) > 0:
        if index >= len(packages.keys):
            if len(packages.keys) > index and packages.find(packages.keys[index]).deadline == 1439 and zone != "":
                index = 0
                zone = ""
                continue
            break
        if len(payload.keys) == truck.MAX_PAYLOAD:
            break
        else:
            # Check and see if the current package is a member of a set
            if "set" in packages.find(packages.keys[index]).value.special_notes:
                set_id = packages.find(packages.keys[index]).value.special_notes.split()[-1]
                set_count = 0
                for key in packages.keys:
                    if "set " + set_id in packages.find(key).value.special_notes:
                        set_count += 1
                if len(payload.keys) + set_count <= truck.MAX_PAYLOAD:
                    i = 0
                    while i < len(packages.keys):
                        if "set " + set_id in packages.find(packages.keys[i]).value.special_notes:
                            if zone == "":
                                zone = packages.find(packages.keys[i]).value.zone
                            payload.insert(packages.keys[i], packages.remove(packages.keys[i]).value)
                            continue
                        else:
                            i += 1
                    continue
            # Check and see if package is restricted to certain truck
            elif "Restricted" in packages.find(packages.keys[index]).value.special_notes:
                if truck.truck_id == int(packages.find(packages.keys[index]).value.special_notes.split()[-1]):
                    if zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                        zone = packages.find(packages.keys[index]).value.zone
                        payload.insert(packages.keys[index], packages.remove(packages.keys[index]).value)
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            # Check and see if package is delayed
            elif "Delayed" in packages.find(packages.keys[index]).value.special_notes:
                time_delay = int(int(packages.find(packages.keys[index]).value.special_notes.split()[-1].split(":")[0]) * 60) \
                             + int(packages.find(packages.keys[index]).value.special_notes.split()[-1].split(":")[1])
                if truck.curr_time >= time_delay:
                    if zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                        zone = packages.find(packages.keys[index]).value.zone
                        payload.insert(packages.keys[index], packages.remove(packages.keys[index]).value)
                        continue
                    else:
                        index += 1
                else:
                    index += 1
                    continue
            elif zone == "" or zone == packages.find(packages.keys[index]).value.zone:
                zone = packages.find(packages.keys[index]).value.zone
                payload.insert(packages.keys[index], packages.remove(packages.keys[index]).value)
            else:
                index += 1
    truck.on_board = payload
    # The truck is loaded. Update the status of all packages on-board as they are now out for delivery.
    for key in truck.on_board.keys:
        truck.on_board.find(key).value.status = "Out for delivery"
    # for package in payload:
    #     package.status = "Out for delivery"


# A simple selection sort algorithm. At O(n^2) the worst-case time complexity of the algorithm is sufficient as
# the average number of input elements is 40. This is an in-place sorting algorithm requiring O(1) auxiliary space.
# For larger data sets a more efficient sorting algorithm, such as quickSort, should be used.
# def sort_packages_by_deadline(packages):
#     for i in range(len(packages)):
#         for j in range(i + 1, len(packages)):
#             if packages[j].deadline < packages[i].deadline:
#                 packages[i], packages[j] = packages[j], packages[i]


# A simple selection sort algorithm. At O(n^2) the worst-case time complexity of the algorithm is sufficient as
# the average number of input elements is 40. This is an in-place sorting algorithm requiring O(1) auxiliary space.
# For larger data sets a more efficient sorting algorithm, such as quickSort, should be used.
# def sort_packages_by_id(packages):
#     for i in range(len(packages)):
#         for j in range(i + 1, len(packages)):
#             if int(packages[j].package_id) < int(packages[i].package_id):
#                 packages[i], packages[j] = packages[j], packages[i]


# Todo: Implement a user interface that allows the user to see the route progression at any given time.
def display_menu():
    print("Enter the simulated current time in the 24-hour format HH:MM")
    user_input = input()
    global global_time
    global_time = int(user_input.split(":")[0]) * 60 + int(user_input.split(":")[1])
    pkgs = simulate_to_time(global_time)
    while user_input != "q" and user_input != "Q":
        print("Select from the following:")
        print("[L]ookup package by ID")
        print("[P]rint all packages")
        print("[Q]uit")
        user_input = input()
        if user_input == "L" or user_input == "l":
            print("Enter a package ID to lookup")
            l_input = input()
            print(str(pkgs.find(l_input).value))
        elif user_input == "P" or user_input == "p":
            for key in pkgs.keys:
                print(str(pkgs.find(key).value))


def simulate_to_time(time):
    packages.sort_keys("deadline")
    truck_one = Truck(1, location_graph)
    truck_two = Truck(2, location_graph)
    while len(packages.keys) > 0 or len(truck_one.on_board.keys) > 0 or len(truck_two.on_board.keys) > 0:
        if global_time <= truck_one.curr_time or global_time <= truck_two.curr_time:
            break
        if len(truck_one.on_board.keys) == 0 and len(packages.keys) > 0:
            if truck_one.curr_location != location_graph.node_list[0]:
                truck_one.goto_location(location_graph.node_list[0])
            load_truck(truck_one, packages)
        if len(truck_two.on_board.keys) == 0 and len(packages.keys) > 0:
            if truck_two.curr_location != location_graph.node_list[0]:
                truck_two.goto_location(location_graph.node_list[0])
            load_truck(truck_two, packages)
        if len(truck_one.on_board.keys) > 0 and truck_one.curr_time <= truck_two.curr_time or len(truck_one.on_board.keys) == 1:
            truck_one.deliver_package()
        if len(truck_two.on_board.keys) > 0 and truck_two.curr_time <= truck_one.curr_time or len(truck_two.on_board.keys) == 1:
            truck_two.deliver_package()
    global global_status_msg
    if len(packages.keys) == 0 and len(truck_one.on_board.keys) == 0 and len(truck_two.on_board.keys) == 0:
        global_status_msg = "All packages delivered on schedule."
    out_packages = HashTable(40)
    out_packages.insert_all(truck_one.delivered)
    out_packages.insert_all(truck_one.on_board)
    out_packages.insert_all(truck_two.delivered)
    out_packages.insert_all(truck_two.on_board)
    out_packages.insert_all(packages)
    out_packages.sort_keys("package_id")
    print(global_status_msg)
    print("Total miles driven = " + str(truck_one.miles_driven + truck_two.miles_driven))
    return out_packages


# The main entry point of the program. Parse package and location data from CSV files located in the
# project's root directory and display menu selection screen to the user.
if __name__ == '__main__':
    packages = load_package_data("packages_csv.csv")
    location_graph = load_location_data("locations_csv.csv")
    display_menu()
