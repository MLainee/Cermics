/*********************************************
 * OPL 12.8.0.0 Model
 * Author: herve
 * Creation Date: 22 nov. 2018 at 15:44:42
 *********************************************/
 
 /*Flights*/
 tuple Flight{
	key string id;
 	float dur; 
 	float tini; 
 	float a;
 	float b;
 	int nb_pass;
 	int cap;
 	float c_del;
 	float c_roc;
 	string crew;
}
{string} flights_id = {};
{Flight} flights;

// Array that maps a flight's id to the corresponding Flight
Flight map_id_flight[flights_id];

 /*Alternatives flights*/
 // Set of alternatives flights for a given flight
 {string} alternative[f in flights];
 // Set of alternatives which has f as alternative
 {string} has_alternative[f in flights] ;
 // Cost of reassignate passengers on a flight of the same air carrier
 float c_rsc[flights_id][flights_id];
 
 /*Swaps*/
 tuple Swap{
 	key string f;
 	key string fprime;
 	float c; 
 }
 {Swap} swaps;
 // Flight preceding a given flight (from the aircraft's point of view)
 string pred[flights_id];
 
 /*Crew swaps */ 
 tuple Crew{
 	key string id;
 	string first_flight;
 	string last_flight; 
 }
 tuple IndexType1{
	string idx1;
	string idx2;
 }
 {string} crew_id = {};
 // Array that maps a crew id to the corresponding crew tuple
 Crew map_id_crew[crew_id];
 
 // Array that maps a crew id to the set of flights carried out by the crew
 {string} flights_crew[crew_id];
 // Set of pairs of crews that can be swapped
 {IndexType1} crew_swaps = {};
 int sigma[flights_id];
 int theta[swaps];
 
 // Set of pairs of flights that must be deleted together 
{IndexType1} FF = {};

 /*Maintenances*/
 tuple Maint{
	key string id;
 	float dur;
 	float tini;
 	float a;
 	float b; 
 	float c;
 }
{string} maints_id = {};
{Maint} maints;
//Array that maps a maintenance's id to the corresponding Maint
Maint map_id_maint[maints_id];

 /*Arcs*/ 
 tuple PlainArc{
 	string f;
 	string g;
 	float dfg;
 }
 tuple PassengerArc{
 	key string f;
 	key string g;
 	float dfg;
 	int nb_pass;
 }
 tuple ReverseArc{
  	key string f;
 	key string g;
 	float dfg;
 	float c;
 }
 tuple MaintArcIn{
 	string f;
 	string m; 
 	float dfm;
 }
 tuple MaintArcOut{
 	string m;
 	string f; 
 }
 {PassengerArc} passengers_arcs = {}; 
 {ReverseArc} reverse_arcs = {};
 {ReverseArc} reverse_arcs_crew = {};
 {MaintArcIn} maint_arcs_in = {};
 {MaintArcOut} maint_arcs_out = {}; 
 {PlainArc} ground_service_arcs = {};
 {PlainArc} crew_transit_arcs = {}; 
 {PlainArc} crew_rest_arcs = {};
 
 // Array that maps 2 flights' id to the corresponding reverse arc
 ReverseArc map_fg_reversearcs[flights_id][flights_id];

 /*Big constant */
 int K = maxint;
 
 /*Dummy parameters*/	
// Helps with the construction of alternatives and has_alternative
{IndexType1} alternative_set = {}; 
// Helps with the construction of map_id_crew
{Crew} crews_temp = {};

