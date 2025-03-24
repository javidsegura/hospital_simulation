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
            self.priority_map = {
                  "critical": 1,
                  "urgent": 2,
                  "moderate": 3,
                  "low": 4,
                  "non-urgent": 5
            }
            
            return None
      
      def __generator__(self):
            """ Generates patients"""
            patient = {"id": 1, "priority": None, "enterHospital": None, "time_in_system": 0}
            while True:
                  self.env.process(self.__activity__(patient))
                  timeBetweenArrivals = random.expovariate(1/self.variables["ARRIVAL"]["arrivalRate"])
                  yield self.env.timeout(timeBetweenArrivals) # Let other patients arrive
                  patient["id"] += 1
      
      def __activity__(self, patient):
            """ Simulates activity of the patients """

            # 1st Stage: Reception
            yield from self.activity_reception(patient)  # Use yield from to maintain generator
            if (patient["priority"] == "non-urgent"):
                self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo="Patient exited due to non-urgent priority")
                return  # Early return exits the patient from the system
            
            # 2nd Stage: Nurse
            if (patient["priority"] not in ["critical", "urgent"]):
                yield from self.activity_nurse(patient)
                if (patient["priority"] == "non-urgent"):
                    self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo="Patient exited due to non-urgent priority")
                    return  # Early return exits the patient from the system
            
            # 3rd Stage: Doctor
            yield from self.activity_doctor(patient)

      
      def __setUp__(self):
            """Set ups a simulation instance to be ran """
            self.env = sim.Environment()
            
            # Change the nurse resource to a PriorityResource
            self.receptionist = sim.Resource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["receptionist"])
            self.nurse = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["nurse"])
            self.doctor = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["doctor"])
            
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
      def activity_reception(self, patient):
            def receptionEvaluation():
                  """Stochastic evaluation following a categorical/discrete-probability distribution"""
                  priorities = {
                        "critical": self.variables["RECEPTION"]["receptionistAssesment"]["critical"]/100,
                        "urgent": self.variables["RECEPTION"]["receptionistAssesment"]["urgent"]/100,
                        "moderate": self.variables["RECEPTION"]["receptionistAssesment"]["moderate"]/100,
                        "low": self.variables["RECEPTION"]["receptionistAssesment"]["low"]/100,
                        "non-urgent": self.variables["RECEPTION"]["receptionistAssesment"]["non-urgent"]/100
                  }
                  return np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]
            self.auxiliaryFunctions.eventPrint(eventStage = "reception",
                                               justArrived = True,
                                               patient_id = patient["id"],
                                               time = self.env.now)
            
            # Requesting resource (appending to queue)
            receptioninstRequest = self.receptionist.request()
            yield receptioninstRequest

            # Service time
            receptionTime = random.normalvariate(self.variables["RECEPTION"]["receptionServiceTime"]["mean"], self.variables["RECEPTION"]["receptionServiceTime"]["std"])
            yield self.env.timeout(receptionTime)

            # Releasing resource
            # Evaluation of the patient: 
            patient["priority"] = receptionEvaluation()
            self.receptionist.release(receptioninstRequest)
            self.auxiliaryFunctions.eventPrint(eventStage = "reception",
                                               justArrived = False,
                                               patient_id = patient["id"],
                                               time = self.env.now,
                                               otherInfo = f"Classified as {patient['priority']}")
      
      def activity_nurse(self, patient):
            assert patient["priority"] is not None, "Patient priority must be set before calling nurse activity"
            def nurseEvaluation(currentPriority):
                  """Stochastic evaluation following a categorical/discrete-probability distribution"""
                  match (currentPriority):
                        case "moderate":
                              priorities = {
                                          "critical": self.variables["NURSE"]["nurseAssesment"]["moderate"]["critical"]/100,
                                          "urgent": self.variables["NURSE"]["nurseAssesment"]["moderate"]["urgent"]/100,
                                          "moderate": self.variables["NURSE"]["nurseAssesment"]["moderate"]["moderate"]/100,
                                          "low": self.variables["NURSE"]["nurseAssesment"]["moderate"]["low"]/100,
                                          "non-urgent": self.variables["NURSE"]["nurseAssesment"]["moderate"]["non-urgent"]/100
                                    }
                              return np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]
                        case "low":
                              priorities = {
                                          "critical": self.variables["NURSE"]["nurseAssesment"]["low"]["critical"]/100,
                                          "urgent": self.variables["NURSE"]["nurseAssesment"]["low"]["urgent"]/100,
                                          "moderate": self.variables["NURSE"]["nurseAssesment"]["low"]["moderate"]/100,
                                          "low": self.variables["NURSE"]["nurseAssesment"]["low"]["low"]/100,
                                          "non-urgent": self.variables["NURSE"]["nurseAssesment"]["low"]["non-urgent"]/100
                                    }
                              return np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]

            self.auxiliaryFunctions.eventPrint(eventStage="nurse",
                                               justArrived=True,
                                               patient_id=patient["id"],
                                               time=self.env.now)
            
            # Get priority based on patient category
            priority = self.priority_map.get(patient["priority"]) 
            
            # Requesting resource with priority (appending to priority queue)
            nurseRequest = self.nurse.request(priority=priority)
            yield nurseRequest

            # Service time
            nurseTime = random.normalvariate(self.variables["NURSE"]["nurseServiceTime"][patient["priority"]]["mean"], self.variables["NURSE"]["nurseServiceTime"][patient["priority"]]["std"])
            yield self.env.timeout(nurseTime)

            # Releasing resource
            patient["priority"] = nurseEvaluation(patient["priority"])
            self.nurse.release(nurseRequest)

            self.auxiliaryFunctions.eventPrint(eventStage="nurse",
                                               justArrived=False,
                                               patient_id=patient["id"],
                                               time=self.env.now,
                                               otherInfo=f"Classified as {patient['priority']}")

      def activity_doctor(self, patient):
            assert patient["priority"] is not None, "Patient priority must be set before calling doctor activity"
            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=True,
                                               patient_id=patient["id"],
                                               time=self.env.now)
            def doctorEvaluation(currentPriority):
                  """Stochastic evaluation following a categorical/discrete-probability distribution"""
                  match (currentPriority):
                        case "critical":
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "urgent":
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "moderate":
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "low":
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["low"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["low"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]

            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=True,
                                               patient_id=patient["id"],
                                               time=self.env.now)
            
            # Get priority based on patient category
            priority = self.priority_map.get(patient["priority"]) 
            
            # Requesting resource with priority (appending to priority queue)
            doctorRequest = self.doctor.request(priority=priority)
            yield doctorRequest

            # Service time
            doctorTime = random.normalvariate(self.variables["DOCTOR"]["doctorServiceTime"][patient["priority"]]["mean"], self.variables["DOCTOR"]["doctorServiceTime"][patient["priority"]]["std"])
            yield self.env.timeout(doctorTime)

            # Releasing resource
            patient["enterHospital"] = doctorEvaluation(patient["priority"])
            self.doctor.release(doctorRequest)

            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=False,
                                               patient_id=patient["id"],
                                               time=self.env.now,
                                               otherInfo=f"{ 'entering hospital' if patient['enterHospital'] == 'yes' else 'not entering hospital' } -- priority: {patient['priority']}")

if __name__ == "__main__":
      simulation = Simulation()
      simulation.start()