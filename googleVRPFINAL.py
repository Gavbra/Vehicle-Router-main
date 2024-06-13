import requests
import json
import urllib
from urllib.parse import urlparse
import csv
import re
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

###############################################################################################################################################
#Compiles the list of drivers
def driver_list_compiler():
    with open("/Users/gavin/Desktop/Python/drivers.csv") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        check_list = [row[0] for row in reader]
        reader = csv.reader(csvfile, delimiter = ",")

    def driver_add_sequence():
        driver_depots = ["Basingstoke", "Hull", "Manchester", "Salisbury"]
        driver_name = input("Please enter the name of the driver you wish to add: ").title()
        while not re.fullmatch(r"\w+", driver_name):
            print("Invalid name suspected. If name is valid, please contact your administrator. Otherwise, please enter a valid name.")
            driver_name = input("Please enter the name of the driver you wish to add: ").title()
        driver_depot = input("Please enter the driver's depot: ").title()
        if driver_depot not in driver_depots:
            while driver_depot not in driver_depots:
                print("Depot not recognised. Please enter a valid depot.")
                driver_depot = input("Please enter the driver's depot: ").title()
        yn = input(f"Driver name: {driver_name}, driver depot: {driver_depot}. Add driver to database? (y/n): ")
        if yn == "y":
            driver = [driver_name, driver_depot]
            with open("/Users/gavin/Desktop/Python/drivers.csv", "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(driver)

    input_ = None
    return_list = []
    while True:
        input_ = input("Please enter driver name. Enter 'done' when finished: ").title()
        if input_ in check_list and input_ not in return_list and re.fullmatch(r"\w+", input_):
            return_list.append(input_)
            print(f"List of drivers so far: {return_list}")
        elif input_ in check_list and input_ in return_list and re.fullmatch(r"\w+", input_):
            print(f"{input_} has already been added to the list. Driver list so far: {return_list}")
        elif input_ == "Done":
            return return_list
        else:
            driver_add_input = input("Driver name not recognised. Would you like to add a new driver to the list? (y/n): ")
            while driver_add_input not in ["y", "n"]:
                input("Invalid response. Would you like to add a new driver to the list? (y/n): ")
            if driver_add_input == "y":
                driver_add_sequence()
                continue
            elif driver_add_input == "n":
                continue
    return return_list

list_drivers = driver_list_compiler()
###############################################################################################################################################
#Generates the list of depots that will be passed to the distance matrix and the data model creator
def depots(driver_list):

    def depot_extractor(driver):
        with open("/Users/gavin/Desktop/Python/drivers.csv") as csvfile:
            reader = csv.reader(csvfile, delimiter = ",")
            for line in reader:
                if driver in line:
                    return line[1]

    depot_list = []
    for driver in driver_list:
        depot_list.append(depot_extractor(driver))
    depot_set = list(set(depot_list))
    return depot_set, depot_list

depot_set, depot_list = depots(list_drivers)
###############################################################################################################################################
#Compiles the list of destinations
def destination_list_compiler():
    def destinations_list_alphabetiser():
        with open("/Users/gavin/Desktop/Python/destinations.csv", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter = "|")
            destinations_list = [row for row in reader]
            destinations_list = [destinations_list[0]] + sorted(destinations_list[1:])

        with open("/Users/gavin/Desktop/Python/destinations.csv", "w") as csvfile:
            writer = csv.writer(csvfile, delimiter = "|")
            for row in destinations_list:
                writer.writerow(row)
    destinations_list_alphabetiser()

    def destination_add_sequence():
        destination_to_add = input("Please enter the name of the destination you wish to add: ").lower().replace(" ", "")
        yn = input(f"Destination name: {destination_to_add}. Add to directory? (y/n): ")
        if yn == "n":
            return
        elif yn not in ("y", "n"):
            while True:
                yn = input(f"Invalid response. Destination name: {destination_to_add}. Add to directory? (y/n): ").lower().replace(" ", "")
                if yn == "n":
                    return
                elif yn == "y":
                    break
        destination_coords = input(f"Please enter the latitude & longitude of the {destination_to_add}: ").replace(" ", "")
        while not re.match(r"5[0-9]\.\d{6},-?\d{1,2}\.\d{6}", destination_coords):
            destination_coords = input(f"Invalid latitude/longitude detected. Please enter a valid latitude/longitude. Enter 'cancel' to stop new destination input: ").replace(" ", "")
            if destination_coords == "cancel":
                return
        depot_bool_input = input(f"Is {destination_to_add} a depot? (y/n): ")
        while depot_bool_input not in ["y", "n"]:
            depot_bool_input = input(f"Invalid response. Is {destination_to_add} a depot? (y/n): ")
        if depot_bool_input == "y":
            depot_bool = True
        if depot_bool_input == "n":
            depot_bool = False

        with open("/Users/gavin/Desktop/Python/destinations.csv", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter = "|")
            destination_list = [row for row in reader]
            destination_list.append([destination_to_add, destination_coords, depot_bool])

        with open("/Users/gavin/Desktop/Python/destinations.csv", "w") as csvfile:
            writer = csv.writer(csvfile, delimiter = "|")
            for row in destination_list:
                writer.writerow(row)

    with open("/Users/gavin/Desktop/Python/destinations.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter = "|")
        next(reader, None)
        full_destination_list = dict((row[0].lower(), row[1]) for row in reader)
        destinations_list = [destination for destination in full_destination_list]
        print(destinations_list)

    input_ = None
    destinations_input_list = [depot for depot in depot_set] #adds the depots to the destinations_input_list first
    while True:
        print(f"Destinations added so far: {destinations_input_list}")
        input_ = input("Please enter the address of the destination you would like to add. Enter 'done' if finished: ").lower().replace(" ", "")
        if input_ in destinations_list and input_ not in destinations_input_list and re.match(r"\w+", input_):
            destinations_input_list.append(input_)
        elif input_ == "done":
            break
        elif input_ not in destinations_list:
            address_adder_input = input(f"Address: {input_} not recognised. Would you like to add a new address? (y/n): ")
            while address_adder_input.lower().replace(" ", "") not in ["y", "n"]:
                address_adder_input = input("Invalid input. Would you like to add a new address? (y/n): ")
            if address_adder_input == "y":
                destination_add_sequence()
                with open("/Users/gavin/Desktop/Python/destinations.csv") as csvfile:
                    reader = csv.reader(csvfile, delimiter = "|")
                    next(reader, None)
                    full_destination_list = dict((row[0].lower(), row[1]) for row in reader)
                    destinations_list = [destination for destination in full_destination_list]
                    print(destinations_list)
    list_dest = [full_destination_list[dest.lower()] for dest in destinations_input_list]
    return list_dest, destinations_input_list

list_dest, destinations_input_list = destination_list_compiler()
###############################################################################################################################################
#compile user input into an API call, make the API call and then process the response of that call into a distance matrix
def distance_matrix_gen(list_dest):

        API_key = "" #Enter your API key here

        def send_request(origin_addresses, dest_addresses, API_key):
            #Build and send request for the given origin and destination addresses
            def build_address_str(addresses):
                # Build a pipe-separated string of addresses
                address_str = ''
                for i in range(len(addresses)):
                    address_str += addresses[i] + '|'
                return urllib.parse.quote(address_str)

            request = 'https://maps.googleapis.com/maps/api/distancematrix/json?' #  "units=imperial" removed
            origin_address_str = build_address_str(origin_addresses)
            print(f"origin_addresses = {origin_addresses}")
            print(f"origin_address_str = {origin_address_str}")
            dest_address_str = build_address_str(dest_addresses)
            print(f"dest_adddresses = {dest_addresses}")
            print(f"dest_address_str = {dest_address_str}")
            request = request + '&origins=' + origin_address_str + '&destinations=' + dest_address_str + '&key=' + API_key
            jsonResult = urllib.request.urlopen(request).read()
            response = json.loads(jsonResult)
            return response

        def dmg(response): #'distance matrix generator' - converts dictionary returned by dmr into a distance matrix - can be used singularly or iteratively depending on the size of the matrix to be created, hence returning a portion of the distance matrix
            distance_matrix_portion = []
            for origin in response["rows"]:
                row_list = [origin["elements"][j]["distance"]["value"] for j in range(len(origin["elements"]))]
                distance_matrix_portion.append(row_list)
            return distance_matrix_portion

        distance_matrix = []
        max_request_size = 100
        num_addresses = len(list_dest)
        max_rows = max_request_size // num_addresses
        q, r = divmod(num_addresses, max_rows)
        if q > 0:
            for i in range(q):
                origin_addresses = list_dest[i * max_rows: (i + 1) * max_rows]
                distance_matrix += dmg(send_request(origin_addresses, list_dest, API_key))

        origin_addresses = list_dest[q * max_rows: q * max_rows + r]
        distance_matrix += dmg(send_request(origin_addresses, list_dest, API_key))

        return distance_matrix

distance_matrix = distance_matrix_gen(list_dest)
################################################################################################################################################
#generate the data object that the manager will process
def create_data_model(driver_list):
     data = {}
     depot_set, depot_list = depots(driver_list)
     if len(depot_set) > 1:
        depot_start_end = [depot_set.index(depot) for depot in depot_list]
        data["distance_matrix"] = distance_matrix
        data["num_vehicles"] = len(driver_list)
        data["starts"] = depot_start_end
        data["ends"] = depot_start_end
     else:
        data["distance_matrix"] = distance_matrix
        data["num_vehicles"] = len(driver_list)
        data["depot"] = 0

     return data

data = create_data_model(list_drivers)
###############################################################################################################################################
#Uses the data to compute the routes.
#Leading 'if' statement used to determine whether or not a multiple-depot route is required
if "starts" in data:
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["starts"], data["ends"]
    )
else:
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data["distance_matrix"][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)

#sets the parameter by which to calculate the cost of each journey. transit_callback_index simply sets this cost to the distance of the journey
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
)

dimension_name = "Distance"
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    1000000,  # vehicle maximum travel distance
    True,  # start cumul to zero
    dimension_name,
)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    """ print(f"Objective: {solution.ObjectiveValue()}") """
    max_route_distance = 0
    for vehicle_id in range(data["num_vehicles"]):
        route_addresses = []
        index = routing.Start(vehicle_id) #type: int
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += f" {manager.IndexToNode(index)} -> " #type: int
            route_addresses.append(destinations_input_list[manager.IndexToNode(index)])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f"{manager.IndexToNode(index)}\n"
        route_addresses.append(destinations_input_list[manager.IndexToNode(index)]) #ADDED
        plan_output += f"Distance of the route: {route_distance}m\n"
        """ print(plan_output) #ORIGINAL """
        print("---------------------------------------")
        print(f"Driver: {list_drivers[vehicle_id]}, route: {route_addresses}, total distance: {route_distance/1000}km") #ADDED
        max_route_distance = max(route_distance, max_route_distance)
    """ print(f"Maximum of the route distances: {max_route_distance}m") #ORIGINAL """

# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)
""" print(solution) #ADDED """

# Print solution on console.
if solution:
    print_solution(data, manager, routing, solution)
else:
    print("No solution found!")
