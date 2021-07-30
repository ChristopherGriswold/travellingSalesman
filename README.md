# c950
Data Structures and algorithms II

###### Algorithm Overview
A simple yet effective Greedy algorithm was chosen to deliver packages.

The main algorithm is divided into two parts, namely the truck loading phase and the package delivery phase. During the execution of the main.load_truck() method packages are selected from the list of available packages and loaded onto the truck with a preference for keeping packages destined for the same geographical area or “zone” together. Packages addressed to locations that are in different zones are only loaded together when no more priority packages remain in the delivery list or as required by a package’s special-notes. For example, in the given scenario, there exists a set of 6 packages that are required to be delivered together even though they are going to opposite sides of the city. A package’s priority is determined by its delivery deadline. Any package that has a deadline earlier than end-of-day is considered high priority.

In essence, the packages have been presorted according to their priority(deadline) and the load_truck method loads the package with the highest priority that is currently available for delivery. It then loads all other available packages that are going to the same zone as the highest priority package. Actual route planning and delivery happens within the truck’s deliver_package() method.

In the second part of the algorithm located in the structures.Truck.deliver_package() method, a much simpler process is at work. It simply selects the package with the address nearest to the trucks current location, travels to that location and delivers the package. This method is called once for every package on board. For a more robust implementation, the algorithm would continue to prioritize by nearest delivery location but would ensure that said delivery will not cause a priority package to be late. However, for our purposes, this is not necessary given that all packages on board are guaranteed by the load_truck method to be within a very short geographic distance to the highest priority package on board. As shown in the program output all priority packages are delivered long before their deadlines.

<img src="./Screenshots/WGUPS_8-55.png?raw=true" alt="WGUPS_8-55.png"/>
