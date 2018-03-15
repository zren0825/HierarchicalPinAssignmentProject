/* EE201A Winter 2018 Course Project
 */

#include "InputOutputHandler.h"
#include <iostream>
#include <fstream>
#include <string>
using namespace std;
oaNativeNS ns;

InputOutputHandler::InputOutputHandler()
{
}

InputOutputHandler::~InputOutputHandler()
{
}

/* Function parses command line arguments for path info
 * OA lib name is always DesignLib
 * Input: designName outputDesignName inputRuleFileName
 */
void InputOutputHandler::ReadInputArguments(char* argv[],
                                                DesignInfo& designInfo)
{
    designInfo.libPath="./DesignLib";
    designInfo.libName="DesignLib";
    designInfo.designName=string(argv[1]);
    designInfo.outputDesignName=string(argv[2]);
    designInfo.designView="layout";
    designInfo.inputRuleFileName=string(argv[3]);
    designInfo.macroInfoFileName=string(argv[4]);
}

/* Given design info, function opens library and returns pointer to oaDesign
 */
oaDesign* InputOutputHandler::ReadOADesign(DesignInfo designInfo, oaLib* lib)
{
    oaNativeNS	ns;
    oaScalarName	libName(ns, designInfo.libName.c_str());
    oaScalarName	cellName(ns, designInfo.designName.c_str());
    oaScalarName	viewName(ns, designInfo.designView.c_str());
    oaString	libraryPath(designInfo.libPath.c_str());
    
    // open the libs defined in "lib.def"
	oaLibDefList::openLibs();

	// locate the library
	lib = oaLib::find(libName);
  
	if (!lib)
	{
  	    if (oaLib::exists(libraryPath))
	    {
			lib = oaLib::open(libName, libraryPath);
	    }
	    else
	    {
			cerr << "Unable to open " << libraryPath 
				 << "/. Make sure the OA database exists before running!" << endl;
			return NULL;
	    }
	}
    oaDesign *design = oaDesign::open(libName, cellName, viewName,'r');//change r to a to write

    return design;
}

/* Given design, function opens the hierarchy and returns the top block
 */
oaBlock* InputOutputHandler::ReadTopBlock(oaDesign* design)
{
	design->openHier();
	oaBlock *block = design->getTopBlock();
	if (!block) {
		//block = oaBlock::create(design);
		cerr << "Unable to find top block in current design. Something is wrong with the input DesignLib." << endl;
		return NULL;
	}

	return block;
}


/* Given block, function iterates through all instances (macro blocks) and saves
 * a unique copy of the master design for each. This enables custom pin placement for each instance.
 */
void InputOutputHandler::SaveMacroDesignCopies(DesignInfo designInfo, oaBlock* block)
{
	//Save macro naming information to file - useful for Innovus flow later
	ofstream macroFile;
	macroFile.open(designInfo.macroInfoFileName.c_str());	

	oaIter<oaInst> instIterator(block->getInsts());
	while (oaInst* inst = instIterator.getNext()) {
		oaDesign* masterDesign = inst->getMaster();
		oaString instName, masterCellName;
		inst->getName(ns, instName);
		inst->getCellName(ns, masterCellName);

		//New name for macro copy
		string outputName = string(masterCellName) + "_" + string(instName);

		oaScalarName	libName(ns, designInfo.libName.c_str());
		oaScalarName	outputDesignName(ns, outputName.c_str());
		oaScalarName	viewName(ns, "abstract");

		//Save copy of master cell under new name
		masterDesign->saveAs(libName, outputDesignName, viewName);
		oaDesign *masterDesignCopy = oaDesign::open(libName, outputDesignName, viewName, 'a');

		// Change master cell of top block inst to new design
		inst->setMaster(masterDesignCopy);
		
		//Print macro naming info to file
		macroFile << string(masterCellName) << " " << string(masterCellName)+"_"+string(instName) << endl;
	}
}

/* When this function is called after opening design, it saves a copy of the design at the end
 * The improved macros can then be extracted from this copy of the design (OA2LEF)
 */
void InputOutputHandler::SaveAndCloseAllDesigns(DesignInfo designInfo, oaDesign* design, oaBlock* block)
{
	//Save and close macro designs (created earlier)
	oaIter<oaInst> instIterator(block->getInsts());
	while (oaInst* inst = instIterator.getNext()) {
		oaDesign* masterDesign = inst->getMaster();
		masterDesign->save();
		if (masterDesign->isDesign())
			masterDesign->close();
	}

	//Save and close top level design
    oaScalarName	libName(ns, designInfo.libName.c_str());
    oaScalarName	outputDesignName(ns, designInfo.outputDesignName.c_str());
    oaScalarName	viewName(ns, designInfo.designView.c_str());
    oaString	libraryPath(designInfo.libPath.c_str());
    design->saveAs(libName, outputDesignName, viewName, 1);

	if (design->isDesign())
		design->close();
}
