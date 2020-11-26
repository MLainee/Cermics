"""
    Main file
"""

from parameters import *
import read_input
import list_builder
import graph
import write_output
import generate_input


if is_generated:#Random generation of the instance 
    leg_list = generate_input.generate_legs()
else:#Reading of the legs file (keeps only leg of the closure day)
    leg_list = read_input.read_leg()

#Construction of the list of flights, of a dictionary that maps id to the correspond object Flight and of 
#the list of maintenances
flights, flights_id, maints = list_builder.legs_builder(leg_list)

#Construction of passengers arcs
passengers_arcs = list_builder.passengers_arcs_builder(flights,flights_id)

#Counts the total number of passengers
total_nb_passengers = sum([flight.nb_pass for flight in flights])
print(total_nb_passengers)

if is_generated:#Random generation of crew rotations
    crew_rotation = generate_input.generate_crew(flights)
else:#Reading of crew rotations
    crew_rotation = read_input.read_crew(flights_id)

#Construction of aircraft rotations
aircraft_rotation = list_builder.aircraft_rotation_builder(flights,maints)

#Construction of same_flights
same_flights = list_builder.same_flights_builder(flights)

#Setting alternatives
list_builder.setting_alternatives(same_flights)

#Aircraft related arcs
ground_service_arcs, maintenance_in_arcs, maintenance_out_arcs = list_builder.aircraft_arcs_builder(aircraft_rotation)

#Crew related arcs
crew_transit_arcs, crew_time_limit_arcs = list_builder.crew_arcs_builder(crew_rotation)


#Construction of possible swaps 
swaps = list_builder.swaps_builder(aircraft_rotation,same_flights)

#Construction of round trips 
round_trips = list_builder.round_trips_builder(aircraft_rotation)
    
#Writing file readable by CPLEX
write_output.write_output(flights,swaps,round_trips,maints,passengers_arcs,crew_rotation,
                        crew_time_limit_arcs,maintenance_in_arcs,maintenance_out_arcs,
                        ground_service_arcs,crew_transit_arcs)
