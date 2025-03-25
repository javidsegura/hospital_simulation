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
            self.currentReceptionWaitingRoomCapacity = 0
            
            return None
      
      def __metrics__(self):
            """ Initializes metrics """
            self.metricsValues = {
                  #General metrics
                  "general_totalTime": 0,
                  "general_totalPatients": 0,
                  "proportion_totalCriticalPatients": 0,
                  "proportion_totalUrgentPatients": 0,
                  "proportion_totalModeratePatients": 0,
                  "proportion_totalLowPatients": 0,
                  "proportion_totalNonUrgentPatients": 0,
                  "proportion_totalPatientsDeclinedAccess": 0,
                  # Arrival metrics
                  "arrival_totalArrivalTime": 0,
                  # Reception metrics
                  "reception_totalServiceTime": 0,
                  "reception_totalWaitingInQueueTime": 0,
                  # Nurse metrics
                  "nurse_totalPatients": 0,
                  "nurse_totalPatientsModerate": 0,
                  "nurse_totalPatientsLow": 0,
                  "nurse_totalServiceTimeModerate": 0,
                  "nurse_totalServiceTimeLow": 0,
                  "nurse_totalWaitingInQueueTimeModerate": 0,
                  "nurse_totalWaitingInQueueTimeLow": 0,
                  # Doctor metrics
                  "doctor_totalPatients": 0,
                  "reception_totalDoctorPatients": 0,
                  "totalDoctorCriticalServiceTime": 0,
                  "totalDoctorCriticalPatients": 0,
                  "totalDoctorUrgentPatients": 0,
                  "totalDoctorModeratePatients": 0,
                  "totalDoctorLowPatients": 0,
                  "totalCriticalHospitalPatients": 0,
                  "totalUrgentHospitalPatients": 0,
                  "totalModerateHospitalPatients": 0,
                  "totalLowHospitalPatients": 0,
            }
            self.metrics = {
                  "general_totalTime": 0,
                  "general_totalPatients": 0,
                  "proportion_CriticalPatients": 0,
                  "proportion_UrgentPatients": 0,
                  "proportion_ModeratePatients": 0,
                  "proportion_LowPatients": 0,
                  "proportion_NonUrgentPatients": 0,
                  "proportion_totalPatientsDeclinedAccess": 0,
                  # Arrival metrics
                  "arrival_waitingTime_average": 0,
                  "arrival_waitingTime_total": 0,
                  # Reception metrics
                  "reception_serviceTime_duration_average": 0,
                  "reception_serviceTime_duration_total": 0,
                  "reception_waitingInQueue_duration_average": 0,
                  "reception_waitingInQueue_duration_total": 0,
                  # Nurse metrics
                  "nurse_proportion_moderatePatients": 0,
                  "nurse_proportion_lowPatients": 0,
                  # "averageNurseCriticalServiceTime": self.metricsValues["totalNurseCriticalServiceTime"] / self.metricsValues["totalNurseCriticalPatients"],
                  # # Doctor metrics
                  # "averageDoctorServiceTime": self.metricsValues["totalDoctorServiceTime"] / self.metricsValues["totalDoctorPatients"],
                  # "proportionDoctorUrgentHospitalization": self.metricsValues["totalDoctorUrgentPatients"] / self.metricsValues["totalDoctorPatients"]
            
            }

      def update_metrics(self):
            # Only calculate proportions if we have patients
            if self.metricsValues["general_totalPatients"] > 0:
                  # General metrics
                  self.metrics["general_totalTime"] = self.metricsValues["general_totalTime"]
                  self.metrics["general_totalPatients"] = self.metricsValues["general_totalPatients"]
                  # Proportions of patients
                  self.metrics["proportion_CriticalPatients"] = self.metricsValues["proportion_totalCriticalPatients"] / self.metricsValues["general_totalPatients"]
                  self.metrics["proportion_UrgentPatients"] = self.metricsValues["proportion_totalUrgentPatients"] / self.metricsValues["general_totalPatients"]
                  self.metrics["proportion_ModeratePatients"] = self.metricsValues["proportion_totalModeratePatients"] / self.metricsValues["general_totalPatients"]
                  self.metrics["proportion_LowPatients"] = self.metricsValues["proportion_totalLowPatients"] / self.metricsValues["general_totalPatients"]
                  self.metrics["proportion_NonUrgentPatients"] = self.metricsValues["proportion_totalNonUrgentPatients"] / self.metricsValues["general_totalPatients"]
                  self.metrics["proportion_totalPatientsDeclinedAccess"] = self.metricsValues["proportion_totalPatientsDeclinedAccess"]
                  # Arrival
                  self.metrics["arrival_waitingTime_average"] = self.metricsValues["arrival_totalArrivalTime"] / self.metricsValues["general_totalPatients"]
                  self.metrics["arrival_waitingTime_total"] = self.metricsValues["arrival_totalArrivalTime"] 
                  # Reception
                  self.metrics["reception_serviceTime_duration_average"] = self.metricsValues["reception_totalServiceTime"] / self.metricsValues["general_totalPatients"]
                  self.metrics["reception_serviceTime_duration_total"] = self.metricsValues["reception_totalServiceTime"] 
                  self.metrics["reception_waitingInQueue_duration_average"] = self.metricsValues["reception_totalWaitingInQueueTime"] / self.metricsValues["general_totalPatients"]
                  self.metrics["reception_waitingInQueue_duration_total"] = self.metricsValues["reception_totalWaitingInQueueTime"] 
                  
                  # Nurse
                  self.metrics["nurse_proportion_moderatePatients"] = self.metricsValues["nurse_totalPatientsModerate"] / self.metricsValues["nurse_totalPatients"]
                  self.metrics["nurse_proportion_lowPatients"] = self.metricsValues["nurse_totalPatientsLow"] / self.metricsValues["nurse_totalPatients"]
      
      def _isWarmUpOver_(self):
            """ Checks if the warm up period is over """
            return self.env.now >= self.variables["GENERAL_SETTINGS"]["warmUpPeriod"]
      
      def __generator__(self):
            """ Generates patients"""
            patient_id = 0  # Starting counter
            
            while True:
                  startGenarationTime = self.env.now
                  patient_id += 1  # Increment ID for each new patient
                  # Create a new patient object for each process
                  patient = {
                        "id": patient_id, 
                        "priority": None, 
                        "enterHospital": None, 
                        "time_in_system": 0
                  }
                  self.currentReceptionWaitingRoomCapacity += 1
                  
                  # Start a new process with the fresh patient object
                  self.env.process(self.__activity__(patient))
                  
                  # Wait for next arrival
                  timeBetweenArrivals = random.expovariate(1/self.variables["ARRIVAL"]["arrivalRate"])
                  yield self.env.timeout(timeBetweenArrivals) # Let other patients arrive
                  if self._isWarmUpOver_():
                        self.metricsValues["general_totalTime"] = self.env.now
                        self.metricsValues["arrival_totalArrivalTime"] += self.env.now - startGenarationTime
      
      def __activity__(self, patient):
            """ Simulates activity of the patients """

            if (self._isWarmUpOver_()):
                  self.metricsValues["general_totalPatients"] += 1

            # 1st Stage: Reception
            yield from self.activity_reception(patient)  # Use yield from to maintain generator
            if (patient["priority"] == "non-urgent"):
                if (self._isWarmUpOver_()):
                      self.metricsValues["proportion_totalNonUrgentPatients"] += 1
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
                      self.metricsValues["proportion_totalNonUrgentPatients"] += 1
                    self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo="Patient exited due to non-urgent priority")
                    return  # Early return exits the patient from the system
            
            # 3rd Stage: Doctor
            yield from self.activity_doctor(patient)

            self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo=f"{ 'entering hospital' if patient['enterHospital'] == 'yes' else 'not entering hospital' } -- priority: {patient['priority']}")
      
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
            
            # Storing results
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
      
      ##########################
      ## ACTIVITY SUBROUTINES ##
      ##########################
      def activity_reception(self, patient):
            if (self.currentReceptionWaitingRoomCapacity > self.variables["RESOURCES_CAPACITY"]["receptionWaitingRoom"]):
                  self.auxiliaryFunctions.eventPrint(eventStage = "arrival",
                                               justArrived = True,
                                               patient_id = patient["id"],
                                               time = self.env.now,
                                               otherInfo = "Patient exited prematurely.🚨🚨🚨System is OVERLOADED🚨🚨🚨")
                  patient["priority"] = "non-urgent"
                  self.metricsValues["proportion_totalPatientsDeclinedAccess"] += 1
                  return
            else:
                  self.auxiliaryFunctions.eventPrint(eventStage = "arrival",
                                               justArrived = True,
                                               patient_id = patient["id"],
                                               time = self.env.now,
                                               )
                  
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
            startReceptionRequestTime = self.env.now
            receptioninstRequest = self.receptionist.request()
            yield receptioninstRequest
            if (self._isWarmUpOver_()):
                  self.metricsValues["reception_totalWaitingInQueueTime"] += self.env.now - startReceptionRequestTime

            # Service time
            startReceptionServiceTime = self.env.now
            receptionTime = random.expovariate(1/self.variables["RECEPTION"]["receptionServiceTime"]["mean"])
            # Evaluation of the patient: 
            patient["priority"] = receptionEvaluation()
            yield self.env.timeout(receptionTime)
            endReceptionServiceTime = self.env.now
            if (self._isWarmUpOver_()):
                  self.metricsValues["reception_totalServiceTime"] += endReceptionServiceTime - startReceptionServiceTime

            # Releasing resource
            self.receptionist.release(receptioninstRequest)
            self.auxiliaryFunctions.eventPrint(eventStage = "reception",
                                               justArrived = False,
                                               patient_id = patient["id"],
                                               time = self.env.now,
                                               otherInfo = f"Classified as {patient['priority']}")
            self.currentReceptionWaitingRoomCapacity -= 1
      
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

            self.metricsValues["nurse_totalPatients"] += 1
            self.metricsValues[f"nurse_totalPatients{patient['priority'].capitalize()}"] += 1
            self.auxiliaryFunctions.eventPrint(eventStage="nurse",
                                               justArrived=True,
                                               patient_id=patient["id"],
                                               time=self.env.now)
            
            
            # Get priority based on patient category
            priority = self.priority_map.get(patient["priority"]) 
            
            # Requesting resource with priority (appending to priority queue)
            startNurseRequestTime = self.env.now
            nurseRequest = self.nurse.request(priority=priority)
            yield nurseRequest
            # if (self._isWarmUpOver_()):
            #       self.metricsValues["nurse_totalWaitingInQueueTime"] += self.env.now - startNurseRequestTime

            # Service time
            startNurseServiceTime = self.env.now
            nurseTime = random.expovariate(1/self.variables["NURSE"]["nurseServiceTime"][patient["priority"]]["mean"])
            yield self.env.timeout(nurseTime)
            # if (self._isWarmUpOver_()):
            #       self.metricsValues["nurse_totalServiceTime"] += self.env.now - startNurseServiceTime

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
                                    self.metricsValues["proportion_totalCriticalPatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "urgent":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalUrgentPatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "moderate":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalModeratePatients"] += 1
                              enterHospital = {
                                          "yes": self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100,
                                          "no": 1 - self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100
                                    }
                              return np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                        case "low":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalLowPatients"] += 1
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
            startDoctorRequestTime = self.env.now
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