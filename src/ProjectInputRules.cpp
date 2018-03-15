/* EE201A Winter 2018 Course Project
 */

#include "ProjectInputRules.h"
#include <iostream>
#include <string>
using namespace oa;
using namespace std;

//PUBLIC METHODS
ProjectInputRules::ProjectInputRules() {
    __pinLayer = 0;
    __minRoutingLayer = 0;
    __maxRoutingLayer = 0;
    __pinMoveStep = 0;
    __minPinPitch = 0;
    __maxPinPerturbation = 0;
	__infinitePerturbationAllowed = false;
}

ProjectInputRules::ProjectInputRules(const string inputRuleFilename) {
    //Read input rules from file
    ifstream infile;
    infile.open(inputRuleFilename.c_str());

    if (!infile) {
        cout << "There was a problem opening input rule file "
             << inputRuleFilename
             << " for reading."
             << endl;
        exit(1);
    }

	string perturb;

    infile >> __pinLayer;
    infile >> __minRoutingLayer;
    infile >> __maxRoutingLayer;
    infile >> __pinMoveStep;
    infile >> __minPinPitch;
    infile >> perturb;
	if (perturb == "Inf") {
		__infinitePerturbationAllowed = true;
		__maxPinPerturbation = -1;
	}
	else {
		__infinitePerturbationAllowed = false;
		__maxPinPerturbation = atoi(perturb.c_str());
	}
}

ProjectInputRules::~ProjectInputRules() {}

int ProjectInputRules::getPinLayer() {
    return __pinLayer;
}

int ProjectInputRules::getMinRoutingLayer() {
    return __minRoutingLayer;
}

int ProjectInputRules::getMaxRoutingLayer() {
    return __maxRoutingLayer;
}

float ProjectInputRules::getPinMoveStep() {
    return __pinMoveStep;
}

float ProjectInputRules::getMinPinPitch() {
    return __minPinPitch;
}

float ProjectInputRules::getMaxPinPerturbation() {
    return __maxPinPerturbation;
}

void ProjectInputRules::setPinLayer(int rule) {
    __pinLayer = rule;
}

void ProjectInputRules::setMinRoutingLayer(int rule) {
    __minRoutingLayer = rule;
}

void ProjectInputRules::setMaxRoutingLayer(int rule) {
    __maxRoutingLayer = rule;
}

void ProjectInputRules::setPinMoveStep(float rule) {
    __pinMoveStep = rule;
}

void ProjectInputRules::setMinPinPitch(float rule) {
    __minPinPitch = rule;
}

void ProjectInputRules::setMaxPinPerturbation(float rule) {
    __maxPinPerturbation = rule;
}

void ProjectInputRules::print() {   
    cout << "Input rules:" << endl
         << "... pin layer: " << __pinLayer << endl
         << "... minimum routing layer: " << __minRoutingLayer << endl
         << "... maximum routing layer: " << __maxRoutingLayer << endl
         << "... pin move step (microns): " << __pinMoveStep << endl
         << "... minimum pin pitch (microns): " << __minPinPitch << endl;
	if (__infinitePerturbationAllowed)
         cout << "... maximum pin perturbation (microns): Infinite. Setting value to -1." << endl;
	else
         cout << "... maximum pin perturbation (microns): " << __maxPinPerturbation << endl;
}
