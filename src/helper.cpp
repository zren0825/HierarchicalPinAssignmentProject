/* EE201A Winter 2018 Course Project
 */

#include <iostream>
#include <fstream>
#include <sys/wait.h>

#include <vector>
#include <string>
#include <set>
#include "oaDesignDB.h"
#include "ProjectInputRules.h"
#include "OAHelper.h"
#include "helper.h"

#include <string.h>
#include <boost/algorithm/string.hpp>

using namespace oa;
using namespace std;

/* write design information to a file and open with python scripts
*/
void dumpDesignInfoFile(ProjectInputRules inputRules, oaBlock* block, oaNativeNS ns ){
	// obtain input rule information
	int pin_layer = inputRules.getPinLayer();
	int min_routing_layer = inputRules.getMinRoutingLayer();
	int max_routing_layer = inputRules.getMaxRoutingLayer();
	float pin_movement_step_size = inputRules.getPinMoveStep();
	float min_pin_pitch = inputRules.getMinPinPitch();
	float max_perturbation = inputRules.getMaxPinPerturbation();

	// Open a file 
	ofstream f;	
	f.open("/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/design_info.txt");
	// Write global info on the top 
	//f << "pinLayer\t" << pin_layer << '\n';
	//f << "minRoutingLayer\t" << min_routing_layer << '\n';
	//f << "maxRoutingLayer\t" << max_routing_layer << '\n';
	f << "pinMovement\t" << pin_movement_step_size << '\n';
	f << "minPinPitch\t" << min_pin_pitch << '\n';
	f << "maxPerturbation\t" << max_perturbation << '\n';
	// Separation
	f << "*\n";

	// Macro Information in the dump file 
	oaString macro_name, macro_type;
	oaBox macro_box;
	oaPoint origin;
	oaIter<oaInst> InstIterator(block->getInsts());
	while(oaInst* inst = InstIterator.getNext())
	{
		// Macro Indicator
		f << "Macro\n";
		inst->getName(ns, macro_name);
		inst->getCellName(ns, macro_type);
		inst->getBBox(macro_box);
		inst->getOrigin(origin);
		f <<  macro_name << '\t' << macro_type << '\t' << macro_box.upperRight().x() << '\t' << macro_box.upperRight().y() << '\t' << macro_box.lowerLeft().x() << '\t' << macro_box.lowerLeft().y() << '\t' << origin.x() << '\t' << origin.y() <<endl;

		oaString instTerm_name, instTerm_net_name;
		oaIter<oaInstTerm> InstTermIterator(inst->getInstTerms());
		while(oaInstTerm* instTerm = InstTermIterator.getNext())
		{
			instTerm->getTermName(ns, instTerm_name);
			// Excluding VDD and VSS instTerms
			if((instTerm_name != "VDD") && (instTerm_name != "VSS"))
			{
				// InstTerm Indicator
				f << "T\t";
				f << instTerm_name << '\t' << "1\t";
				if((instTerm->getNet()) == NULL)
				{
					f << "NONE\t";
				}
				else
				{
					instTerm->getNet()->getName(ns, instTerm_net_name);
					f << instTerm_net_name << '\t';
				}
				oaPoint instTerm_position = OAHelper::GetAbsoluteInstTermPosition(instTerm);
				//oaPoint instTerm_position = OAHelper::GetTermPosition(instTerm);
				f << instTerm_position.x() << '\t' << instTerm_position.y() << '\n';
			}
		}
		// End to a macro Indicator
		f << "end\n";	
	}
	// Net Information in the dump file
		oaString net_name, net_instTerm_name;
		oaIter<oaNet> netIterator(block->getNets());
		while(oaNet* net = netIterator.getNext())
		{
			if((net->getTerms().getCount() == 0) && (net->getInstTerms().getCount() > 0))
			{
				net->getName(ns, net_name);
				if((net_name != "VDD") && (net_name != "VSS"))
				{
					f << "Net\n";
					f << net_name << '\n';
					oaIter<oaInstTerm> instTermIterator(net->getInstTerms());
					while(oaInstTerm* instTerm = instTermIterator.getNext())
					{
						instTerm->getTermName(ns, net_instTerm_name);
						oaPoint net_instTerm_position = OAHelper::GetAbsoluteInstTermPosition(instTerm);
						f << "T\t" << net_instTerm_name << '\t' << "1\t" << net_name << '\t' << net_instTerm_position.x() << '\t' << net_instTerm_position.y() << '\n';
					}	
					f << "end\n";
				}
			}
		}
	
		f.close();	
	}

