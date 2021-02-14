import structures


def load_package_data(filename):
    # Open file, read packages one line at a time,
    # create package objects and append them to a list.
    # Return the list once the entire file is processed.
    package_hash = structures.HashTable(40)
    with open(filename) as package_data:
        lines = package_data.readlines()
        for line in lines:
            package_info = line.split(",")
            package = structures.Package(package_info[0], package_info[1], package_info[2], package_info[3],
                                         package_info[4], package_info[5], package_info[6], package_info[7])
            package_hash.insert(package.package_id, package)
    return package_hash


def load_location_data(filename):
    # Open file, read locations one line at a time,
    # Create a Graph object initialized with a node_list and adjacency matrix.
    # Populate and return graph.
    graph = structures.Graph([], [[]])
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
