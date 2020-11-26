import random 
"""
    Parameters used by generate_legs 
"""

random.seed(42)

flights_nb = 800
maints_nb = 40

min_legs_aircraft = 1
max_legs_aircraft = 8 

min_flights_crew = 1
max_flights_crew = 5 

hub = "CDG"
others_airports = ["AJA","ALG","AMS","ARN","ATH","BES","BGO","BHX","BLQ","BOD","BRI","BUD",
                    "CMN","CPH","CTA","DBV","DUB","FSC","GVA","HAM","IBZ","LED","LHR","LIS",
                    "LYS","MAD","MAN","MPL","MRS","MUC","MXP","NAP","NCE","NTE","OPO", "ORN",
                    "OTP","PRG","RBA","SOF","SVO","TLS","TUN","VCE","VIE","WAW", "ZAG", "ZRH"]

min_dep_time = 1*60
max_dep_time = 8*60

flight_duration_min = 60
flight_duration_max = 4*60 

times_dic = {hub:{}}
for airport in others_airports:
    times_dic[airport] = {hub:random.randint(flight_duration_min,flight_duration_max)}
    times_dic[hub][airport] = times_dic[airport][hub]

maint_duration_min = 3*60
maint_duration_max = 10*60

ground_time_min = 30
ground_time_max = 70

max_interflights_time_crew = 120