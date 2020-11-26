# -*- coding: utf-8 -*-


def parse_data_Herve(filename):
    f = open(filename,'r')
    lines = f.read().splitlines()
    flights, maintenances = [] , []
    for i in range(1,len(lines)):
        line = lines[i].split(';' )       
        flight = []
        flight.append(line[2][1:-1]+str(i)) #plane ID
        D,A = line[-2],line[-1]
        d = 36000 * int(D[12]) + 3600 * int(D[13]) + 600 * int(D[15])+ 60 * int(D[16])\
            + 10* int(D[18]) + int(D[19])
        a = 36000 * int(A[12]) + 3600 * int(A[13]) + 600 * int(A[15])+ 60 * int(A[16])\
            + 10* int(A[18]) + int(A[19])
        flight.append(int(d/60)) #departure time, minutes from midnight
        flight.append(int((a-d)/60)) #duration, minutes
        flight.append(line[3][1:-2]) #departure airport
        flight.append(line[4][1:-2]) #arrival airport
        flight.append(0) #passenger TBD
        flight.append(0) #capacity TBD
        
        flight.append(D[10]) #day ID
        if line[1][1] == "L":
            flights.append(flight)            
        else:
            maintenances.append(flight)
    flights.sort(key = lambda tup: tup[1])
    F=[[]for i in range(7)]
    print(F)
    for f in flights:
        f[-3],f[-2] = 50,100
        if f[-1]  == '0':
            F[0].append(f[:-1])
        else:
            F[int(f[-1])-3].append(f[:-1])
    for Day in F:
        print(len(Day))
        for i in range(len(Day)):
            id = Day[i][0][0:5]
            Day[i].append(-1)
            for j in range(i+1,len(Day)):
                if Day[j][0][0:5] == id:
                    Day[i][-1] = Day[j][0]
                    break
    M=[[]for i in range(7)]
    for m in maintenances:
        if m[-1]  == 0:
            M[0].append(m[:-1])
        else:
            M[int(m[-1])-3].append(m[:-1])
    return F,M
        
    




