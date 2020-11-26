"""
    General parameters used essentially in list_builder.py
"""

import datetime
from parameters_generation import flights_nb, maints_nb
#Input paths
path = "../../Instances AirFrance/"
filename_legs = "leg_list.csv"
filename_crew = "crewRotation.csv"

#Day considered for the AirFrance instance
closure_day = datetime.datetime(2018,8,5)

#Closure time window 
closure_beginning = 14*60
closure_ending = 15*60

#Is the instance generated ?
is_generated = True

#Maximal authorized delay
delay_limit_flight = int(2.5*60)
delay_limit_maint = 1000

#Arcs lengths
ground_time_max = 45
crew_transit_time = 75
time_before_maint = 10
max_time_crew = 11*60+15

#Parameters related to "Flight" objects
capacity = 200

passengers_nb_min = 50
passengers_nb_max = capacity

#Connections parameters
connection_min = 0
connection_max = 1

rate_pass_connection_min = 0.01
rate_pass_connection_max = 0.1

connection_time = 20

max_connection_time = int(1.5*60) #Maximal initial time between 2 flights with a passenger arc between them
#Dummy flights duration
duration_min = 60 
duration_max = 4*60

#Time window between a flight and a dummy flight (enables the flight to be delayed)
time_window_min = 0
time_window_max = 30 

#Costs 
reserve_crew_cost = 100*60
roc_cost = 3*60 
swap_cost = 100*60

#Parameter to determine flights that take off nearly before or after a given flight and thus can be swapped with it
swaps_time_window = 30

#Export path
export_path = "../../Code CPLEX/DisruptionManagement_Cancellation/Instances/"
closure_duration = int((closure_ending - closure_beginning)/60)
if is_generated:
    export_filename = "instance_generated_"+str(flights_nb)+"_"+str(maints_nb)+"_"\
                        +str(closure_duration)+"H.csv"
else:
    export_filename = "instance_AF_" + str(closure_day)[:10] + "_"+str(closure_duration)+"H.csv"