//Limitations
int max_reserve_crew = 0;
int max_deleted_flights = 3;
int max_swapped_flights = 2;
 execute{
	var f=new IloOplInputFile("Instances/instance_generated_400_20_2H.csv");
//	var f = new IloOplInputFile("Instances/instance_AF_2018-08-05_2H.csv")
	var str=f.readline();
	var ar=str.split(",");
	
	// First line : metadata
	var nb_flights = Opl.intValue(ar[0]);
	var nb_swaps = Opl.intValue(ar[1]);
	var nb_crew_rotation = Opl.intValue(ar[2]); 
	var nb_ff = Opl.intValue(ar[3]);
	var nb_maints = Opl.intValue(ar[4]);
	var nb_passengers_arcs = Opl.intValue(ar[5]);
	var nb_reverse_arcs_crew = Opl.intValue(ar[6]);
	var nb_maint_arcs_in = Opl.intValue(ar[7]);
	var nb_maint_arcs_out = Opl.intValue(ar[8]);
	var nb_ground_service_arcs = Opl.intValue(ar[9]);
	var nb_crew_transit_arcs = Opl.intValue(ar[10]);
	// Flights
	for(var i = 0; i < nb_flights; i++){
		str = f.readline();
		ar = str.split(",");
		flights_id.add(ar[0]);
		flights.add(ar[0],Opl.intValue(ar[1]),Opl.intValue(ar[2]),Opl.intValue(ar[3]),
		Opl.intValue(ar[4]),Opl.intValue(ar[5]),Opl.intValue(ar[6]),Opl.intValue(ar[7]),
		Opl.intValue(ar[8]),ar[9]);
		for(var j = 10; j < ar.length; j++){
			alternative_set.add(ar[0],ar[j]);		
		}
	}
	// Construction of map_id_flight 
	for(var id in flights_id){
		map_id_flight[id] = flights.get(id);	
	}
	// Construction of alternative and has_alternative
	for(var alter in alternative_set){
		if(alter.idx2 != ""){	
			alternative[map_id_flight[alter.idx1]].add(alter.idx2);
			has_alternative[map_id_flight[alter.idx2]].add(alter.idx1);		
		}
	}
	// Construction of c_rsc 
	for(var id_f in flights_id){
		for(var id_fprime in alternative[map_id_flight[id_f]]){
			// We use the positive part of f.tini - fprime.tini 
			if(map_id_flight[id_fprime].tini - map_id_flight[id_f].tini >= 0){
				c_rsc[id_f][id_fprime] = map_id_flight[id_fprime].tini - map_id_flight[id_f].tini;			
				writeln(c_rsc[id_f][id_fprime]);
			}		
			else{
				c_rsc[id_f][id_fprime] = 0;		
			}
		}
	}
	// Construction of swaps
	for(var i = 0; i < nb_swaps; i++){
		str = f.readline();
		ar = str.split(",");
		swaps.add(ar[0],ar[1],Opl.floatValue(ar[2]));	
	}
	// Construction of crew_id on the basis of the attribute crew of flights
	for(var flight in flights){
		crew_id.add(flight.crew);	
	}
	// Construction of flights_crew 
	for(var flight in flights){
		flights_crew[flight.crew].add(flight.id);	
	}
	// Construction of map_id_crew 
	for(var i = 0; i < nb_crew_rotation; i++){
		str = f.readline();
		ar = str.split(",");
		crews_temp.add(ar[0],ar[1],ar[2]);
		map_id_crew[ar[0]] = crews_temp.get(ar[0]);
	}
	//Construction of FF
	for(var i = 0; i < nb_ff; i++){
		str = f.readline();
		ar = str.split(",");
		FF.add(ar[0],ar[1]);	
	}
	//Maintenances
	for(var i = 0; i < nb_maints; i++){
		str = f.readline();
		ar = str.split(",");
		maints_id.add(ar[0]);
		maints.add(ar[0],Opl.intValue(ar[1]),Opl.intValue(ar[2]),Opl.intValue(ar[3]),
		Opl.intValue(ar[4]),Opl.intValue(ar[5]));
	}
	//Construction of map_id_maint
	for(var id in maints_id){
		map_id_maint[id] = maints.get(id);	
	}
	//Arcs 
	for(var i = 0; i < nb_passengers_arcs; i++){
		str = f.readline();
		ar = str.split(",");
		passengers_arcs.add(ar[0],ar[1],Opl.floatValue(ar[2]),Opl.intValue(ar[3]));
	}	
	for(var i = 0; i < nb_reverse_arcs_crew; i++){
		str = f.readline();
		ar = str.split(",");
		reverse_arcs_crew.add(ar[0],ar[1],Opl.intValue(ar[2]),Opl.intValue(ar[3]));	
		map_fg_reversearcs[ar[0]][ar[1]] = reverse_arcs_crew.get(ar[0],ar[1]);	
	}
	for(var i = 0; i < nb_maint_arcs_in; i++){
		str = f.readline();
		ar = str.split(",");
		maint_arcs_in.add(ar[0],ar[1],Opl.floatValue(ar[2]));		
	}
	for(var i = 0; i < nb_maint_arcs_out; i++){
		str = f.readline();
		ar = str.split(",");
		maint_arcs_out.add(ar[0],ar[1]);		
	}
	for(var i = 0; i < nb_ground_service_arcs; i++){
		str = f.readline();
		ar = str.split(",");
		ground_service_arcs.add(ar[0],ar[1],Opl.floatValue(ar[2]));	
		pred[ar[1]] = ar[0];
	}
	for(var i = 0; i < nb_crew_transit_arcs; i++){
		str = f.readline();
		ar = str.split(",");
		crew_transit_arcs.add(ar[0],ar[1],Opl.floatValue(ar[2]));
	}
	//Construction of theta and crew_swaps on the basis of swaps 
	for(var swap in swaps){	
		var crew_change_f = false;
		var crew_change_fprime = false; 
		for(var arc in crew_transit_arcs){
			//sigma[f] = 0 if a crew transit arc arrives on f or if f is the first flight of a crew rotation
			if(arc.g == swap.f || map_id_crew[map_id_flight[swap.f].crew].first_flight == swap.f){
				crew_change_f = true;	
				sigma[swap.f] = 0;			
			}
			if(arc.g == swap.fprime || map_id_crew[map_id_flight[swap.fprime].crew].first_flight == swap.fprime){
				crew_change_fprime = true;	
				sigma[swap.fprime] = 0;		
			}		
		}
		if(!crew_change_f){
		   sigma[swap.f] = 1;		
		}
		if(!crew_change_fprime){
		   sigma[swap.fprime] = 1;  		
		}
		theta[swap] = sigma[swap.f] + sigma[swap.fprime] - sigma[swap.f]*sigma[swap.fprime];
		crew_swaps.add(map_id_flight[swap.f].crew,map_id_flight[swap.fprime].crew);
		//We make sure that if (c,c') is in crew_swaps then (c',c) isn't on crew_swaps
		crew_swaps.remove(map_id_flight[swap.fprime].crew,map_id_flight[swap.f].crew);
	}
	f.close(); 
 }
