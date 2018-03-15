/* EE201A Winter 2018 Course Project
 */

#ifndef PROJECTINPUTRULES_H
#define	PROJECTINPUTRULES_H

#include <string>
#include "oaDesignDB.h"
using namespace oa;
using namespace std;


class ProjectInputRules
{
public:
    ProjectInputRules();
    ProjectInputRules(const string inputRuleFilename);
    virtual ~ProjectInputRules();
    
    int getPinLayer();
    int getMinRoutingLayer();
    int getMaxRoutingLayer();
    float getPinMoveStep();
    float getMinPinPitch();
    float getMaxPinPerturbation();

    void setPinLayer(int rule);
    void setMinRoutingLayer(int rule);
    void setMaxRoutingLayer(int rule);
    void setPinMoveStep(float rule);
    void setMinPinPitch(float rule);
    void setMaxPinPerturbation(float rule);

    void print();
    
private:
    int __pinLayer;
	int __minRoutingLayer;
    int __maxRoutingLayer;
	float __pinMoveStep;
    float __minPinPitch;
    float __maxPinPerturbation;
	bool __infinitePerturbationAllowed;
};

#endif	/* PROJECTINPUTRULES_H */

