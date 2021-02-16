import structures


# Open file, read packages one line at a time, create package objects and insert them into a hash table.
# Return the hash table once the entire file is processed. Time complexity: O(n) where n is the number of
# lines in the file. Auxiliary space complexity: O(1)
def load_package_data(filename):
    with open(filename) as package_data:
        lines = package_data.readlines()
        package_hash = structures.HashTable(len(lines))
        for line in lines:
            package_info = line.split(",")
            package = structures.Package(package_info[0], package_info[1], package_info[2], package_info[3],
                                         package_info[4], package_info[5], package_info[6], package_info[7])
            package_hash.insert(package.package_id, package)
    return package_hash


# Open file, read locations one line at a time. Create a Graph object containing a list of
# locations and an adjacency matrix representing distances between locations. Populate and return graph.
# Time complexity: O(n) where n is the number of lines in the file. Auxiliary space complexity: O(1)
def load_location_data(filename):
    graph = structures.Graph()
    with open(filename) as node_data:
        lines = node_data.readlines()
        for index, line in enumerate(lines):
            node_info = line.split(",")
            graph.node_list.append(structures.GraphNode(node_info[0], node_info[1], index))
            graph.adj_matrix.append([])
            for i, col in enumerate(node_info):
                if i > 1:
                    graph.adj_matrix[index].append(float(node_info[i]))
    return graph
