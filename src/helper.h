/* EE201A Winter 2018 Course Project
 */

#include <vector>
#include <string>
#include "oaDesignDB.h"
#include "ProjectInputRules.h"


using namespace std;
using namespace oa;

void dumpDesignInfoFile(ProjectInputRules inputRules, oaBlock* block, oaNativeNS ns);
void callCplexSolver();
map<string, map<string, pair<int, int> > > readDecisionFile(string filename);
void updateNewTermLocations(map<string, map<string, pair<int, int> > > decision_map, oaBlock *block, oaNativeNS ns);
