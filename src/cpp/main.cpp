/* EE201A Winter 2018 Course Project
 */

#include <iostream>
#include "oaDesignDB.h"
#include <vector>
#include "InputOutputHandler.h"
#include "ProjectInputRules.h"
#include "OAHelper.h"

#include <fstream>
#include <sys/wait.h>
//#include <boost/filesystem.hpp>

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
    cout << "<YOUR TEAM NUMBER HERE>" << endl;
    cout << "<YOUR NAMES HERE>" << endl;
    cout << "<YOUR STUDENT IDS HERE>" << endl;
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

	// obtain input rule information
	int pin_layer = inputRules.getPinLayer();
	int min_routing_layer = inputRules.getMinRoutingLayer();
	int max_routing_layer = inputRules.getMaxRoutingLayer();
	float pin_movement_step_size = inputRules.getPinMoveStep();
	float min_pin_pitch = inputRules.getMinPinPitch();
	float max_perturbation = inputRules.getMaxPinPerturbation();

	// Open a file 
	ofstream myfile;	
	myfile.open("cplex_for_python.txt");
	
	// Write global info on the top 
	myfile << "Global info\n";
	myfile << "pinLayer\t" << pin_layer << '\n';
	myfile << "minRoutingLayer\t" << min_routing_layer << '\n';
	myfile << "maxRoutingLayer\t" << max_routing_layer << '\n';
	myfile << "pinMovement\t" << pin_movement_step_size << '\n';
	myfile << "minPinPitch\t" << min_pin_pitch << '\n';
	myfile << "maxPerturbation\t" << max_perturbation << '\n';
	// Separation
	myfile << "*\n";

	// Macro Information in the dump file 
	oaString macro_name, macro_type;
	oaBox macro_box;
	oaIter<oaInst> InstIterator(block->getInsts());
	while(oaInst* inst = InstIterator.getNext())
	{
		// Macro Indicator
		myfile << "Macro\n";
		inst->getName(ns, macro_name);
		inst->getCellName(ns, macro_type);
		inst->getBBox(macro_box);
		//int macro_upperRight_x = macro_box.upperRight().x();
		//int macro_upperRight_y = macro_box.upperRight().y();
		//int macro_lowerLeft_x = macro_box.lowerLeft().x();
		//int macro_lowerLeft_y = macro_box.lowerLeft().y();
		myfile << macro_name << '\t' << macro_type << '\t' << macro_box.upperRight().x() << '\t' << macro_box.upperRight().y() << '\t' << macro_box.lowerLeft().x() << '\t' << macro_box.lowerLeft().y() << '\n';
		
		oaString instTerm_name, instTerm_net_name;
		oaIter<oaInstTerm> InstTermIterator(inst->getInstTerms());
		while(oaInstTerm* instTerm = InstTermIterator.getNext())
		{
			instTerm->getTermName(ns, instTerm_name);
			// Excluding VDD and VSS instTerms
			if((instTerm_name != "VDD") && (instTerm_name != "VSS"))
			{
				// InstTerm Indicator
				myfile << "T\t";
				myfile << instTerm_name << '\t' << "1\t";
				if((instTerm->getNet()) == NULL)
				{
					myfile << "NONE\t";
				}
				else
				{
					instTerm->getNet()->getName(ns, instTerm_net_name);
					myfile << instTerm_net_name << '\t';
				}
				oaPoint instTerm_position = OAHelper::GetAbsoluteInstTermPosition(instTerm);
				myfile << instTerm_position.x() << '\t' << instTerm_position.y() << '\n';
			}
		}
		// End to a macro Indicator
		myfile << "end\n";	
	}

	// Net Information in the dump file
	oaString net_name, net_instTerm_name;
	oaIter<oaNet> netIterator(block->getNets());
	while(oaNet* net = netIterator.getNext())
	{
		if((net->getTerms().getCount() == 0) && (net->getInstTerms().getCount() > 0))
		{
			net->getName(ns, net_name);
			//bool firstEnter = true;
			if((net_name != "VDD") && (net_name != "VSS"))
			{
				myfile << "Net\n";
				myfile << net_name << '\n';
				oaIter<oaInstTerm> instTermIterator(net->getInstTerms());
				while(oaInstTerm* instTerm = instTermIterator.getNext())
				{
					instTerm->getTermName(ns, net_instTerm_name);
					//if(firstEnter)
					//{
					//	myfile << "Net\n";
					//	myfile << net_name << '\n';
					//	firstEnter = false;
					//}
					oaPoint net_instTerm_position = OAHelper::GetAbsoluteInstTermPosition(instTerm);
					myfile << "T\t" << net_instTerm_name << '\t' << "1\t" << net_name << '\t' << net_instTerm_position.x() << '\t' << net_instTerm_position.y() << '\n';
				}	
				myfile << "end\n";
				//firstEnter = true;
			}
		}
	}
	
	myfile.close();	


	// Create child process and let the parent process to wait for the child process to finish
	pid_t PID = 0;
	// Check the status of the child process
	int status;
	// Create a new process
	PID = fork();

	// If child process, call python script
	if(PID == 0)
	{
		execl("/bin/sh", "sh", "-c", "python test.py", NULL);
	}
	else // Parent process waiting for cplex python script to complete
	{
		waitpid(PID, &status, 0);
		// Wait for the solution .txt file dumped by Python side
		ifstream pythonSolution("python.txt");
		while(!pythonSolution.is_open())
		{
			;//cout << "Can't find python.txt" << endl;
		}
		//cout << "python.txt exists now" << endl;
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
