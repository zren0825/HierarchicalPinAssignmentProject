/* EE201A Winter 2018 Course Project
 */

#include <iostream>
#include "oaDesignDB.h"
#include <vector>
#include <map>
#include "InputOutputHandler.h"
#include "ProjectInputRules.h"
#include "OAHelper.h"
#include "helper.h"

using namespace oa;
using namespace std;

static oaNativeNS ns;

/*
 * 
 */
int main(int argc, char *argv[])
{
    //Hello World
    cout << "=================================================" << endl;
    cout << "Automated Inter-Chip Pin Assignment" << endl;
    cout << "UCLA EE 201A Winter 2017 Course Project" << endl;
    cout << endl;
    cout << "<Group 16>" << endl;
    cout << "<Zhengshuang Ren>" << endl;
    cout << "<704775155>" << endl;
    cout << "=================================================" << endl << endl;
   
    //Usage
    cout << "Ensure you have an existing OA design database before running this tool. Also please adhere to the following command-line usage:" << endl;
    cout << "./PinAssign <DESIGN NAME> <OUTPUT DESIGN NAME> <INPUT RULE FILE NAME> <MACRO INFO FILENAME>" << endl;
    cout << "For example:" << endl;            
    cout << "./PinAssign sbox_x2 sbox_x2_minrule benchmarks/sbox_x2/min.inputrules logs/sbox_x2/pinassign_sbox_x2_minrule.macros" << endl;

	// Initialize OA with data model 3
	oaDesignInit(oacAPIMajorRevNumber, oacAPIMinorRevNumber, 3);
    oaRegionQuery::init("oaRQSystem");

    //Read in design library
    cout << "\nReading design library..." << endl;
    DesignInfo designInfo;
    InputOutputHandler::ReadInputArguments(argv, designInfo);
	oaLib* lib;
    oaDesign* design= InputOutputHandler::ReadOADesign(designInfo, lib);

	// Get the TopBlock for this design.
    oaBlock* block= InputOutputHandler::ReadTopBlock(design);

	// Fetch all instances in top block and save a unique master design copy for each
    cout << "\nSaving copies of each unique macro instance..." << endl;
	InputOutputHandler::SaveMacroDesignCopies(designInfo, block);
	
    //now, get the input rules from file
    cout << "\nReading input rules..." << endl;
    ProjectInputRules inputRules(designInfo.inputRuleFileName); 
    inputRules.print();
    
    cout << "\nBeginning pin assignment..." << endl;
	//=====================================================================
    // All pin assignment code should be handled here
	// The scratch code below covers basic traversal and some useful functions provided
	// You are free to edit everything in this section (marked by ==)
	
    	// write design information to a file and open with python scripts
	dumpDesignInfoFile(inputRules, block, ns);

	/* create new process -> call python scripts to make pin placement decision, 
	   meanwhile c++ waits untill the DecisionMade file indicator -> kill process -> return to c++ process  
	*/ 
	


	bool run = true;
	if(run){

		callCplexSolver();
	// read python output decision file
	string decision_filename = "/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/pin_assignment_decision.txt";

	map<string, map<string, pair<int, int> > > decision_map = readDecisionFile(decision_filename);

	// update term locations according to decision map
	updateNewTermLocations(decision_map, block, ns);

	}
	

/*
	// Code provided
	oaString netName, instName, masterCellName, assocTermName, termName;
	oaIter<oaNet> netIterator(block->getNets());
	while (oaNet* net = netIterator.getNext()) {
		net->getName(ns, netName);
		oaIter<oaInstTerm> instTermIterator(net->getInstTerms());
		oaIter<oaTerm> termIterator(net->getTerms());
		
		//InstTerms
		while (oaInstTerm* instTerm = instTermIterator.getNext()) {
			instTerm->getTermName(ns, assocTermName);
			oaPoint instTermPos = OAHelper::GetAbsoluteInstTermPosition(instTerm);

			oaInst* inst = instTerm->getInst();
			inst->getName(ns, instName);
			inst->getCellName(ns, masterCellName);

			// Use either of the 2 functions below to move macro pins
			// Both samples move the instTerm 100 DBUs in the x direction on the global design
			
			// 1. Move pin to new absolute coordinate on the global design
			//oaPoint newPos = oaPoint(instTermPos.x()+100, instTermPos.y());
			//OAHelper::MovePinToPosition(instTerm, newPos);

			// 2. Move pin by offset according to the global design coordinate system
			//oaPoint offset = oaPoint(100,0);
			//OAHelper::MovePinByOffset(instTerm, offset);
		}
		
		//Terms
		while (oaTerm* term = termIterator.getNext()) {
			term->getName(ns,termName);
			oaPoint termPos = OAHelper::GetTermPosition(term);
		}
	}

	//=====================================================================
*/	
    //Save the improved version of the design
    InputOutputHandler::SaveAndCloseAllDesigns(designInfo, design, block);

	if (lib)
		lib->close();

    cout << endl << "\nDone!" << endl;
    return 0;
}

