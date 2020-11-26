"""
    File that contains fonctions computing useful stuff for the export  
"""

import random
import graph
import uuid 
from parameters import *

random.seed(42)
def legs_builder(leg_list):
    """
        Parameter : list of legs returned by generate_leg if data is generated and read_leg otherwise
        Returns : - list of Flight objects sorted by departure time
                  - dictionary that maps a flight id to the Flight object
                  - list of Maint objects sorted by beginning time
    """
    #Lists + dictionary to return
    flights = []
    flights_id = {}
    maints = []

    #Counts number of flights and maintenances
    nb_flight = 0
    nb_maint = 0
    for leg in leg_list:
        id, leg_type, aircraft, origin, destination, dt, at = leg 

        #Arrival time can be the day after so we have to handle this case (we suppose nothing last more than 24 hours)
        if dt < at:
            dur = at - dt
        else:
            dur = 60*24+at - dt

        if leg_type == "LEG":
            #Time window is set on the basis of the airport closure 
            if dt >= closure_beginning and dt <= closure_ending and origin == "CDG":
                a = closure_ending
            elif at >=closure_beginning and at <= closure_ending and destination == "CDG":
                a = closure_ending - dur
            else:
                a = dt

            b = min(dt + delay_limit_flight,24*60)
            nb_flight += 1
            nb_pass = random.randint(passengers_nb_min,passengers_nb_max)
            del_cost = dt
            current_flight = graph.Flight(id,aircraft,origin,destination,dt,dur,a,b,
                                            capacity,nb_pass,del_cost,roc_cost)
            flights_id[id] = current_flight
            flights.append(current_flight)
        else: #Maintenance case
            a = dt 
            b = min(dt + delay_limit_maint,24*60)
            nb_maint += 1
            maints.append(graph.Maint(id,aircraft,dt,dur,a,b,dur)) #Cost = duration
    print(nb_flight, nb_maint)
    return sorted(flights,key=lambda f:f.bt), flights_id, sorted(maints,key=lambda f:f.bt)

def passengers_arcs_builder(flights,flights_id):
    """
        Parameters : - list of Flight object returned by leg_builder
                     - dictionary returned by leg_builder
        Returns : set of PassengersTransit objects

        This function also adds some dummy flights to the flights list and update flights_id
    """
    passengers_arcs = set() #Set to return 
    dummy_flights = []
    for i in range(len(flights)):

        #We connect flights arriving to CDG and departing from CDG 
        if flights[i].destination == "CDG":
            j = i+1

            #Aggregate number of passengers of flights[i] connecting with an other flight
            #Enables to check that there are'nt more passengers connecting than passengers in the aircraft
            connecting_pass_nb = 0 
            
            #We loop over flight departing after flights[i] but not too far after 
            while(j < len(flights) and flights[j].bt <= flights[i].bt + flights[i].dur + max_connection_time
                   and connecting_pass_nb <= flights[i].cap):
                nb_pass_connection = int(flights[i].nb_pass*random.uniform(rate_pass_connection_min,rate_pass_connection_max))+1
                
                #We check that some conditions are satisfied before adding a passenger arc
                if(flights[j].origin == "CDG" and flights[j].bt >= flights[i].bt + flights[i].dur + connection_time 
                and flights[j].destination != flights[i].origin 
                and flights[j].nb_pass + flights[j].nb_pass_connection + nb_pass_connection <= flights[j].cap):
                    passengers_arcs.add(graph.PassengersTransit(flights[i].id,flights[j].id,
                    connection_time,nb_pass=nb_pass_connection))
                    flights[j].add_pass(nb_pass_connection) 
                    connecting_pass_nb += nb_pass_connection
                j += 1
        else: #We connect flight departing from CDG and arriving to X with a dummy flight
            #Generation of connections number
            nb_connections = random.randint(connection_min,connection_max)
            #Generation of dummy flights 
            for k in range(nb_connections):

                #Generation of the dummy flight features
                aircraft_id = str(uuid.uuid4()) #It will always be a different aircraft 
                crew_id = str(uuid.uuid4())
                dummy_origin = flights[i].destination
                dummy_destination = "BAHAMAS" #Helpful to recognize a dummy flight
                dummy_flight_id = dummy_origin+"-"+dummy_destination+str(uuid.uuid4())
                dummy_dur = random.randint(duration_min,duration_max)   
                time_window = random.randint(time_window_min,time_window_max)
                dummy_dt = flights[i].bt + flights[i].dur + connection_time + time_window

                #No dummy flight departing the day after
                if dummy_dt >= 24*60:
                    nb_connections -= 1 
                else:
                    dummy_at = dummy_dt + dummy_dur
                    dummy_a = dummy_dt
                    dummy_b = dummy_dt #We don't want to delay dummy flights
                    nb_pass_connection = int(flights[i].nb_pass*random.uniform(rate_pass_connection_min,rate_pass_connection_max))+1
                    dummy_nb_pass = random.randint(passengers_nb_min,passengers_nb_max-nb_pass_connection)
                    dummy_capacity = capacity
                    dummy_del_cost = dummy_dt*len(flights) #We don't want to delete dummy flights either
                    dummy_roc_cost = roc_cost
                    dummy_flight = graph.Flight(dummy_flight_id,aircraft_id,dummy_origin,
                            dummy_destination,dummy_dt,dummy_dur,dummy_a,dummy_b,dummy_capacity,
                            dummy_nb_pass,dummy_del_cost,dummy_roc_cost,crew_id=crew_id)
                    dummy_flights.append(dummy_flight) 
                    passengers_arcs.add(graph.PassengersTransit(flights[i].id,dummy_flight_id,connection_time,
                            nb_pass=nb_pass_connection))
                    flights_id[dummy_flight_id] = dummy_flight
    flights += dummy_flights
    flights.sort(key=lambda f: f.bt)
    return passengers_arcs

