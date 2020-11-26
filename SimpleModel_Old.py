# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 09:55:55 2020

@author: laine
"""

import gurobipy as gp
from gurobipy import GRB
import Parser as ps
def curfew(airport):
    return GRB.INFINITY

def turnover(airport):
    return 0

def passenger_delay(airport):
    return 0

print(gp.gurobi.version())

    
#flight format [id 0 ,departure 1 ,duration 2 ,origin 3 ,destination 4 , passengers 5 ,
#               capacity 6 , [(connection, passengers, destination),...] 7]

def FlightModelSimple(flights,connections):
    m = gp.Model('Flights')
    D ={}
    for f in flights:
        D[f[0]] = (m.addVar(lb = f[1], ub = curfew(f[3])),\
            m.addVar(lb = f[1]+f[2], ub = curfew(f[4])))
    m.update()
    m.setObjective(gp.quicksum((D[f[0]][1]-f[1]-f[2])*f[5] for f in flights),GRB.MINIMIZE)
    for f in flights:
        m.addConstr(D[f[0]][1]-D[f[0]][0],GRB.EQUAL,f[1])
    for id_f, id_g in connections:
        for f in flights.select(id_f,'*','*','*','*','*'):
            m.addConstr(D[id_g][0]-D[id_f][1],GRB.GREATER_EQUAL,turnover(f[4]))
            m.addConstr(D[id_g][0]-D[id_f][1],GRB.GREATER_EQUAL,passenger_delay(f[4]))
    m.optimize()
    
def FlightModel(flights,connections):
    m = gp.Model('Flights2')
    print(type(m))
    m.setParam("NotConvex",2)
    print(m.Params.NonConvex)
    penalty = 180
    bigM = 100000
    D,PR,NP,C = gp.tupledict({}), gp.tupledict({}), gp.tupledict({}), gp.tupledict({})
    for f in flights:
        D[f[0]] = (m.addVar(lb = f[1], ub = curfew(f[3]),name = "Dep"+str(f[0])),\
            m.addVar(lb = f[1]+f[2], ub = curfew(f[4]), name = "Arr"+str(f[0])),\
            m.addVar(vtype = GRB.INTEGER, name = "Pass"+str(f[0])))
        for c in f[7]:
            C[(f[0],c[0])] = m.addVar(vtype = GRB.BINARY,name = "conn_"+str(f[0])+"_"+str(c[0]))
        for g in flights.select('*','*','*','*',f[3],'*','*','*'):
            L = [c[2] for c in g[7]]
            if g[1]+g[2]+passenger_delay(f[3]) < f[1] and f[4] in L:
                PR[(g[0],f[0],f[4])] = m.addVar(lb = 0, vtype = GRB.INTEGER,name = "PR_"+str(g[0])+"_"+str(f[0]))
    for id_f,id_g in connections:
        c = flights.select(id_g,'*','*','*','*','*','*','*')[0][4]
        NP[(id_f,id_g,c)] = m.addVar(lb = 0, vtype = GRB.INTEGER,name = "NP_"+str(id_f)+"_"+str(id_g))
    p = m.addVar(vtype = GRB.INTEGER,name = "p")
    m.update()
    m.setObjective(penalty * p +gp.quicksum((D[f[0]][1]-f[1]-f[2])*D[f[0]][2]\
                                            for f in flights),GRB.MINIMIZE)
    for f in flights:
        m.addConstr(D[f[0]][1]-D[f[0]][0],GRB.EQUAL,f[2])
        m.addConstr(D[f[0]][2],GRB.EQUAL,f[5] + PR.sum('*',f[0],'*')- NP.sum('*',f[0],'*'))
        m.addConstr(D[f[0]][2],GRB.LESS_EQUAL,f[6])
        for c in f[7]:
            m.addConstr(PR.sum(f[0],'*',c[2]),GRB.LESS_EQUAL,NP.sum(f[0],'*',c[2]))
    for id_f, id_g in connections:
        for f in flights.select(id_f,'*','*','*','*','*','*','*'):
            b,c,d = f[7].select(id_g,'*','*')[0]
            m.addConstr(D[id_g][0]-D[id_f][1] + bigM * C[(id_f,id_g)],GRB.GREATER_EQUAL,\
                        max(turnover(f[4]),passenger_delay(f[4])))
            m.addConstr(NP[(id_f,id_g,d)],GRB.LESS_EQUAL, bigM * C[(id_f,id_g)])
            m.addConstr(NP[(id_f,id_g,d)],GRB.LESS_EQUAL,c)
            m.addConstr(NP[(id_f,id_g,d)],GRB.GREATER_EQUAL,c - (1-C[(id_f,id_g)]) * bigM)
            
            
    m.addConstr(p,GRB.EQUAL,NP.sum('*','*')-PR.sum('*','*')) #Maybe?#
    m.optimize()
    print(m.getVars())
    
def test():
    f = (0,100,1000,0,1,50,100,gp.tuplelist([(1,10,2),(2,1,3)]))
    g = (1,1250,150,1,2,50,100,[])
    h = (2,150,150,1,3,50,100,[])
    L = gp.tuplelist([f,g,h])
    F,M = ps.parse("C:/Users/laine/OneDrive/Desktop/Cermics/Re_Data_AirFrance/leg_list.csv")
    F2 = gp.tuplelist([])
    for f in F[2]:
        f.append([])
        F2.append(tuple(f))
    FlightModel(F2,[])
    #FlightModel(L,[(0,1),(0,2)])
    






    