import datetime
import local
import math


class HashTable:
    def __init__(self, init_capacity):
        self.capacity = init_capacity
        self.size = 0
        self.buckets = []
        self.keys = []
        for i in range(init_capacity):
            self.buckets.append([HashNode(None, None)])

    def hash(self, key):
        return int(key) % self.capacity

    def insert(self, key, value):
        self.size += 1
        index = self.hash(key)
        self.keys.append(key)
        # self.buckets[index].append(HashNode)
        # self.buckets[index][-1].key = key
        # self.buckets[index][-1].value = value
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


class HashNode:
    key = None
    value = None

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Graph:
    def __init__(self):
        self.node_list = []
        self.adj_matrix = [[]]

    def get_node(self, node_id):
        return self.node_list[node_id]

    def find_node_id(self, address):
        for node in self.node_list:
            if address in node.address:
                return node.node_id


class GraphNode:
    def __init__(self, name="", address="", node_id=0):
        self.name = name
        self.address = address
        self.node_id = node_id


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
        self.payload = HashTable(self.MAX_PAYLOAD)
        self.delivered = HashTable(40)
        self.curr_location = road_map.node_list[0]
        self.miles_driven = 0
        self.curr_time = local.SHIFT_START_TIME

    def load(self, package):
        if len(self.payload.keys) < self.MAX_PAYLOAD:
            package.status = "Out for delivery"
            self.payload.insert(package.package_id, package)
            return True
        else:
            return False

    def goto_location(self, location):
        distance = self.road_map.adj_matrix[self.curr_location.node_id][location.node_id]
        self.curr_location = location
        self.miles_driven += distance
        if distance > 0:
            self.curr_time += math.ceil((distance / self.AVG_SPEED) * 60)

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
        package.value.status = "Delivered at: " + str(
            datetime.time(int(self.curr_time / 60), (self.curr_time % 60) - 1).strftime("%H:%M"))