def aircraft_rotation_builder(flights,maints):
    """
        Parameters : - list of Flight objects (can include dummy flights) 
                     - list of Maint objects
        Returns a dictionary that maps an aircraft id to the list of flights and maintenances planned for it
    """
    aircraft_rotation = {}
    for flight in flights:
        if flight.aircraft in aircraft_rotation.keys():
            aircraft_rotation[flight.aircraft].append(flight)
        else:
            aircraft_rotation[flight.aircraft] = [flight]
    for maint in maints:
        if maint.aircraft in aircraft_rotation.keys():
            aircraft_rotation[maint.aircraft].append(maint)
        else:
            aircraft_rotation[maint.aircraft] = [maint]
    return aircraft_rotation

def same_flights_builder(flights):
    """
        Parameter : list of Flight objects
        Returns a dictionary that maps an origin and a destination to the list of flights that
        have this origin and this destination
    """
    same_flights = {}
    for flight in flights:
        if flight.origin in same_flights.keys():
            if flight.destination in same_flights[flight.origin].keys():
                same_flights[flight.origin][flight.destination].append(flight)
            else:
                same_flights[flight.origin][flight.destination] = [flight]
        else:
            same_flights[flight.origin] = {flight.destination:[flight]}
    return same_flights

def setting_alternatives(same_flights):
    """
        Parameter : dictionary returned by same_flights_builder 
        Returns nothing

        This function sets the alternatives attribute of each Flight object.
        The list of alternatives of a given flight f consist only of one flight that is the next flight
        departing from the same origin and arriving to the same destination as f.
    """
    for o in same_flights.keys():
        for d in same_flights[o].keys():
            if d != "BAHAMAS": #We don't set alternatives to dummy flights
                same_flights[o][d].sort(key=lambda f: f.bt)
                for i in range(len(same_flights[o][d])-1):
                    same_flights[o][d][i].add(same_flights[o][d][i+1].id)

