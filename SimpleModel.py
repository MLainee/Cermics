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


    
#flight format [id 0 ,departure 1 ,duration 2 ,origin 3 ,destination 4 , passengers 5 ,
#               capacity 6 , [(connection, passengers, destination),...] 7,
#               connecting passengers (#) 8, following flight 9]

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
    
def FlightModelNC(flights,connections):
    m = gp.Model('Flights2')
    m.setParam("NonConvex",2)
    print(m.Params.NonConvex)
    penalty = 180
    bigM = 100000
    D,PR,NP,C = gp.tupledict({}), gp.tupledict({}), gp.tupledict({}), gp.tupledict({})
    for f in flights:
        D[f[0]] = (m.addVar(lb = f[1], ub = curfew(f[3]),name = "Dep"+str(f[0])),\
            m.addVar(lb = f[1]+f[2], ub = curfew(f[4]), name = "Arr"+str(f[0])),\
            m.addVar(name = "Pass"+str(f[0])), m.addVar(name = "PassEff"+str(f[0])))
        for c in f[7]:
            C[(f[0],c[0])] = m.addVar(vtype = GRB.BINARY,name = "conn_"+str(f[0])+"_"+str(c[0]))
        for g in flights.select('*','*','*','*',f[3],'*','*','*'):
            L = [c[2] for c in g[7]]
            if g[1]+g[2]+passenger_delay(f[3]) < f[1] and f[4] in L:
                PR[(g[0],f[0],f[4])] = m.addVar(lb = 0,name = "PR_"+str(g[0])+"_"+str(f[0]))
    for id_f,id_g in connections:
        c = flights.select(id_g,'*','*','*','*','*','*','*')[0][4]
        NP[(id_f,id_g,c)] = m.addVar(lb = 0,name = "NP_"+str(id_f)+"_"+str(id_g))
    p = m.addVar(name = "p")
    m.update()
    m.setObjective(penalty * p +gp.quicksum((D[f[0]][1] - f[1] - f[2])*D[f[0]][3]\
                                            for f in flights),GRB.MINIMIZE)
    for f in flights:
        m.addConstr(D[f[0]][1]-D[f[0]][0],GRB.EQUAL,f[2])
        m.addConstr(D[f[0]][2],GRB.EQUAL,f[5] + PR.sum('*',f[0],'*')- NP.sum('*',f[0],'*'))
        m.addConstr(D[f[0]][2],GRB.LESS_EQUAL,f[6])
        m.addConstr(D[f[0]][3],GRB.EQUAL,f[5] - f[8] + PR.sum('*',f[0],'*'))
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
    
