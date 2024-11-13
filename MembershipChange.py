

class MembershipChange():

   """
   This function is overridden in each of the child classes that represent a specific membership change
   @param temporalGraph  object of class TemporalGraph that consists of a series of graph snapshots
   @param expansionChangeMiner object of that class to mine for expansion changes  (atomic change as building block for other complex changes)
   @param expulsionChangeMiner object of that class to mine for expulsion changes  (atomic change as building block for other complex changes)
   @return dict of membership changes
   """
   def detectChanges(self,temporalGraph, expansionChangeMiner, expulsionChangeMiner):
        pass

   def printDetectedChanges(self, listOfChanges):
       pass

   def printToCSV(self, listOfChanges, writer):
       pass