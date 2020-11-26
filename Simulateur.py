# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:12:35 2020

@author: laine
"""


import simpy
import ParseAF as ps
import scipy.stats as st

M,S = ps.Delay_distrib()

P = ps.Pass_distrib()

CDGN = st.norm(loc = M[0], scale = S[0])
ORYN = st.norm(loc = M[1], scale = S[1])
LHN = st.norm(loc = M[2], scale = S[2])
MHN = st.norm(loc = M[3], scale = S[3])

MH_List = ['CAY','FDF','PTP']
LH_List = ['MIA']
T = ps.Airport_type()
for i in range(len(T)):
    if T.iloc[i]['Dpt'] != 'ORY' and T.iloc[i]['Dpt'] != 'CDG':
        if T.iloc[i]['Long_haul'] == 1.0:
            LH_List.append(T.iloc[i]['Dpt'])
        else:
            MH_List.append(T.iloc[i]['Dpt'])


def heuristic(Network,Plane):
    Plane.takeoff = True
    if Plane.id == 1:
        if Plane.swap(Network.Plane(0)) == -1:
            Plane.takeoff = False
    return 10

def takeoff_delay(Airport):
    if Airport == 'CDG':
        return max(0,round(CDGN.rvs()))
    if Airport == 'ORY':
        return max(0,round(ORYN.rvs()))
    if Airport in LH_List:
        return max(0,round(LHN.rvs()))
    if Airport in MH_List:
        return max(0,round(MHN.rvs()))
    print("Airport not found")
    return 0
    
def turnover(Airport):
    return 0

def passenger_delay(Airport):
    return 0

def delay(Airport):
    return 0

def generate_passengers(K,m,v, Distrib = P):
    #s = P[P['Capacity'] == Plane]
    a = K - v*K/m - m
    b = 1 - m*K + m*m
    n = - b/a
    N = n*K/m
    test = n*K*(N-K)*(N-n)/N/N/(N-1)
    retest = n*K/N
    return n,N,test,retest

def test(m,K):
    for i in range(10):
        n = 2*K + 10000000*i
        N = n*K/m
        D = st.hypergeom(int(N),n,K)
        print(int(N),n)
        print(D.var())

class Schedule(object):
    def __init__(self,L):
        self.list = L
        
    def id(self, i=0):
        if len(self.list) > 0:
            return self.list[i][0]
        return -1
        
    def departure(self,i=0):
        return self.list[i][1]
    
    def duration(self,i=0):
        return self.list[i][2]
    
    def origin(self,i=0):
        return self.list[i][3]
    
    def destination(self,i=0):
        return self.list[i][4]
    
    def passengers(self,i=0):
        return self.list[i][5]
    
    def connections(self,i=0):
        return self.list[i][6]
    
    def connecting_passengers(self,i=0):
        a = 0
        for c in self.connections(i):
            a+= c[1]
        return a
        
    
    def add_passengers(self, passengers, i=0):
        self.list[i][5] += passengers

    def change_connection(self, id, flight_id = "", passengers = 0):
        i = 0
        if flight_id != "":
            while i < len(self.list) and self.id(i)!= flight_id:
                i+=1
        if i > len(self.list):
            print("Flight not found")
            return -1
        if passengers !=0 :
            self.list[i][6].append((id,passengers))
            return passengers
        j = 0
        while j < len(self.connections(i)):
            a = self.connections(i)[j]
            if a[0] == id:
                self.list[i][6].pop(j)
                self.add_passengers(-a[1],i)
                return (a[1])
        print("Connection not found")
        return -2
    

    def pop(self):
        return self.list.pop(0)
    
    def append(self,f):
        self.list = f + self.list
    
    def copy(self):
        S = self.list.copy()
        return Schedule(S)
    
class Airplane(object):
    def __init__(self, S, id,capacity =100, Airport = 0):
        self.id = id
        self.schedule = S
        self.airport = Airport
        self.takeoff = True
        self.capacity = capacity
        self.destination = 0
        
    def swap(self,Plane):
        print(self.airport,Plane.airport)
        S1,S2 = self.schedule.copy(),Plane.schedule.copy()
        A1,A2 = self.destination, Plane.destination
        print(A1,A2)
        f1,f2 = [],[]
        if self.airport !=0:
            A1 = self.airport
        else:
            f1.append(S1.pop())
        if Plane.airport != 0:
            A2 = Plane.airport
        else:
            f2.append(S2.pop())
        if A1 != A2:
            print("Incompatible schedules")
            return(-1)
        print("Swap!")
        S1.append(f2)
        S2.append(f1)
        Plane.schedule = S1
        self.schedule = S2

class Network(object):
    def __init__(self,Airports,Planes):
        self.planes = Planes
        self.airports = Airports
        self.landed = []
        self.cost = 0
    
    def takeoff(self,env,Airport,Plane):
        print("Plane",Plane.id,"taking off on flight",Plane.schedule.id(),"at",env.now)
        Plane.airport = 0
        Plane.destination = Plane.schedule.destination()
        yield env.timeout(Plane.schedule.duration())
        yield(env.process(self.land(env,Airport,Plane)))
    
    def land(self,env,Airport,Plane):
        delay = env.now-Plane.schedule.duration()-Plane.schedule.departure()
        eff_passengers = Plane.schedule.passengers()-Plane.schedule.connecting_passengers()
        print(delay,eff_passengers)
        self.cost += delay * eff_passengers
        print("Plane",Plane.id,"landed in",Airport,"at",env.now)
        self.landed.append((Plane.schedule.id(),env.now))
        Plane.schedule.pop()
        Plane.airport = Airport
        Plane.destination = 0
        yield env.timeout(turnover(Airport))
        if Plane.schedule.id() != -1:
            yield env.process(self.query(env,Airport,Plane)) 
        
    def query (self,env,Airport,Plane):
        print(env.now)
        print(Plane.id,Plane.schedule.list)
        delay = heuristic(self,Plane)
        print(Plane.id,Plane.schedule.list)
        c = self.check_connections(env,Plane)
        if Plane.takeoff:
            yield env.timeout(max(c,Plane.schedule.departure()-env.now))
            yield env.timeout(takeoff_delay(Airport))
            yield env.process(self.takeoff(env,Plane.schedule.destination(),Plane))
        else:
            yield env.timeout(delay)
            yield(env.process(self.query(env,Airport,Plane)))
        
    def check_connections(self,env,Plane):
        a,t,d = 0,env.now,passenger_delay(Plane.airport)
        for c in Plane.schedule.connections():
            Found = False
            for f in self.landed:
                if c[0] == f[0]:
                    a = max(a,f[1]+d-t)
                    Found = True
                    break
            if Found == False:
                if t > Plane.schedule.departure():
                    print("Plane",Plane.id,"is waiting on connections")
                Plane.takeoff = False
                return -2
        return a
    
    def Plane(self,id):
        for p in self.planes:
            if p.id == id:
                return p
        

def generate_network(day = '09/09/2019'):
    Data = ps.Schedule_day(day)
    Planes=[]
    for i in range(len(Data)):
        P = Data[i]
        S = []
        for j in range(len(P)):
            p = P[j]
            s= []
            s.append(p.name)
            s.append(ps.mins(p['Dpt_time']))
            d = ps.mins(p['Arv_time'])-ps.mins(p['Dpt_time'])
            if d > 0:
                s.append(d)
            else :
                s.append(1440+d)
            s.append(p['Dpt'])
            s.append(p['Arv'])
            s.append(generate_passengers(p['Dpt'],p['Arv']))
            s.append([])
            s.append(generate_passengers(p['Dpt'],p['Arv'],True))
            S.append(s)
        Planes.append(Airplane(Schedule(S),P[0]['Plane']))
    N = Network([],Planes)
    return N

def trialN():
    S1 = Schedule([[1,100,100,1,2,50,[]],[3,200,100,2,4,50,[]]])
    S2 = Schedule([[2,150,100,2,3,50,[]]])
    P1 = Airplane(S1,0,1)
    P2 = Airplane(S2,1,2)
    N = Network([],[P1,P2])
    return N

def sim(N = []):
    if N == []:
        N = trialN()
    env = simpy.Environment()
    for i in range(len(N.planes)):
        env.process(N.query(env,N.planes[i].airport,N.planes[i]))
    env.run()
    return N.cost




       
        
        