def FlightModel(flights,connections,distrib,omega = 1000):
    m = gp.Model('Flights3')
    penalty = 180
    bigM = 100000
    s=10
    D,PR,NP,C,D2,D3=[],[],[],[],[],[]
    for i in range(omega):
        D.append(gp.tupledict({}))
        PR.append(gp.tupledict({}))
        NP.append(gp.tupledict({}))
        C.append(gp.tupledict({}))
        D2.append(gp.tupledict({}))
        D3.append(gp.tupledict({}))
    for w in range(omega):
        for f in flights:
            D[w][f[0]] = (m.addVar(lb = f[1], ub = curfew(f[3]),name = "Dep"+str(f[0])),\
                m.addVar(lb = f[1]+f[2], ub = curfew(f[4]), name = "Arr"+str(f[0])),\
                m.addVar(name = "Pass"+str(f[0])), m.addVar(name = "_PassEff"+str(f[0])))
            L2 = [m.addVar(vtype = GRB.BINARY,name = "_BinPass"+str(f[0])) for i in range(s)]
            L3 = [m.addVar(lb = 0,name= "_AuxDep"+str(f[0])) for i in range(s)]
            D2[f[0]] = tuple(L2)
            D3[f[0]] = tuple(L3)
            for c in f[7]:
                C[(f[0],c[0])] = m.addVar(vtype = GRB.BINARY,name = "conn_"+str(f[0])+"_"+str(c[0]))
            for g in flights.select('*','*','*','*',f[3],'*','*','*'):
                L = [c[2] for c in g[7]]
                if g[1]+g[2]+passenger_delay(f[3]) < f[1] and f[4] in L:
                    PR[(g[0],f[0],f[4])] = m.addVar(lb = 0,name = "PR_"+str(g[0])+"_"+str(f[0]))
        for id_f,id_g in connections:
            c = flights.select(id_g,'*','*','*','*','*','*','*','*')[0][4]
            NP[(id_f,id_g,c)] = m.addVar(lb = 0,name = "NP_"+str(id_f)+"_"+str(id_g))
        p = m.addVar(name = "p")
    m.update()
    Obj = []
    for f in flights:
        for i in range(s):
            Obj.append((D3[f[0]][i])*(2**i))
    m.setObjective(penalty * p + gp.quicksum(Obj),GRB.MINIMIZE)
    for f in flights:
        m.addConstr(D[f[0]][1]-D[f[0]][0],GRB.EQUAL,f[2],name="1"+str(f))
        m.addConstr(D[f[0]][2],GRB.EQUAL,f[5] + PR.sum('*',f[0],'*')- NP.sum('*',f[0],'*'),name="2"+str(f))
        m.addConstr(D[f[0]][2],GRB.LESS_EQUAL,f[6],name="3"+str(f))
        m.addConstr(D[f[0]][3],GRB.EQUAL,sum(D2[f[0]][i]*(2**i) for i in range(s)),name="4"+str(f))
        m.addConstr(D[f[0]][3],GRB.EQUAL,f[5] - f[8] + PR.sum('*',f[0],'*'),name="5"+str(f))
        for g in flights.select(f[9],'*','*','*','*','*','*','*','*','*'):
            m.addConstr(D[g[0]][0]-D[f[0]][1],GRB.GREATER_EQUAL,turnover(f[4]))
        for c in f[7]:
            m.addConstr(PR.sum(f[0],'*',c[2]),GRB.LESS_EQUAL,NP.sum(f[0],'*',c[2]))
        for i in range(s):
            m.addConstr(D3[f[0]][i],GRB.GREATER_EQUAL,D[f[0]][0] - f[1] - f[2] - bigM*(1-D2[f[0]][i]))
    for id_f, id_g in connections:
        for f in flights.select(id_f,'*','*','*','*','*','*','*','*'):
            b,c,d = f[7].select(id_g,'*','*')[0]
            m.addConstr(D[id_g][0]-D[id_f][1] ,GRB.GREATER_EQUAL,\
                        max(turnover(f[4]),passenger_delay(f[4])) - bigM * C[(id_f,id_g)])
            m.addConstr(NP[(id_f,id_g,d)],GRB.LESS_EQUAL, bigM * C[(id_f,id_g)])
            m.addConstr(NP[(id_f,id_g,d)],GRB.LESS_EQUAL,c)
            m.addConstr(NP[(id_f,id_g,d)],GRB.GREATER_EQUAL,c - (1-C[(id_f,id_g)]) * bigM)
            
            
    m.addConstr(p,GRB.EQUAL,NP.sum('*','*')-PR.sum('*','*')) #Maybe?#
    m.optimize()
    for v in m.getVars():
        if v.VarName[0] != "_":
            print(v.VarName,v.X)
    
def test():
    f = (0,100,500,0,1,50,100,gp.tuplelist([(1,1,2),(2,1,3)]),2,-1)
    g = (1,250,150,1,2,50,100,[],0,-1)
    h = (2,150,150,1,3,50,100,[],0,-1)
    i = (3,650,150,1,2,50,100,[],0,-1)
    L = gp.tuplelist([f,g,h,i])
    F,M = ps.parse_data_Herve("C:/Users/laine/OneDrive/Desktop/Cermics/Re_Data_AirFrance/leg_list.csv")
    F2 = gp.tuplelist([])
    for f in F[3]:
        id = f[-1]
        f[-1] = []
        f.append(0)
        f.append(id)
        F2.append(tuple(f))
    FlightModel(gp.tuplelist(F2),[])
    for i in range(13):
        print(F2[i])
    #FlightModel(L,[(0,1),(0,2)])
    #FlightModelNC(L,[(0,1),(0,2)])
    






    