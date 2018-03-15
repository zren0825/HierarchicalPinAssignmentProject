/* EE201A Winter 2018 Course Project
 */

#ifndef INPUTOUTPUTHANDLER_H
#define	INPUTOUTPUTHANDLER_H

#include <vector>
#include <string>
#include "oaDesignDB.h"
//#include "Connection.h"
using namespace std;
using namespace oa;

struct DesignInfo
{
    string libPath;
    string libName;
    string designName;
    string outputDesignName;
    string designView; 
    string inputRuleFileName;
    string macroInfoFileName;
};

class InputOutputHandler
{
public:
    InputOutputHandler();
    virtual ~InputOutputHandler();
	static void ReadInputArguments(char* argv[], DesignInfo& designInfo);
    static oaDesign* ReadOADesign(DesignInfo designInfo, oaLib* lib);
	static oaBlock* ReadTopBlock(oaDesign* design);
	static void SaveMacroDesignCopies(DesignInfo designInfo, oaBlock* block);
	static void SaveAndCloseAllDesigns(DesignInfo designInfo, oaDesign* design, oaBlock* block);

    
private:

};

#endif	/* INPUTOUTPUTHANDLER_H */

