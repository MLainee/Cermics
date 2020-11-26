"""
    Contains functions to generate an instance from scratch
"""

import networkx as nx 
import uuid
import random
from parameters import crew_transit_time, max_time_crew
from parameters_generation import*

random.seed(45)
def generate_legs():
    """ 
        Returns a list of flights and maintenances (same format than the list returned by read_leg). 
        Their number is defined in parameters_generation.py
        Each flight/maintenance has an id, an aircraft, an origin, a destination, 
        a departure/beginning time and an arrival/ending time.
        
        To construct the list, we loop over a list of shuffled leg types ("LEG" for flight and "MAINT" for 
        maintenances) and we assign to each leg an id, an aircraft, an origin, a destination, 
        a departure/beginning time and an arrival/ending time depending on previous assignements
    """

    type_leg_list = ["LEG" for i in range(flights_nb)]
    for i in range(maints_nb):
        idx_maint = random.randint(0,len(type_leg_list)-1)
        #We make sure that there are'nt two maintenances following each other
        while type_leg_list[idx_maint] == "MAINT" or (idx_maint >= 1 and type_leg_list[idx_maint - 1] == "MAINT"):
            idx_maint = random.randint(0,len(type_leg_list)-1)
        type_leg_list.insert(idx_maint,"MAINT")

    leg_list = [] #List we will return
    idx = 0 
    #Setup for first leg 
    aircraft_id = str(uuid.uuid4())
    nb_legs_max = random.randint(min_legs_aircraft, max_legs_aircraft) #Maximum number of legs for the current aircraft
    current_legs_nb = 0 
    while idx < len(type_leg_list):
        leg_type = type_leg_list[idx]

        #If the current leg is the first of the list or if current aircraft can still perform
        #flights / maintenance and the end of day is not exceeded : we add current leg to this aircraft
        if current_legs_nb == 0 or (current_legs_nb < nb_legs_max and leg_list[-1][6] + ground_time_max <= 24*60):
            flight_aircraft = aircraft_id
            current_legs_nb += 1 
        else: #We create a new aircraft
            aircraft_id = str(uuid.uuid4())
            nb_legs_max = random.randint(min_legs_aircraft, max_legs_aircraft)
            flight_aircraft = aircraft_id 
            current_legs_nb = 1

        #Assignement of origin + destination for the first leg of an aircraft
        if current_legs_nb == 1:
            dt = random.randint(min_dep_time,max_dep_time)
            if leg_type == "MAINT":
                origin = hub
                destination = hub 
                at = dt + random.randint(maint_duration_min,maint_duration_max)
            else: 
                if random.randint(0,1):
                    origin = hub 
                    destination = random.choice(others_airports)
                else:
                    origin = random.choice(others_airports)
                    destination = hub
                # at = dt + random.randint(flight_duration_min,flight_duration_max)
                at = dt + times_dic[origin][destination]
        else:#Assignement of origin + destination for a random leg depending on previous one(s)
            origin = leg_list[-1][4]
            dt = leg_list[-1][6] + random.randint(ground_time_min,ground_time_max)
            if leg_type == "MAINT":
                destination = leg_list[-1][4]
                at = dt + random.randint(maint_duration_min,maint_duration_max)
            else:
                #We consider that a given aircraft rotation consist only in round trips 
                # of the form X-CDG and CDG-X
                if current_legs_nb == 2 and leg_list[-1][1] == "MAINT": 
                    destination = random.choice(others_airports)
                elif current_legs_nb > 2 and leg_list[-1][1] == "MAINT":
                    destination = leg_list[-2][3]
                else:
                    destination = leg_list[-1][3]
                # at = dt + random.randint(flight_duration_min,flight_duration_max)
                at = dt + times_dic[origin][destination]
        flight_id = origin+"-"+destination+str(uuid.uuid4())
        leg_list.append((flight_id,leg_type,flight_aircraft,origin,destination,dt,at))
        idx += 1 
    return leg_list

def generate_crew(flights):
    """
        Parameter : list of "Flight" objects
        Returns a dictionary that maps a crew id to the list of flights performed by the crew.

        To construct the dictionary, we start from a flight to which we assign a crew and we assign 
        a maximum number of flights that the crew can perform. Then, we try to find flights that can 
        be performed by the assigned crew after the first flight. If there are several candidates, we
        assign one randomly, we mark it as "assigned" and we continue. If there are no candidates, 
        we move to an other flight that hasn't been marked as "assigned" yet. We do this until each
        flight has been assigned to a crew.  
    """
    crew_rotations = {} #Dictionary we will return
    #At the beginning, no flights has been assigned
    is_assigned = [not flights[i].crew_id == None for i in range(len(flights))] 
    
    for i in range(len(flights)):
        if not is_assigned[i]:
            crew_id = "crew"+str(uuid.uuid4())
            crew_rotations[crew_id] = [flights[i]]
            flights[i].crew_id = crew_id
            is_assigned[i] = True
            nb_flights_max = random.randint(min_flights_crew,max_flights_crew)
            current_flights_nb = 1 
            current_flight_idx = i 

            #We try to assign a maximum number of flights to the current crew to the extent of nb_flights_max
            while current_flights_nb < nb_flights_max:
                j = current_flight_idx + 1
                candidates = []
                #Looking for candidates to follow current flight 
                #Candidates are flights that meet a certain number of conditions (essentially satisfy
                # precedence constraints but are not too far from the previous flight)
                while(j < len(flights) 
                  and flights[j].bt <= flights[current_flight_idx].bt + flights[current_flight_idx].dur 
                                       + max_interflights_time_crew
                  and flights[j].bt + flights[j].dur - flights[i].bt <= max_time_crew):
                    if((flights[j].aircraft == flights[current_flight_idx].aircraft or 
                      flights[j].bt >= flights[current_flight_idx].bt + flights[current_flight_idx].dur + crew_transit_time) 
                      and flights[current_flight_idx].destination == flights[j].origin and not is_assigned[j]):
                        candidates.append(j)
                    j += 1 
                if candidates == []:
                    break 
                candidate_chosen_idx = random.choice(candidates)
                is_assigned[candidate_chosen_idx] = True
                crew_rotations[crew_id].append(flights[candidate_chosen_idx])
                flights[candidate_chosen_idx].crew_id = crew_id
                current_flights_nb += 1 
                current_flight_idx = candidate_chosen_idx 
    return crew_rotations
                     
