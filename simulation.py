import random 
import os

import simpy as sim
import numpy as np

from utilities import AuxiliaryFunctions
import yaml



class Simulation():
      def __init__(self) -> None:
            
            self.variables = yaml.load(open("paramters.yaml"), Loader=yaml.FullLoader)

            self.auxiliaryFunctions = AuxiliaryFunctions(self.variables)
            
            return None
      
      def __generator__(self):
            """ Generates patients"""
            patient = {"id": 1, "category": None}
            while True:
                  self.env.process(self.__activity__(patient))
                  timeBetweenArrivals = random.expovariate(1/10)
                  yield self.env.timeout(timeBetweenArrivals) # Let other patients arrive
                  patient["id"] += 1
      
      def __activity__(self,
                       patient: dict[str, int]
                       ):
            """ Simulates activity of the patients """

            # 1st Stage: Reception
            yield from self.activity_reception(patient)  # Use yield from to maintain generator
            
            # 2nd Stage: Nurse
            # self.activity_nurse(patient)
            
            # 3rd Stage: Doctor
            # self.activity_doctor(patient)

      
      def __setUp__(self ):
            """Set ups a simulation instance to be ran """
            self.env = sim.Environment()
            resourcesListName = ["receptionist", "nurse", "doctor"]
            for resourceName in resourcesListName:
                  setattr(self, resourceName, sim.Resource(self.env, capacity = self.variables["RESOURCES_CAPACITY"][resourceName]))
            self.env.process(self.__generator__())
            self.env.run(until = self.variables["GENERAL_SETTINGS"]["totalSimulationTime"])

            # Storing results

      def start(self):
            # <<==>> ADD MULTIHIREADING HERE <<==>>
            numberOfRuns = self.variables["GENERAL_SETTINGS"]["numberOfRuns"]
            for i in range(numberOfRuns):
                  self.__setUp__()
      
      ##########################
      ## ACTIVITY SUBROUTINES ##
      ##########################
      def activity_reception(self, patient: dict[str, int]):
            def receptionEvaluation():
                  "Stochastic evaluation following a categorical/discrete-probability distribution"
                  priorities = {
                        "critical": self.variables["RECEPTION"]["receptionistAssesment"]["critical"],
                        "urgent": self.variables["RECEPTION"]["receptionistAssesment"]["urgent"],
                        "moderate": self.variables["RECEPTION"]["receptionistAssesment"]["moderate"],
                        "low": self.variables["RECEPTION"]["receptionistAssesment"]["low"],
                        "non-urgent": self.variables["RECEPTION"]["receptionistAssesment"]["non-urgent"]
                  }
                  return np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]
            self.auxiliaryFunctions.eventPrint(eventStage = "reception",
                                               isStart = True,
                                               patient_id = patient["id"],
                                               time = self.env.now)
            
            # Requesting resource (appending to queue)
            receptioninstRequest = self.receptionist.request()
            yield receptioninstRequest

            # Service time
            receptionTime = random.expovariate(1/7)
            yield self.env.timeout(receptionTime)

            # Releasing resource
            # Evaluation of the patient: 
            patient["category"] = receptionEvaluation()
            self.receptionist.release(receptioninstRequest)
            self.auxiliaryFunctions.eventPrint(eventStage = "reception",
                                               isStart = False,
                                               patient_id = patient["id"],
                                               time = self.env.now,
                                               otherInfo = f"Classified as {patient['category']}")




if __name__ == "__main__":
      simulation = Simulation()
      simulation.start()