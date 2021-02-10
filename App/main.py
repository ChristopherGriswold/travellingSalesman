# Todo: Import node data and use that to create a graph. Use an adjacency matrix to store distances between nodes.

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
    status = "None"

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


# Todo: Implement greedy algorithm to calculate a decent route.

# Todo: Implement a user interface that allows the user to see the route progression at any given time.
if __name__ == '__main__':
    packages = load_package_data("packages_csv.csv")
    for package in packages:
        print(package)
    # myPackage = Package(1, "195 W Oakland Ave", "Salt Lake City", "UT", "84115", "10:30 AM", 21, "None")
