/* EE201A Winter 2018 Course Project
 */

#include "OAHelper.h"
#include <iostream>
using namespace std;

OAHelper::OAHelper()
{
}

OAHelper::~OAHelper()
{
}

/* Function returns position of an oaTerm as an oaPoint
 * oaTerm -> oaPin -> oaPinFig -> oaBox -> getCenter()
 */
oaPoint OAHelper::GetTermPosition(oaTerm* term)
{
	oaIter<oaPin> pinIterator(term->getPins());
	oaIter<oaPinFig> pinFigIterator(pinIterator.getNext()->getFigs());
	oaPinFig* pinFig = pinFigIterator.getNext();
	oaBox box; oaPoint point;
	pinFig->getBBox(box);
	box.getCenter(point);
	return point;
}

/* Function returns ABSOLUTE position of an oaInstTerm as an oaPoint
 * The associated oaTerm is fetched, which is basically the corresponding pin inside the macro block
 * The oaTerm position is then added to the oaInst origin to get the absolute instTerm position
 * Note: We cannot simply use the oaInst origin as the oaInstTerm position(as in Labs 1 & 3).
 */
oaPoint OAHelper::GetAbsoluteInstTermPosition(oaInstTerm* instTerm)
{
	//Get relative position of associated terminal inside the instance master
	oaTerm* assocTerm = instTerm->getTerm();
	oaPoint relativePos = GetTermPosition(assocTerm);
    
	//Get the origin and orientation of the instance
	oaInst* inst = instTerm->getInst();
	oaPoint instOrigin;
	inst->getOrigin(instOrigin);
	oaOrient orient = inst->getOrient();
	
	//Rotate relative position by orient
	oaTransform trans = oaTransform(orient);
	relativePos.transform(trans);
	
	//Compute absolute position in global design
	oaPoint absolutePos = relativePos + instOrigin;
	return absolutePos;
}

/* Function moves the pin (oaTerm) associated with instTerm to ABSOLUTE position newPos
 */
void OAHelper::MovePinToPosition(oaInstTerm* instTerm, oaPoint newAbsolutePos)
{
	//cout << newAbsolutePos.x() << '\t' << newAbsolutePos.x() << endl;
	//Get current relative position of associated term
	oaTerm* assocTerm = instTerm->getTerm();
	oaPoint currentRelativePos = GetTermPosition(assocTerm);
	
	//Get origin, orientation and inverse orientation of inst
	oaInst *inst = instTerm->getInst();
	oaPoint instOrigin;
	inst->getOrigin(instOrigin);
	oaOrient orient = inst->getOrient();
	oaOrient inverseOrient = orient.getRelativeOrient(oacR0);

	//Find new relative position and rotate it according to inverse orient
	oaPoint newRelativePos = newAbsolutePos - instOrigin;
	oaTransform trans = oaTransform(inverseOrient);
	newRelativePos.transform(trans);
	
	//Calculate offset
	oaPoint offset = newRelativePos - currentRelativePos;
	oaTransform trans2 = oaTransform(offset);
	
	//Find associated term's pinfig and apply move
	oaIter<oaPin> pinIterator(assocTerm->getPins());
	oaIter<oaPinFig> pinFigIterator(pinIterator.getNext()->getFigs());
	oaPinFig* pinFig = pinFigIterator.getNext();

	pinFig->move(trans2);
}

/* Function moves the pin (oaTerm) associated with instTerm by the offset oaPoint
 */
void OAHelper::MovePinByOffset(oaInstTerm* instTerm, oaPoint offset)
{
	//Get orientation of inst, and find its inverse
	oaInst *inst = instTerm->getInst();
	oaOrient orient = inst->getOrient();
	oaOrient inverseOrient = orient.getRelativeOrient(oacR0);
	
	//Rotate offset according to inverse orient
	oaTransform trans = oaTransform(inverseOrient);
	offset.transform(trans);
		
	oaTransform trans2 = oaTransform(offset);

	//Find associated term's pinfig and apply move
	oaTerm* assocTerm = instTerm->getTerm();
	oaIter<oaPin> pinIterator(assocTerm->getPins());
	oaIter<oaPinFig> pinFigIterator(pinIterator.getNext()->getFigs());
	oaPinFig* pinFig = pinFigIterator.getNext();

	pinFig->move(trans2);
}
