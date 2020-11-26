# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 12:51:37 2020

@author: laine
"""
import pandas as pd
import numpy as np
import scipy.stats as st

def getdate(s):
    return s[-5:]

def getname(s):
    return s[0:5]

def makebool(b):
    return bool(int(b))

def gethyper(N,m,v):
    a = - N
    b = m*N + N*N - m/(N*(N-1)*v)
    c = - m*N*N
    D = b*b - 4*a*c
    x1,x2 = (-b+np.sqrt(D))/(2*a),(-b-np.sqrt(D))/(2*a)
    n1,n2 = m*N/x1,m*N/x2
    return x1,x2,n1,n2

def mins(time):
    m = 600 * int(time[0]) + 60 * int(time[1]) + 10 * int(time[3]) + int(time[4])
    if m > 24 * 60:
        print("invalid time")
        return (-1)
    return m

def time(mins):
    d = mins//(60*24)
    h,m = str((mins-(d*60*24)) // 60) , str(mins % 60)
    if len(h) == 1:
        h = '0'+h
    if len(m) == 1:
        m = '0'+m
    if d>0:
        print("Time is",d,"days from start")
    return h + ':' + m

def capacity(Plane):
    if Plane == '320':
        return 200
    if Plane == '321':
        return 230
    if Plane == '319':
        return 160
    if Plane == '318':
        return 140
    if Plane == '772':
        return 380
    if Plane =='77W':
        return 470
    if Plane == '332':
        return 250
    if Plane == '32A':
        return 210
    if Plane =='388':
        return 853
    if Plane =='343':
        return 290
    if Plane == '789':
        return 330
    
def longhaul(Plane):
    if Plane[0:2] == '31' or Plane[0:2] == '32':
        return 0
    return 1

def delay(row):
    return row['Arv_delay'] - row['Prev_delay'] #+ max(0,row['Tat_sch']-row['Tat_fnl'])

def parseflights():  
    a = "C:/Users/laine/OneDrive/Desktop/Cermics/altea_karma.csv"
    b = "C:/Users/laine/OneDrive/Desktop/Cermics/PONCTU_extract.csv"
    df = pd.read_csv(a,sep = ';') 
    df.rename(columns={'flight_number':'Flight','departure_airport' : 'Dpt',\
            'departure_date_utc_sc':'Date','nb_paxs_total':'Pass'},inplace = True)
    P = df[df['airline_code'] == 'AF'].groupby(by = ['Flight','Date','Dpt']).sum()
    PP = df[df['type_pax'] == 'cnt']
    P_cnt = PP[PP['airline_code'] == 'AF'].groupby(by = ['Flight','Date','Dpt']).sum()
    P.drop(['Unnamed: 0','operational_capacity','physical_capacity'],axis = 1, inplace=True)
    P_cnt.drop(['Unnamed: 0','operational_capacity','physical_capacity'],axis = 1, inplace=True)
    P_cnt.rename(columns={'Pass':'Cnt_pass'},inplace = True)
    P1 = pd.concat([P,P_cnt],axis = 1)
    P1.fillna(0,inplace=True)
    df = pd.read_csv(b,sep = ';')
    df['Dpt_time'] = df['DPT_DATETIME_UTC_SCH'].apply(getdate)
    df['Capacity'] = df['ARCFT_TYPE'].apply(capacity)
    df['Long_haul'] = df['ARCFT_TYPE'].apply(longhaul)
    df.drop(['Unnamed: 0','ARCFT_TYPE','ARV_DATE_UTC_SCH','DPT_DATE_LOC_SCH','DPT_TIME_LOC_SCH',\
             'ARV_DATE_LOC_SCH','ARV_TIME_LOC_SCH','HAUL_TYP','DPT_COUNTRY','ARV_COUNTRY',\
             'DPT_DATETIME_UTC_SCH','ARV_DATETIME_UTC_SCH','DPT_DATETIME_LOC_SCH',\
             'DPT_DATETIME_LOC_FNL','ARV_DATETIME_LOC_SCH'],axis = 1,inplace = True)
    df.rename(columns={'ARV_ARPT_SCH':'Arv','DPT_ARPT_SCH':'Dpt','IMMAT':'Plane',\
             'FLIGHT':'Flight','DPT_DATE_UTC_SCH':'Date','ARV_TIME_UTC_SCH':'Arv_time',\
             'DPT_DELAY':'Dpt_delay','ARV_DELAY':'Arv_delay','ARV_DELAY_PREV' : 'Prev_delay',\
             'TAT_SCH_SCH':'Tat_sch','TAT_FNL_SCH':'Tat_fnl','FIRST_FLIGHT':'First_flight',\
              'TTM':'Min_tat'},inplace=True)
    df['First_flight'] = df['First_flight'].apply(makebool)
    df['Plane'] = df['Plane'].apply(getname)
    df['Primary_delay'] = df.apply(lambda row: delay(row), axis = 1)
    cols = df.columns.tolist()
    cols = cols[1:2]+cols[0:1]+cols[2:5]+cols[-2:-1]+cols[5:-2]+cols[-1:]
    df = df[cols]
    df.set_index(['Flight','Date','Dpt'],drop=False,inplace = True)
    DF = pd.merge(df,P1,how = 'left',right_index=True, left_index = True)
    DF.rename_axis(index=['Fl','D','Dp'],inplace=True)
    
    return DF

def Airport_means():
    T =parseflights()
    DPT = T.groupby('Dpt').mean()
    ARV = T.groupby('Arv').mean()
    return DPT,ARV

def Schedule_day(Day):
    T = parseflights()
    S = T[T['Date']== Day]
    L=[]
    for P in S.Plane.unique():
        l=[]
        for i in range(len(S)):
            if S.iloc[i].Plane == P:
                l.append(S.iloc[i])
        L.append(l)
    return L



def Airport_pairs():
    T = parseflights()[['Dpt','Arv','Tat_sch','Pass','Cnt_pass']].reset_index(drop = True)
    M = T.groupby(['Dpt','Arv']).mean()
    V = T.groupby(['Dpt','Arv']).var()
    C = T.groupby(['Dpt','Arv']).count()
    C.drop(['Tat_sch','Cnt_pass'],axis = 1,inplace = True,)
    C.rename(columns= {'Pass':'Count'},inplace = True)
    M.rename(columns = {'Tat_sch':'Tat_sch_mean','Pass':'Pass_mean','Cnt_pass'\
                        :'Cnt_pass_mean'},inplace = True)
    V.rename(columns = {'Tat_sch':'Tat_sch_var','Pass':'Pass_var','Cnt_pass'\
                        :'Cnt_pass_var'},inplace = True)
    T0 = pd.merge(M,V,how='left',right_index=True,left_index=True)
    T = pd.merge(T0,C,how='left',right_index=True,left_index=True)
    return T
    

def Delay_distrib():
    T = parseflights()
    CDG,ORY,LH,MH = [],[],[],[]
    for i in range(len(T)):
        if T.iloc[i]['Dpt']=='CDG':
            CDG.append(T.iloc[i]['Primary_delay'])
        elif T.iloc[i]['Dpt']=='ORY':
            ORY.append(T.iloc[i]['Primary_delay'])
        elif T.iloc[i]['Long_haul']:
            LH.append(T.iloc[i]['Primary_delay'])
        else:
            MH.append(T.iloc[i]['Primary_delay'])
    L = [CDG,ORY,LH,MH]
    for l in L:
        n = len(l)
        for i in range(n):
            if abs(l[n-i-1]) > 120:
                l.remove(l[n-i-1])
    M = [np.mean(L[i]) for i in range(4)]
    S = [np.std(L[i]) for i in range(4)]
    return M,S

def Pass_distrib():
    T = parseflights()
    S = T[['Capacity','Pass','Cnt_pass']]
    R = S.drop(S[S['Pass']>S['Capacity']].index)
    M = R.groupby('Capacity').mean()[['Pass','Cnt_pass']]
    V = R.groupby('Capacity').var()[['Pass','Cnt_pass']]
    T = pd.merge(M,V,how='left',right_index=True,left_index=True)
    T.reset_index(inplace = True)
    return T


def Airport_type():
    T = parseflights()[['Dpt','Long_haul']]
    M = T.groupby(['Dpt']).mean()
    M.reset_index(inplace = True)
    return M

def Test():
    T = parseflights()
    T.hist(column = 'Primary_delay',bins = 81, range = [-120,120])
    return T[T['Primary_delay']<-50]
    
    
    
        