//// 
 /* Variables */
 dvar float dt_f[flights];
 dvar float dt_m[maints];
 dvar float at[flights];
 dvar int gamma[flights] in 0..1;
 dvar int x[swaps] in 0..1;
 dvar int r[reverse_arcs_crew] in 0..1;
 dvar int z[passengers_arcs] in 0..1;
 dvar float+ y[flights];
 dvar float ct[passengers_arcs];
 dvar float+ pr[flights_id][flights_id];
 dvar int+ nr[flights];
 dvar int delta[crew_swaps] in 0..1;
 dvar float+ kappa[passengers_arcs];
 
/*Objective function */
 minimize sum(f in flights) (y[f]) + sum(m in maints) m.c * (dt_m[m] - m.tini) 
 + sum(f in flights)sum(fprime in alternative[f])c_rsc[f.id][fprime]*pr[f.id][fprime] 
 + sum(f in flights)f.c_roc*nr[f];
 
 /*Constraints*/ 
 constraints{
 	// Precedence constraints
 	forall(f in flights) 
 		at[f] - dt_f[f] == f.dur*(1-gamma[f]);
 	forall(<f,g,dfg> in ground_service_arcs)
 	  	dt_f[map_id_flight[g]] - at[map_id_flight[f]] >= dfg - 
 	  	K*(gamma[map_id_flight[f]]+gamma[map_id_flight[g]]
 	  	+sum(fg in swaps : fg.f == g || fg.fprime == g)x[fg]);
 	forall(<f,g,dfg> in crew_transit_arcs)
 	  	dt_f[map_id_flight[g]] - at[map_id_flight[f]] >= dfg
 	  	-K*(gamma[map_id_flight[f]] + gamma[map_id_flight[g]]
 	  	+sum(fg in swaps : fg.f == g)sigma[fg.fprime]*x[fg]
 	  	+sum(fg in swaps : fg.fprime == g)sigma[fg.f]*x[fg]); 
 	forall(fg in crew_rest_arcs)	
 	  	dt_f[map_id_flight[fg.g]] - at[map_id_flight[fg.f]] >= fg.dfg 
 	  	- K*(gamma[map_id_flight[fg.f]] + gamma[map_id_flight[fg.g]]);
 	forall(fg in passengers_arcs)
 	  	dt_f[map_id_flight[fg.g]] - at[map_id_flight[fg.f]] >= fg.dfg - K*z[fg];
 	forall(<f,m,dfm> in maint_arcs_in)
 	  	dt_m[map_id_maint[m]] - at[map_id_flight[f]] >= dfm;
 	forall(<m,f> in maint_arcs_out)
 	  	dt_f[map_id_flight[f]] - dt_m[map_id_maint[m]] >= map_id_maint[m].dur 
 	  	- K*(gamma[map_id_flight[f]]+sum(fg in swaps : fg.f == f || fg.fprime == f)x[fg]);  	
 	forall(fg in reverse_arcs)
 	  	dt_f[map_id_flight[fg.g]] - at[map_id_flight[fg.f]] >= -fg.dfg - K*(gamma[map_id_flight[fg.f]]+gamma[map_id_flight[fg.g]]
 	  	+ sum(swap in crew_swaps : swap.idx1 == map_id_flight[fg.f].crew || swap.idx2 == map_id_flight[fg.f].crew) delta[swap]);
 	forall(fg in reverse_arcs_crew)
 	  	dt_f[map_id_flight[fg.g]] - at[map_id_flight[fg.f]] >= -fg.dfg - K*(r[fg]+gamma[map_id_flight[fg.f]]
 	  	+ gamma[map_id_flight[fg.g]] + sum(swap in crew_swaps : swap.idx1 == map_id_flight[fg.f].crew || swap.idx2 == map_id_flight[fg.f].crew) delta[swap]);
 	// Deletion constraints
 	forall(fg in passengers_arcs)
 	  	2*z[fg] >= gamma[map_id_flight[fg.f]] + gamma[map_id_flight[fg.g]];
 	forall(ff in FF)
 	    gamma[map_id_flight[ff.idx1]] == gamma[map_id_flight[ff.idx2]];
 	forall(f in flights)
 	  forall(fm in maint_arcs_in: fm.f == f.id)
 	    gamma[f] == 0;
 	// Aircraft swap constraints
 	forall(fg in ground_service_arcs)
 	  	forall(swap in swaps:swap.f == fg.g)
	 	  	dt_f[map_id_flight[swap.fprime]] - at[map_id_flight[fg.f]] >= fg.dfg - K*(1-x[swap]);
	forall(fg in ground_service_arcs)
 	  	forall(swap in swaps:swap.fprime == fg.g)
	 	  	dt_f[map_id_flight[swap.f]] - at[map_id_flight[fg.f]] >= fg.dfg - K*(1-x[swap]);
 	forall(<m,f> in maint_arcs_out)
 	  	forall(swap in swaps : swap.f ==f)
 	  	  dt_f[map_id_flight[swap.fprime]] - dt_m[map_id_maint[m]] >= map_id_maint[m].dur - K*(1-x[swap]);
 	forall(<m,f> in maint_arcs_out)
 	  	forall(swap in swaps : swap.fprime == f)
 	  	  dt_f[map_id_flight[swap.f]] - dt_m[map_id_maint[m]] >= map_id_maint[m].dur - K*(1-x[swap]); 	  
 	forall(f in flights)
 	  	1 >= gamma[f] + sum(fg in swaps : fg.f == f.id || fg.fprime == f.id)x[fg];
 	// Crew swap constraints
 	forall(swap in crew_swaps)
 	  	delta[swap] == sum(g in flights_crew[swap.idx1])sum(gprime in flights_crew[swap.idx2])
 	  	sum(fg in swaps : (fg.f == g && fg.fprime == gprime) || (fg.f == gprime && fg.fprime == g))
 	  	theta[fg]*x[fg];
 	forall(c in crew_id)
 	  	1 >= sum(swap in crew_swaps : swap.idx1 == c || swap.idx2 == c) delta[swap];
 	forall(swap in crew_swaps)
 	  	dt_f[map_id_flight[map_id_crew[swap.idx2].first_flight]] - at[map_id_flight[map_id_crew[swap.idx1].last_flight]]
 		>= -map_fg_reversearcs[map_id_crew[swap.idx1].last_flight][map_id_crew[swap.idx1].first_flight].dfg
 			-K*(1-delta[swap]);
 	forall(swap in crew_swaps)
 	  	dt_f[map_id_flight[map_id_crew[swap.idx1].first_flight]] - at[map_id_flight[map_id_crew[swap.idx2].last_flight]]
 		>= -map_fg_reversearcs[map_id_crew[swap.idx2].last_flight][map_id_crew[swap.idx2].first_flight].dfg
 			-K*(1-delta[swap]); 
 	forall(<f,g,dfg> in crew_transit_arcs)
 	  	forall(swap in swaps : swap.f == g)
 	  	   dt_f[map_id_flight[swap.fprime]] - dt_f[map_id_flight[f]] >= dfg - K*(1-sigma[swap.fprime]*x[swap]);
 	forall(<f,g,dfg> in crew_transit_arcs)
 	  	forall(swap in swaps : swap.fprime == g)
 	  	   dt_f[map_id_flight[swap.f]] - dt_f[map_id_flight[f]] >= dfg - K*(1-sigma[swap.f]*x[swap]);  	   
 	// Constraints on the reassignement of passengers
 	forall(f in flights)
 	    K*(1-gamma[f]) >= sum(g in has_alternative[f])pr[g][f.id];
 	forall(f in flights)
 	  	sum(fprime in alternative[f])pr[f.id][fprime] + nr[f] == f.nb_pass*gamma[f] 
 	  	+ sum(fg in passengers_arcs:fg.g == f.id) fg.nb_pass*(z[fg] - gamma[map_id_flight[fg.f]]);  
 	forall(f in flights)
 	 	f.cap >= sum(g in has_alternative[f])pr[g][f.id] + f.nb_pass + sum(fg in passengers_arcs:fg.g == f.id) fg.nb_pass*(1-z[fg]);
 	// Passengers cost function 
 	forall(fg in passengers_arcs)
 	  	ct[fg] >= at[map_id_flight[fg.f]]+fg.dfg;
 	forall(fg in passengers_arcs)
 	  	ct[fg] >= map_id_flight[fg.g].tini;
 	forall(fg in passengers_arcs)
 	  	kappa[fg] >= fg.nb_pass*(dt_f[map_id_flight[fg.g]]-ct[fg])
					- K*gamma[map_id_flight[fg.f]];
 	forall(f in flights)
  		y[f] >= f.nb_pass*(dt_f[f]-f.tini) 
  		+ sum(fg in passengers_arcs : fg.g == f.id) kappa[fg]; 
  	//Definition domain
 	forall(f in flights)	
 	  	dt_f[f] >= f.a*(1-gamma[f]);	
 	forall(f in flights)
 	  	dt_f[f] <= f.b*(1-gamma[f]); 	 
 	forall(m in maints)
 	  	dt_m[m] >= m.a;
 	forall(m in maints)
 	  	dt_m[m] <= m.b;
 	//Limitations constraints
 	sum(fg in reverse_arcs_crew)r[fg] <= max_reserve_crew;
 	sum(f in flights)gamma[f] <= max_deleted_flights;
 	sum(fg in swaps)x[fg] <= max_swapped_flights;
 	
 }
 /*Output*/
 execute{
// 	var f=new IloOplOutputFile("Outputs/export_05-08-2018_2H.csv");
    var f=new IloOplOutputFile("Outputs/export_400_20_2H.csv");
    var nb_delayed_flights = 0;
    var mean_delay_flight = 0;
    var nb_del = 0; 
    var nb_delayed_maints = 0;
    var mean_delay_maint = 0; 
    var nb_swaps = 0;
    var nb_missconnection = 0;
    var nb_reassigned_passengers = 0;
    var nb_notreassigned_passengers = 0;
    var nb_reserve_crew = 0;

    
    for(var fl in flights)
    {
    	if(dt_f[fl] - fl.tini > Math.pow(10,-1) ){
    		nb_delayed_flights = nb_delayed_flights + 1;    
    		mean_delay_flight = mean_delay_flight + dt_f[fl] - fl.tini;	
    		f.writeln(fl.id," retarde",Math.round(dt_f[fl]-fl.tini));
    	}
    	if(gamma[fl] == 1){
    		nb_del = nb_del + 1;   
    		f.writeln(fl.id," supprime");	
    	}
    	nb_notreassigned_passengers = nb_notreassigned_passengers + nr[fl];
    }
    for(var maint in maints)
    {
    	if(dt_m[maint] - maint.tini > Math.pow(10,-1)){
    		nb_delayed_maints = nb_delayed_maints + 1;  
    		mean_delay_maint = mean_delay_maint + dt_m[maint] - maint.tini;  	
    	}    
    }
    for(var swap in swaps)
    {
    	nb_swaps = nb_swaps + x[swap];   	
    }
    for(var fg in passengers_arcs)
    {
		nb_missconnection = nb_missconnection + z[fg];    	
    }
    for(var f1 in flights_id){
    	for(var f2 in flights_id){
    		 nb_reassigned_passengers = nb_reassigned_passengers + pr[f1][f2];
    	}    
    }
    for(fg in reverse_arcs_crew){
    	nb_reserve_crew = nb_reserve_crew + r[fg];    
    }
    f.writeln("Nombre de vols retardes : ", nb_delayed_flights);
    f.writeln("Retard moyen : ", mean_delay_flight/nb_delayed_flights);
    f.writeln("Nombre de vols supprimes : ", nb_del);
    f.writeln("Nombre de maintenances retardes : ", nb_delayed_maints);
    f.writeln("Retard moyen : ", mean_delay_maint/nb_delayed_maints);
    f.writeln("Nombre de swaps : ", nb_swaps);
    f.writeln("Nombre de correspondances ratees : ",nb_missconnection);
    f.writeln("Nombre de passagers reaffectes : ", nb_reassigned_passengers);
    f.writeln("Nombre de passagers non reaffectes : ", nb_notreassigned_passengers);
    f.writeln("Nombre de recours à un equipage de reserve : ", nb_reserve_crew);
    f.close();   	
 } 
 