/* create new process -> call python scripts to make pin placement decision, 
   meanwhile c++ waits untill the DecisionMade file indicator -> kill process -> return to c++ process  
*/
void callCplexSolver(){
// Create child process and let the parent process to wait for the child process to finish
	pid_t PID = 0;
	// Check the status of the child process
	int status;
	// Create a new process
	cout << "Before PID." << endl;
	PID = fork();
	cout << "After PID." << endl;
	// If child process, call python script
	if(PID == 0)
	{
		cout << "Python started." << endl;
		execl("/bin/sh", "sh", "-c", "python /w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/src/Python/solver.py", NULL);
	}
	else // Parent process waiting for cplex python script to complete
	{
		waitpid(PID, &status, 0);
		// Wait for the solution .txt file dumped by Python side
		ifstream decisionMade("/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/DecisionsMade.txt");
		while(!decisionMade.is_open())
		{
			//cout << "Can't find python.txt" << endl;
		}
		decisionMade.close();
		
		//cout << "python.txt exists now" << endl;
	}
	cout << "Decision File Ready!" << endl;
}

/* Function to read decision output file from Python 
   save and return as a nested map: macro_name -> map(term_name->new_location) 
*/
//vector<pair<string, vector<string, pair<int, int> > > >readDecisionFile(string filename){
map<string, map<string, pair<int, int> > > readDecisionFile(string filename){
	//string filename = "/w/class.2/ee/ee201a/zhengshu/project/project_W18_v1/pin_assignment_decision.txt";
	ifstream infile(filename.c_str());
		
	//vector<pair<string, vector<string, pair<int, int> > > > decision_map;
	//pair<string, vector<string, pair<int, int> > >  macro_decision;
	map<string, map<string, pair<int, int> > > decision_map;
	map<string, pair<int, int> > macro_decision;
	pair<int, int> term_location;
	set<string> macros;
	string delim = "\t";
	string macro_name;
	string term_name;
	string line;
	int steps;
	int x;
	int y;
	vector<string> tokens;
	pair<set<string>::iterator,bool> exist;
	while(getline(infile, line)){
		
		boost::split(tokens, line, boost::is_any_of("\t"));
		if(tokens.size() == 1){
			macro_name = tokens[0];
			macro_name.erase(remove(line.begin(),line.end(),'\n'),line.end());
			exist = macros.insert(macro_name);
			if(exist.second == false){
				decision_map[macro_name] = macro_decision;
				macro_decision.clear();
			}
		}
		else{
			term_name = tokens[0];
			steps = atoi(tokens[1].c_str());
			x = atoi(tokens[2].c_str());
			tokens[3].erase(remove(line.begin(),line.end(),'\n'),line.end());
			y = atoi(tokens[3].c_str());
			term_location.first = x;
			term_location.second = y;
			macro_decision[term_name] = term_location; 
			//cout << macro_name << endl;
			//cout << term_name << '\t' << x << '\t' << y << '\t' << endl;
		}
	}

	// debug
/*
	for(map<string, map<string, pair<int, int> > >::iterator it = decision_map.begin(); it != decision_map.end(); ++it){
		macro_decision = it->second;
		cout << it->first << endl;
		for(map<string, pair<int, int> >::iterator it = macro_decision.begin(); it != macro_decision.end(); ++it){
			cout << it-> first << '\t' << (it->second).first << '\t' << (it->second).second << endl;
		}
	}
*/
	infile.close();
	return decision_map;	
}
/* Function to update the new location of pins according to decision map
*/
void updateNewTermLocations(map<string, map<string, pair<int, int> > > decision_map, oaBlock *block, oaNativeNS ns){
	oaBox  macro_box;	

	oaString inst_name;
	oaString term_name;
	string instName;
	string termName;
	map<string, pair<int, int> > macro_map;
	oaIter<oaInst> instIterator(block->getInsts());
	while(oaInst* inst = instIterator.getNext()){
		inst->getName(ns, inst_name);
		oaIter<oaInstTerm> instTermIterator(inst->getInstTerms());
		/*
		inst->getBBox(macro_box);
		cout << "Original" << endl;
		cout << macro_box.upperRight().x() << '\t' << macro_box.upperRight().y() << endl;
		cout << macro_box.lowerLeft().x() << '\t' << macro_box.lowerLeft().y() << endl;
		*/
		while(oaInstTerm* instTerm = instTermIterator.getNext()){	
			instTerm->getTermName(ns, term_name);
			if(term_name != "VDD" && term_name != "VSS"){
				for(map<string, map<string, pair<int, int> > >::iterator it = decision_map.begin(); it != decision_map.end(); ++it){
					if(inst_name == (it->first).c_str()) instName = it->first;
				}
				macro_map = decision_map[instName];
				for(map<string, pair<int, int> >::iterator it = macro_map.begin(); it != macro_map.end(); ++it){
					if(term_name == (it->first).c_str() ) termName = it->first;  
				}
				oaPoint new_position = oaPoint(macro_map[termName].first, macro_map[termName].second);		
				cout << new_position.x() << '\t' << new_position.x() << endl;
				OAHelper::MovePinToPosition(instTerm, new_position);
				
				
			}
			/*
			inst->getBBox(macro_box);
			cout << "After Change" << endl;
			cout << macro_box.upperRight().x() << '\t' << macro_box.upperRight().y() << endl;
			cout << macro_box.lowerLeft().x() << '\t' << macro_box.lowerLeft().y() << endl;
			*/
		}
		
	}
}


	