def aircraft_arcs_builder(aircraft_rotation):
    """
        Parameter : dictionary returned by aircraft_rotation_builder
        Returns : - set of GroundService objects
                  - set of MaintenanceIn objects
                  - set of MaintenanceOut objects

        Ground service arc : arc between two flights carried out by the same aircraft and that follow each other
        Maintenance arc "in" : arc from a flight to a maintenance
        Maintenance arc "out" : arc from a maintenance to a flight
    """
    ground_service_arcs = set()
    maintenance_in_arcs = set()
    maintenance_out_arcs = set()
    for aircraft,legs in aircraft_rotation.items():
        legs_sorted = sorted(legs,key=lambda x: x.bt)
        for i in range(len(legs_sorted)-1):
            if isinstance(legs_sorted[i],graph.Flight) and isinstance(legs_sorted[i+1],graph.Flight):
                ground_service_arcs.add(graph.GroundService(legs_sorted[i].id,legs_sorted[i+1].id,
                min(legs_sorted[i+1].bt-legs_sorted[i].bt-legs_sorted[i].dur,ground_time_max)))
            elif isinstance(legs_sorted[i],graph.Flight) and isinstance(legs_sorted[i+1],graph.Maint): 
                maintenance_in_arcs.add(graph.MaintenanceIn(legs_sorted[i].id,legs_sorted[i+1].id))
            elif isinstance(legs_sorted[i],graph.Maint) and isinstance(legs_sorted[i+1],graph.Flight):
                maintenance_out_arcs.add(graph.MaintenanceOut(legs_sorted[i].id,legs_sorted[i+1].id))
    return ground_service_arcs, maintenance_in_arcs, maintenance_out_arcs

def crew_arcs_builder(crew_rotation):
    """
        Parameter : dictionary returned by read_crew 
        Returns : - set of CrewTransit objects
                  - set of CrewTimeLimit objects 

        Crew transit arc : arc that indicates that the crew changes aircraft between two flights
        Crew time limit arc : arc between the last and the first flight of a crew 
    """
    crew_transit_arcs = set()
    crew_time_limit_arcs = set()
    for crew,rotation in crew_rotation.items(): 
        if len(rotation) >= 2:
            crew_time_limit_arcs.add(graph.CrewTimeLimit(rotation[-1].id,rotation[0].id,reserve_crew_cost))
        for i in range(len(rotation)-1):
            if rotation[i].aircraft != rotation[i+1].aircraft:
                crew_transit_arcs.add(graph.CrewTransit(rotation[i].id,rotation[i+1].id))
    return crew_transit_arcs, crew_time_limit_arcs

def swaps_builder(aircraft_rotation,same_flights):
    """
        Parameters : - dictionary returned by aircraft_rotation_builder
                     - dictionary returned by same_flights_builder
        Returns : set of tuples of two flights id corresponding to possible swaps

        A possible swap is a pair of distinct flights that take off from the same airport and       
        approximately at the same hour and such that either of them are followed by a maintenance
    """
    can_be_swapped = {}
    
    #We start by marking flights followed by a maintenance in the day because we don't allow swaps
    #with such flights
    for aircraft, legs in aircraft_rotation.items():
        legs_sorted = sorted(legs,key=lambda x: x.bt)
        last_maintenance = max([i for i in range(len(legs_sorted)) if isinstance(legs_sorted[i],graph.Maint)]+[0])
        for i,leg in enumerate(legs_sorted):
                can_be_swapped[leg] = (i > last_maintenance)

    swaps = set() #Set to be returned 
    same_origin = {}

    #We regroup all flights departing from the same airport thanks to same_flights and then we
    #we try all pairs of flights 
    for o in same_flights.keys():
        same_origin[o] = []
        for d in same_flights[o].keys():
            if d != "BAHAMAS": #We don't want to swap with dummy flights
                for flight in same_flights[o][d]:
                    same_origin[o].append(flight)
        for f in same_origin[o]:
            for fprime in same_origin[o]:
                if (f != fprime and fprime.bt >= f.bt - swaps_time_window 
                and fprime.bt <= f.bt + swaps_time_window and (fprime,f) not in swaps
                and can_be_swapped[f] and can_be_swapped[fprime]):
                    swaps.add((f,fprime))
    return swaps

def round_trips_builder(aircraft_rotation):
    """
        Parameter : dictionary returned by aircraft_rotation_builder
        Returns a list of tuples of two fight id corresponding to the round trips, i.e.
        the pairs of flights that must be deleted together
    """
    round_trips = []
    for aircraft,legs in aircraft_rotation.items():
        flights_sorted = sorted([leg for leg in legs if isinstance(leg,graph.Flight)],key=lambda x: x.bt)
        if flights_sorted == []:
            continue
        origin_first_flight = flights_sorted[0].origin 
        idx_first_leg = [i for i in range(len(flights_sorted)) if flights_sorted[i].origin == origin_first_flight]
        for i in range(1,len(flights_sorted)):  
            if i not in idx_first_leg:
                round_trips.append((flights_sorted[i-1].id,flights_sorted[i].id))
    return round_trips

