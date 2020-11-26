"""
    File that manages the writing of an output readable by CPLEX
"""

from parameters import *
import random 

def write_output(flights,swaps,round_trips,maints,passengers_arcs,crew_rotation,crew_time_limit_arcs,
                maintenance_in_arcs,maintenance_out_arcs,ground_service_arcs,crew_transit_arcs):
    """
        Writes a csv file in a way that the CPLEX model can read it
    """
    with open(export_path+export_filename,'w') as f:
        nb_crew_rotation = sum([1 for crew in crew_rotation.keys() if crew_rotation[crew] != []]) 
        f.write(','.join(list(map(str,[len(flights),len(swaps),nb_crew_rotation,len(round_trips),
        len(maints),len(passengers_arcs), len(crew_time_limit_arcs),len(maintenance_in_arcs),
        len(maintenance_out_arcs), len(ground_service_arcs),len(crew_transit_arcs)])))+'\n')
        for flight in flights:
            f.write(','.join(list(map(str,[flight.id,flight.dur,flight.bt,flight.a,flight.b,flight.nb_pass,
            flight.cap,flight.del_cost,flight.roc_cost,flight.crew_id])))+','+','.join(flight.alternatives) + '\n')   
        for swap in swaps:
            f.write(','.join([swap[0].id,swap[1].id,str(swap_cost)])+'\n')
        for crew,rotation in crew_rotation.items():
            if rotation != []:
                f.write(','.join([crew,rotation[0].id,rotation[-1].id])+'\n')
        for ff in round_trips:
            f.write(ff[0]+','+ff[1]+'\n')
        for maint in maints:
            f.write(','.join(list(map(str,[maint.id,maint.dur,maint.bt,maint.a,maint.b,maint.cost])))+'\n')
        for arc in passengers_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g,arc.dur,arc.nb_pass])))+'\n')
        for arc in crew_time_limit_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g,arc.dur,arc.cost])))+'\n')
        for arc in maintenance_in_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g,arc.dur])))+'\n')
        for arc in maintenance_out_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g])))+'\n')
        for arc in ground_service_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g,arc.dur])))+'\n')
        for arc in crew_transit_arcs:
            f.write(','.join(list(map(str,[arc.f,arc.g,arc.dur])))+'\n')