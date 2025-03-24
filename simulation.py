import random 
import os
import csv
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
            self.__metrics__()
            
            return None
      
      def __metrics__(self):
            """ Initializes metrics """
            self.metricsValues = {
                  #General metrics
                  "totalTime": 0,
                  "totalPatients": 0,
                  "totalCriticalPatients": 0,
                  "totalUrgentPatients": 0,
                  "totalModeratePatients": 0,
                  "totalLowPatients": 0,
                  "totalNonUrgentPatients": 0,
                  # Arrival metrics
                  "totalArrivalTime": 0,
                  # Reception metrics
                  "totalReceptionServiceTime": 0,
                  # Nurse metrics
                  "totalNurseServiceTime": 0,
                  "totalNursePatients": 0,
                  "totalNurseCriticalServiceTime": 0,
                  "totalNurseCriticalPatients": 0,
                  # Doctor metrics
                  "totalDoctorServiceTime": 0,
                  "totalDoctorPatients": 0,
                  "totalDoctorCriticalServiceTime": 0,
                  "totalDoctorCriticalPatients": 0,
                  "totalDoctorUrgentPatients": 0,
                  "totalDoctorModeratePatients": 0,
                  "totalDoctorLowPatients": 0,
                  "totalCriticalHospitalPatients": 0,
                  "totalUrgentHospitalPatients": 0,
                  "totalModerateHospitalPatients": 0,
                  "totalLowHospitalPatients": 0,
                  # Financials
                  "totalFinancials": 0,
                  "totalEnterHospital": 0,
                  "totalExitHospital": 0
            }
            self.metrics = {
                  "totalTime": 0,
                  "totalPatients": 0,
                  "proportionCriticalPatients": 0,
                  "proportionUrgentPatients": 0,
                  "proportionModeratePatients": 0,
                  "proportionLowPatients": 0,
                  "proportionNonUrgentPatients": 0,
                  # Reception metrics
                  # "averageReceptionServiceTime": self.metricsValues["totalReceptionServiceTime"] / self.metricsValues["totalPatients"],
                  # # Nurse metrics
                  # "averageNurseServiceTime": self.metricsValues["totalNurseServiceTime"] / self.metricsValues["totalNursePatients"],
                  # "averageNurseCriticalServiceTime": self.metricsValues["totalNurseCriticalServiceTime"] / self.metricsValues["totalNurseCriticalPatients"],
                  # # Doctor metrics
                  # "averageDoctorServiceTime": self.metricsValues["totalDoctorServiceTime"] / self.metricsValues["totalDoctorPatients"],
                  # "proportionDoctorUrgentHospitalization": self.metricsValues["totalDoctorUrgentPatients"] / self.metricsValues["totalDoctorPatients"]
                  # Financial metrics
                  "totalFinancials": 0,
                  "averageRevenuePerPatient": 0,
                  "hospitalEntryRate": 0
            }

      def update_metrics(self):
            # Only calculate proportions if we have patients
            if self.metricsValues["totalPatients"] > 0:
                  # General metrics
                  self.metrics["totalTime"] = self.metricsValues["totalTime"]
                  self.metrics["totalPatients"] = self.metricsValues["totalPatients"]

                  # Proportions of patients
                  self.metrics["proportionCriticalPatients"] = self.metricsValues["totalCriticalPatients"] / self.metricsValues["totalPatients"]
                  self.metrics["proportionUrgentPatients"] = self.metricsValues["totalUrgentPatients"] / self.metricsValues["totalPatients"]
                  self.metrics["proportionModeratePatients"] = self.metricsValues["totalModeratePatients"] / self.metricsValues["totalPatients"]
                  self.metrics["proportionLowPatients"] = self.metricsValues["totalLowPatients"] / self.metricsValues["totalPatients"]
                  self.metrics["proportionNonUrgentPatients"] = self.metricsValues["totalNonUrgentPatients"] / self.metricsValues["totalPatients"]
                  
                  # Financial metrics
                  self.metrics["totalFinancials"] = self.metricsValues["totalFinancials"]
                  self.metrics["averageRevenuePerPatient"] = self.metricsValues["totalFinancials"] / self.metricsValues["totalPatients"]
                  self.metrics["hospitalEntryRate"] = self.metricsValues["totalEnterHospital"] / self.metricsValues["totalPatients"]
      
      def _isWarmUpOver_(self):
            """ Checks if the warm up period is over """
            return self.env.now > self.variables["GENERAL_SETTINGS"]["warmUpPeriod"]
      
      def __generator__(self):
            """ Generates patients"""
            patient_id = 0  # Starting counter
            
            while True:
                  patient_id += 1  # Increment ID for each new patient
                  # Create a new patient object for each process
                  patient = {
                        "id": patient_id, 
                        "priority": None, 
                        "enterHospital": None, 
                        "time_in_system": 0
                  }
                  
                  # Start a new process with the fresh patient object
                  self.env.process(self.__activity__(patient))
                  
                  # Wait for next arrival
                  timeBetweenArrivals = random.expovariate(1/self.variables["ARRIVAL"]["arrivalRate"])
                  yield self.env.timeout(timeBetweenArrivals) # Let other patients arrive
                  if self._isWarmUpOver_():
                        self.metricsValues["totalTime"] = self.env.now
      
      def __activity__(self, patient):
            """ Simulates activity of the patients """

            if (self._isWarmUpOver_()):
                  print(f"Patient {patient['id']} arrived at {self.env.now}")
                  self.metricsValues["totalPatients"] += 1
                  print(f"Total patients: {self.metricsValues['totalPatients']}")

            # 1st Stage: Reception
            yield from self.activity_reception(patient)  # Use yield from to maintain generator
            if (patient["priority"] == "non-urgent"):
                if (self._isWarmUpOver_()):
                      self.metricsValues["totalNonUrgentPatients"] += 1
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
                    if (self._isWarmUpOver_()):
                      self.metricsValues["totalNonUrgentPatients"] += 1
                    self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo="Patient exited due to non-urgent priority")
                    return  # Early return exits the patient from the system
            
            # 3rd Stage: Doctor
            yield from self.activity_doctor(patient)
            
            # Financials
            self.financials(patient)

            self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo=f"{'entering hospital' if patient['enterHospital'] == 'yes' else 'not entering hospital'} -- priority: {patient['priority']} -- Financials: ${self.metricsValues['totalFinancials']}")
      
      def __setUp__(self):
            """Set ups a simulation instance to be ran """
            self.env = sim.Environment()
            
            # Change the nurse resource to a PriorityResource
            self.receptionist = sim.Resource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["receptionist"])
            self.nurse = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["nurse"])
            self.doctor = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["doctor"])
            
            self.env.process(self.__generator__())
            self.env.run(until = self.variables["GENERAL_SETTINGS"]["totalSimulationTime"])

            # Update metrics before storing results
            self.update_metrics()
            
            # Print financial summary
            print("\n===== FINANCIAL SUMMARY =====")
            print(f"Total Revenue: ${self.metricsValues['totalFinancials']:.2f}")
            print(f"Patients Entering Hospital: {self.metricsValues['totalEnterHospital']} ({(self.metricsValues['totalEnterHospital']/self.metricsValues['totalPatients']*100):.1f}%)")
            print(f"Average Revenue Per Patient: ${(self.metricsValues['totalFinancials']/self.metricsValues['totalPatients']):.2f}")
            print("============================\n")
            
            # Storing results
            print("Metrics:", self.metrics)
            with open(self.variables["GENERAL_SETTINGS"]["csvFilePath"], "a") as file:
                  writer = csv.writer(file, delimiter = ",")
                  writer.writerow([metricValue for metricValue in self.metrics.values()])

      def start(self):
            # <<==>> ADD MULTIHIREADING HERE <<==>>
            with open(self.variables["GENERAL_SETTINGS"]["csvFilePath"], "w") as file:
                  writer = csv.writer(file, delimiter = ",")
                  writer.writerow([metricName for metricName in self.metrics.keys()])
            numberOfRuns = self.variables["GENERAL_SETTINGS"]["numberOfRuns"]
            for i in range(numberOfRuns):
                  self.__setUp__()
      
      
      ################
      ## FINANCIALS ##
      ################
      
      def financials(self, patient):
            """ Calculates the financials of the simulation """
            
            # All patients pay the general urgency fee
            self.metricsValues["totalFinancials"] += self.variables["FEES"]["generalUrgenceFee"]
            
            if patient["enterHospital"] == "yes":
                  # Add the appropriate hospital entry fee based on priority
                  if patient["priority"] == "critical":
                        self.metricsValues["totalFinancials"] += self.variables["FEES"]["enterHospitalCritical"]
                  elif patient["priority"] == "urgent":
                        self.metricsValues["totalFinancials"] += self.variables["FEES"]["enterHospitalUrgent"]
                  elif patient["priority"] == "moderate":
                        self.metricsValues["totalFinancials"] += self.variables["FEES"]["enterHospitalModerate"]
                  elif patient["priority"] == "low":
                        self.metricsValues["totalFinancials"] += self.variables["FEES"]["enterHospitalLow"]
                  
                  self.metricsValues["totalEnterHospital"] += 1
            else:
                  self.metricsValues["totalExitHospital"] += 1
      
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
            receptionTime = random.expovariate(1/self.variables["RECEPTION"]["receptionServiceTime"]["mean"])
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
            nurseTime = random.expovariate(1/self.variables["NURSE"]["nurseServiceTime"][patient["priority"]]["mean"])
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
            assert patient["priority"] is not None, f"Patient priority must be set before calling doctor activity, current priority: {patient['priority']}"
            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=True,
                                               patient_id=patient["id"],
                                               time=self.env.now)
            def doctorEvaluation(currentPriority):
                  """Stochastic evaluation following a categorical/discrete-probability distribution"""
                  match (currentPriority):
                        case "critical":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["totalCriticalPatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "urgent":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["totalUrgentPatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "moderate":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["totalModeratePatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "low":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["totalLowPatients"] += 1
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
            doctorTime = random.expovariate(1/self.variables["DOCTOR"]["doctorServiceTime"][patient["priority"]]["mean"])
            yield self.env.timeout(doctorTime)

            # Releasing resource
            patient["enterHospital"] = doctorEvaluation(patient["priority"])
            self.doctor.release(doctorRequest)

            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=False,
                                               patient_id=patient["id"],
                                               time=self.env.now)

if __name__ == "__main__":
      simulation = Simulation()
      simulation.start()