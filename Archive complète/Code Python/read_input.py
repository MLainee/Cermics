"""
    File that manages the read of AirFrance instances
"""
import dateutil.parser
from parameters import *

def read_leg():
    """
        Reads leg file 
        Returns a list of tuple of the form :
        (flight id,leg type, aircraft id, origin, destination, departure time, arrival time)
    """ 
    with open(path + filename_legs) as f:
        lines = list(map(str.rstrip, f.readlines()))
        leg_list = list(map(lambda x:x.split(';'), lines[1:]))
        leg_list_readable = []

        for leg in leg_list:
            leg = list(map(lambda x:x.strip('\"'),leg))
            #Conversion of ISO8601 into a Datetime object
            dt_iso =  dateutil.parser.parse(leg[5])
            at_iso = dateutil.parser.parse(leg[6])
            day = datetime.datetime(dt_iso.year,dt_iso.month,dt_iso.day)
            if day == closure_day:
                #Conversion in minutes
                dt = 60*dt_iso.hour + dt_iso.minute
                at = 60*at_iso.hour + at_iso.minute
                origin = leg[3].strip()
                destination = leg[4].strip()
                leg_list_readable.append((leg[0].strip('_ '),leg[1],leg[2],origin,destination,dt,at))
        return leg_list_readable

def read_crew(flights_id):
    """
        Reads crew rotation file
        Returns a dictionary that maps a crew id to a list of Flight objects
    """ 
    with open(path + filename_crew) as f:
        lines = list(map(str.rstrip, f.readlines()))
        crew_rotations_str = list(map(lambda x:x.split(';'), lines[1:]))
        crew_rotations = {}

        for crew in crew_rotations_str:
            legs_id = crew[1].strip('[]\"').split(',')
            crew_id = crew[2].strip('"')
            crew_rotations[crew_id] = []
            for id in legs_id:
                #Some flights of crewRotation are not in leg_list + some flights appear in several crew rotations
                if id in flights_id.keys() and flights_id[id].crew_id == None:  
                    crew_rotations[crew_id].append(flights_id[id])
                    flights_id[id].crew_id = crew_id 
            crew_rotations[crew_id].sort(key=lambda x: x.bt)
        return crew_rotations
