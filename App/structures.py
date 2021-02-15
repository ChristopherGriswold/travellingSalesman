import local
import datetime
from typing import List


# Used by a hash table to store key-value pairs.
class HashNode:
    key = None
    value = None

    def __init__(self, key, value):
        self.key = key
        self.value = value


# A self-adjusting data structure that utilizes a simple modulo hash function along with chaining collision handling
# to store key-value pairs in a two-dimensional list. Along with typical insert, remove and find operations this
# implementation includes additional sorting and merging functionality.
class HashTable:
    buckets: List[List[HashNode]]

    def __init__(self, init_capacity):
        self.capacity = init_capacity
        self.size = 0
        self.buckets = []
        self.keys = []
        for i in range(init_capacity):
            self.buckets.append([])

    # Using the provided key, generate an index to the bucket list that will store a node
    # containing the key-value pair.
    def hash(self, key):
        return int(key) % self.capacity

    # Insert the key-value pair into the hash table and append the key to the key list. This operation is
    # done in constant O(1) time and auxiliary space.
    def insert(self, key, value):
        self.size += 1
        index = self.hash(key)
        self.keys.append(key)
        self.buckets[index].append(HashNode(key, value))

    # Insert all elements from the other hash table into this one. This operation is
    # done in linear O(n) time and constant O(1) auxiliary space.
    def merge(self, other):
        while len(other.keys) > 0:
            self.insert(other.keys[0], other.remove(other.keys[0]).value)

    # Find the node in the hash table corresponding to the provided key and return it. This operation
    # is done in linear O(n) time, where n is the number of elements contained in the table with the
    # same hash value. Auxiliary space complexity is O(1)
    def find(self, key):
        index = self.hash(key)
        for hash_node in self.buckets[index]:
            if hash_node.key == key:
                return hash_node
        return None

    # Find and remove the node in the hash table corresponding to the provided key and return it.
    # The key is also removed from the key list. This operation is done in linear O(n) time,
    # where n is the number of elements contained in the table with the same hash value.
    # Auxiliary space complexity is O(1)
    def remove(self, key):
        index = self.hash(key)
        for hash_node in self.buckets[index]:
            if hash_node.key == key:
                self.keys.remove(key)
                self.buckets[index].remove(hash_node)
                self.size -= 1
                return hash_node
        return None

    # A simple selection sort algorithm. At O(n^2) the worst-case time complexity of the algorithm is sufficient as
    # the average number of input elements is 40. This is an in-place sorting algorithm requiring O(1) auxiliary space.
    # For much larger data sets a more efficient sorting algorithm, such as quickSort, should be used.
    def sort_keys(self, by):
        for i in range(len(self.keys)):
            val_i = int(getattr(self.find(self.keys[i]).value, by))
            for j in range(i + 1, len(self.keys)):
                val_j = int(getattr(self.find(self.keys[j]).value, by))
                if val_j < val_i:
                    self.keys[i], self.keys[j] = self.keys[j], self.keys[i]
                    val_i = val_j
        return self.keys


# Used by a graph to store relevant location data.
class GraphNode:
    def __init__(self, name="", address="", node_id=0):
        self.name = name
        self.address = address
        self.node_id = node_id


# Stores a list of nodes representing map locations and the driving distances between each
# in the form of an adjacency matrix.
class Graph:
    def __init__(self):
        self.node_list = []
        self.adj_matrix = [[]]

    # Given a valid node_id, returns the corresponding node from the node list.
    def get_node(self, node_id):
        return self.node_list[node_id]

    # Given a valid address, returns the id of the node containing the address.
    def find_node_id(self, address):
        for node in self.node_list:
            if address in node.address:
                return node.node_id


# Stores all information regarding a delivery package.
class Package:
    def __init__(self, package_id="", address="", city="", state="", zip_code="", deadline="",
                 mass_kilo="", special_notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        if deadline == "EOD":
            deadline = str(local.SHIFT_END_TIME // 60) + ":" + str(local.SHIFT_END_TIME % 60)
        self.deadline = int(deadline.split(":")[0]) * 60 + int(deadline.split(":")[1])
        self.mass_kilo = mass_kilo
        self.special_notes = special_notes
        self.zone = local.zones[zip_code]
        self.status = "On schedule"

    # Returns a string representation of the package for use within the UI as a reporting mechanism.
    def __str__(self):
        return str("Package ID: " + str(self.package_id) + "\t\tAddress: " + self.address + " - " + self.city + ", " +
                   self.state + " " + self.zip_code + "\t\tDeadline: " +
                   str(datetime.time(self.deadline // 60, self.deadline % 60).strftime("%H:%M")) + "\t\tWeight: " +
                   str(self.mass_kilo) + " k" + "\t\tStatus: " + str(self.status))


# A representation of a package delivery truck that includes functionality to navigate between
# location nodes and load/deliver packages.
class Truck:
    AVG_SPEED = 18
    MAX_PAYLOAD = 16

    def __init__(self, truck_id, road_map):
        self.truck_id = truck_id
        self.road_map = road_map
        self.payload = HashTable(self.MAX_PAYLOAD)
        self.delivered = HashTable(40)
        self.curr_location = road_map.node_list[0]
        self.miles_driven = 0
        self.curr_time = local.SHIFT_START_TIME

    # Changes the status of all packages on board to reflect the fact that they are now out for delivery.
    # Time complexity is O(n), where n is the number of packages on board. Auxiliary space complexity is O(1).
    def load(self, package):
        if len(self.payload.keys) < self.MAX_PAYLOAD:
            package.status = "\033[93mOut for delivery\033[0m"
            self.payload.insert(package.package_id, package)
            return True
        else:
            return False

    # Navigate to the delivery location and update the truck's miles driven and time taken.
    def goto_location(self, location):
        distance = self.road_map.adj_matrix[self.curr_location.node_id][location.node_id]
        self.curr_location = location
        self.miles_driven += distance
        if distance > 0:
            self.curr_time += int(distance / self.AVG_SPEED * 60)
        if self.curr_time > local.global_time:
            self.miles_driven -= distance

    # Identifies the package with the nearest delivery address and delivers it. This operation happens
    # in linear O(n) time, where n is the number of packages on board. Auxiliary space complexity is O(1).
    def deliver_package(self):
        if len(self.payload.keys) == 0:
            return
        closest_key_index = 0
        for i in range(1, len(self.payload.keys)):
            curr_node = self.curr_location.node_id
            next_node = self.road_map.find_node_id(self.payload.find(self.payload.keys[i]).value.address)
            dist = self.road_map.adj_matrix[curr_node][next_node]
            next_node_id = self.road_map.find_node_id(
                self.payload.find(self.payload.keys[closest_key_index]).value.address)
            if dist < self.road_map.adj_matrix[self.curr_location.node_id][next_node_id]:
                closest_key_index = i
        package = self.payload.remove(self.payload.keys[closest_key_index])
        self.goto_location(self.road_map.node_list[self.road_map.find_node_id(package.value.address)])
        self.delivered.insert(package.key, package.value)
        if self.curr_time > local.global_time:
            return
        package.value.status = '\033[92m' + "Delivered at: " + str(
            datetime.time(int(self.curr_time / 60), self.curr_time % 60).strftime("%H:%M") + '\033[0m')
