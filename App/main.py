# Todo: Import node data and use that to create a graph. Use an adjacency matrix to store distances between nodes.
zones = {}
zones.update(dict.fromkeys(["84104", "84103", "84111", "84102"], "North"))
zones.update(dict.fromkeys(["84124", "84117", "84107", "84121"], "South"))
zones.update(dict.fromkeys(["84115", "84106", "84105"], "East"))
zones.update(dict.fromkeys(["84119", "84129", "84123", "84118"], "West"))


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


# Todo: Import package data. Make every package an object.
class Package:
    package_id = None
    address = None
    city = None
    state = None
    zip_code = None
    delivery_deadline = None
    mass_kilo = None
    special_notes = None
    status = "Holding"

    def __init__(self, package_id="", address="", city="", state="", zip_code="", delivery_deadline="",
                 mass_kilo="", special_notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.delivery_deadline = delivery_deadline
        self.mass_kilo = mass_kilo
        self.special_notes = special_notes

    def __str__(self):
        return str(str(self.package_id) + "\t" + self.address + "\t" + self.city + ", " + self.state + "\t" +
                   self.zip_code + "\t" + self.delivery_deadline + "\t" + str(self.mass_kilo) + "\t" +
                   self.special_notes + "\t" + str(self.status))


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
                    graph.adj_matrix[index].append(node_info[i])
    return graph


def print_matrix(matrix):
    for row in matrix:
        for entry in row:
            print(str(entry), end=" |")
        print("")


# Todo: Implement greedy algorithm to calculate a decent route.

def calculate_route(locations, packages):
    pass


# Todo: Implement a user interface that allows the user to see the route progression at any given time.

if __name__ == '__main__':
    packages = load_package_data("packages_csv.csv")
    location_graph = load_location_data("locations_csv.csv")
    # print_matrix(location_graph.adj_matrix)
    for i, node in enumerate(location_graph.node_list):
        print(node.name + " - " + node.address + " | " + node.zone)
