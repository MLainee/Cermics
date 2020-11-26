"""
    Some classes that enables us to store the data in the form of a graph
"""
import dateutil.parser
import datetime
from parameters import *
class Node:
    def __init__(self,id,aircraft,bt,dur,a,b):
        self._id = id
        #Aircraft concerned
        self._aircraft = aircraft
        #Beginning time
        self._bt = bt
        #Duration
        self._dur = dur
        #Time window
        self._a = a
        self._b = b 
    @property
    def id(self):
        return self._id
    @property
    def bt(self):
        return self._bt
    @property
    def dur(self):
        return self._dur
    @property
    def a(self):
        return self._a
    @property
    def b(self):
        return self._b
    @property 
    def aircraft(self):
        return self._aircraft

class Flight(Node):
    def __init__(self,id,aircraft,origin,destination,dt,dur,a,b,cap,nb_pass,
                del_cost,roc_cost,alternatives=None,crew_id=None):
        super().__init__(id,aircraft,dt,dur,a,b)
        self._origin = origin
        self._destination = destination
        #Capacity 
        self._cap = cap
        #Number of passengers
        self._nb_pass = nb_pass
        #Cost of deleting flight
        self._del_cost = del_cost
        #Cost of reassigning passengers on a flight of an other airline compagny
        self._roc_cost = roc_cost
        if alternatives is None: 
            self._alternatives = []
        else:
            self._alternatives = alternatives
        self._crew_id = crew_id
        #Number of passengers coming from a connection flight (not counted in nb_pass)
        self._nb_pass_connection = 0 
    @property
    def origin(self):
        return self._origin
    @property
    def destination(self):
        return self._destination
    @property
    def cap(self):
        return self._cap
    @property
    def nb_pass(self):
        return self._nb_pass
    @property
    def del_cost(self):
        return self._del_cost
    @property
    def roc_cost(self):
        return self._roc_cost
    @property 
    def alternatives(self):
        return self._alternatives
    def add(self,alternative):
        self._alternatives.append(alternative)
    @property
    def crew_id(self):
        return self._crew_id
    @crew_id.setter
    def crew_id(self,id):
        self._crew_id = id
    @property
    def nb_pass_connection(self):
        return self._nb_pass_connection
    def add_pass(self,nb):
        self._nb_pass_connection += nb
class Maint(Node):
    def __init__(self,id,aircraft,dt,dur,a,b,cost):
        super().__init__(id,aircraft,dt,dur,a,b)
        self._cost = cost
    @property
    def cost(self):
        return self._cost

class Arc:
    def __init__(self,f,g,dur):
        self._f = f
        self._g = g
        self._dur = dur
    @property
    def f(self):
        return self._f
    @property
    def g(self):
        return self._g
    @property
    def dur(self):
        return self._dur
    def __eq__(self,other):
        if isinstance(other,Arc):
            return ((self._f == other._f) and (self._g == other._g))
        else:
            return False
    def __hash__(self):
        return hash((self._f,self._g))

class GroundService(Arc):
    def __init__(self,f,g,ground_time):
        super().__init__(f,g,ground_time)
        
class CrewTransit(Arc):
    def __init__(self,f,g):
        super().__init__(f,g,crew_transit_time)

class MaintenanceIn(Arc):
    def __init__(self,f,g):
        super().__init__(f,g,time_before_maint) #A voir éventuellement avec Solène

class MaintenanceOut(Arc):
    def __init__(self,f,g):
        super().__init__(f,g,None)

class CrewTimeLimit(Arc):
    def __init__(self,f,g,cost):
        super().__init__(f,g,max_time_crew)
        self._cost = cost
    @property
    def cost(self):
        return self._cost
class PassengersTransit(Arc):
    def __init__(self,f,g,dur,cost=0,itineraries=None,nb_pass=0):
        super().__init__(f,g,dur)
        self._cost = cost
        if itineraries is None: 
            self._itineraries = []
        else:
            self._itineraries = itineraries
        self._nb_pass = nb_pass
    @property
    def cost(self):
        return self._cost
    @property
    def itineraries(self):
        return self._itineraries
    @property
    def nb_pass(self):
        return self._nb_pass

class Itinerary:
    def __init__(self,id,nb_pass,flights):
        self._id = id
        self._nb_pass = nb_pass
        self._flights = flights
    @property
    def id(self):
        return self._id
    @property
    def nb_pass(self):
        return self._nb_pass
    @property
    def flights(self):
        return self._flights