import math
from datetime import timedelta

import numpy as np
import sys

class TieStrengthHandler:
    """
    @param timeStep : one time step for the decay formula in minutes
    @param jumpSize: value of increase of a tie when an interaction takes place
    @param periodOfTotalDecay: After how many minutes no collaboration event should a relationship totally disappear (including the period of stability)?   (Will be converted to the number of timesteps)
    Note that the periodOfTotalDecay must be larger than the offset (period of stability)
    @param scale:  if decay = 0.5, the scale param indicates the half life of a tie: expressed in timesteps! Otherwise it's the timesteps from origin + offset for which the decay function will return the value of the decay parameter
    @param offset: period of stability of tie strength in MINUTES (the same unit as the timesteps) : must be expressed in the "number of timesteps", therefore divide this by the timestep value
    @param decay : decay rate of tie strength
    """
    def __init__(self,timeStep, jumpSize, periodOfTotalDecay, threshold = 0.01,scale = None, offset = 0, decay = 0.5):
        self.jumpSize = jumpSize
        self.upperBoundary = 1
        self.timeStep = timeStep   #in minutes
        self.decay = decay
        self.offset = offset/timeStep
        self.threshold = threshold
        if scale:
            self.scale = scale
        else:
            self.scale = self.__calculateHalfLife(periodOfTotalDecay)

    """
    Calculate the half life based on a constant threshold value and the period of total decay 
    Half life is the square root of ln(decay)* the period in timesteps squared;    with decay == 0.5! 
    divided by the ln(threshold) 
    
     @param periodOfTotalDecay: After how many minutes no collaboration event should a relationship totally disappear (including the period of stability)?   (Will be converted to the number of timesteps) 
    """
    def __calculateHalfLife(self,periodOfTotalDecay):
        if self.decay != 0.5 :
            #this logic does not hold anymore since the scale == half life ONLY if the decay = 0.5
            sys.exit("The half life can only be calculated if the decay value equals 0.5. Either set the decay value to 0.5, or provide custom scale and threshold values.")
        timesteps = periodOfTotalDecay / self.timeStep
        if  self.offset >= timesteps:
            sys.exit("The period of total decay should be larger than the period of stability.")
        nominator = (timesteps - self.offset)**2   #we omit max(0, value)  because the decay period should be larger than the offset
        nominator = nominator * np.log(self.decay)
        fraction = nominator / (np.log(self.threshold))
        halflife = math.sqrt(fraction)
        return halflife


    """
    Return the threshold at which an edge disappears if its weight falls below the threshold  
    """
    def getWeightCutoffThreshold(self):
        return self.threshold

    """
    Increase the current tie strength by a parameter value jumpsize to a maximum set by upper boundary
    """
    def handleInteraction(self,currentTieStrength):
        return min(currentTieStrength + self.jumpSize, self.upperBoundary)




    """
    Calculates the number of time steps (as set in this tiestrengthhandler class between the current timestamp and the target timestamp) 
    @param currentWeightsTimestamp : begin timestamp of datetime object 
    @param targetTimestamp: target timestamp of which we want to know the new weight later 
    @returns how many timesteps there are between begin and target 
    NOTE:  the difference between the begin and target TS is not necessarily a multiple of the timeStep variable, so no rounding is needed 
        This is no problem, as the function will return a fraction : this will result in an accurate weight decay, so definitely not round this value!
        Just use the fraction as the number of timesteps in the decay function 
    
    """
    def calculateNumberOfTimeSteps(self,currentWeightsTimestamp,targetTimestamp):

        timeDifference = (targetTimestamp - currentWeightsTimestamp).total_seconds() / 60
        timeSteps = timeDifference / self.timeStep



        return timeSteps



    """
    IMPORTANT: PARAMETERS SHOULD REFERENCE THE POINT WHEN THE LAST EVENT TOOK PLACE ON THIS EDGE !!
    Decays the weight following the tie decay function 
    CONDITION: WITHOUT incorporating an effect for interactions: there is no interaction between the timestamp of
               the currentWeight and the target timestamp!!
    @param currentWeight: the weight value at the moment of the last event on this edge:  to decay over the period of time (timesteps) 
    @param numberOfTimeSteps : the number of timesteps to decay the weight value over : difference between the timestamp of the last event on this edge and the timestamp we want to know the decayed weight of
    @returns the edge weight after the numberOfTimeSteps 
    """
    def decayEdgeWeight(self,currentWeight,numberOfTimeSteps) :

        value = max(0, (numberOfTimeSteps - self.offset))**2
        denominator = (self.scale**2) / np.log(self.decay)
        value = value / denominator
        decayedWeight = currentWeight * math.exp(value)
        #upper bound to tie strength
        newWeight = min(decayedWeight, self.upperBoundary)
        return newWeight


    """
    Only call function with currentTS that the last interaction on the edge took place 
    @param currentWeight: the weight value to decay over the period of time
    @param currentTS: current timestamp in DateTime format  of last interaction on the edge we're calculating the decay timestamp of 
    """
    def getPredictedTSofDecay(self, currentWeight, currentTS):

        #at the current point there is an interaction so we could take the offset into account
        #Add offset to currentTS to form the new starting point : offset is in timesteps so multiple
        updatedCurrentTS = currentTS + timedelta(minutes=(self.offset * self.timeStep))

        nominator = (np.log(self.threshold) - np.log(currentWeight))*(self.scale**2)
        value = nominator / (np.log(self.decay))
        totalTimesteps = math.sqrt(value)

        #at currentTS + the number of timesteps, the weight value will be equal to the threshold, after that the edge will be removed

        predictedDecayTS = updatedCurrentTS + timedelta(minutes=(totalTimesteps * self.timeStep))
        #add a small amount to go over the threshold
        predictedDecayTS = predictedDecayTS + timedelta(minutes = 1)

        return predictedDecayTS
