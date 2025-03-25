import random 
import os
import csv
import simpy as sim
import numpy as np

from utilities import AuxiliaryFunctions
import yaml

np.random.seed(42)
random.seed(42)



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
                  # 1. General metrics
                  "general_totalTime": 0,
                  "general_totalPatients": 0,
                  # 2. Proportions of patients
                  "proportion_totalCriticalPatients": 0,
                  "proportion_totalUrgentPatients": 0,
                  "proportion_totalModeratePatients": 0,
                  "proportion_totalLowPatients": 0,
                  "proportion_totalNonUrgentPatients": 0,
                  "proportion_totalPatientsDeclinedAccess": 0,
                  "proportion_totalPatientsLeftDueToWaiting": 0,
                  # 3. Arrival metrics
                  "arrival_totalArrivalTime": 0,
                  # 4. Reception metrics
                  "reception_totalServiceTime": 0,
                  "reception_totalWaitingInQueueTime": 0,
                  # 5. Nurse metrics
                  # 5.1 Proportions
                  "nurse_totalPatients": 0,
                  "nurse_totalPatientsModerate": 0,
                  "nurse_totalPatientsLow": 0,
                  # 5.2 Service time
                  "nurse_totalServiceTimeModerate": 0,
                  "nurse_totalServiceTimeLow": 0,
                  # 5.3 Waiting in queue
                  "nurse_totalWaitingInQueueTimeModerate": 0,
                  "nurse_totalWaitingInQueueTimeLow": 0,
                  # 5.4 Revaluations
                  # 5.4.1 Moderate
                  "nurse_revaluations_moderate_toCritical": 0,
                  "nurse_revaluations_moderate_toUrgent": 0,
                  "nurse_revaluations_moderate_toModerate": 0,
                  "nurse_revaluations_moderate_toLow": 0,
                  "nurse_revaluations_moderate_toNon-urgent": 0,
                  # 5.4.2 Low
                  "nurse_revaluations_low_toCritical": 0,
                  "nurse_revaluations_low_toUrgent": 0,
                  "nurse_revaluations_low_toModerate": 0,
                  "nurse_revaluations_low_toLow": 0,
                  "nurse_revaluations_low_toNon-urgent": 0,
                  # 6. Doctor metrics
                  # 6.1 Proportions
                  "doctor_totalPatients": 0,
                  "doctor_totalPatientsCritical": 0,
                  "doctor_totalPatientsUrgent": 0,
                  "doctor_totalPatientsModerate": 0,
                  "doctor_totalPatientsLow": 0,
                  # 6.2 Service time
                  "doctor_totalServiceTimeCritical": 0,
                  "doctor_totalServiceTimeUrgent": 0,
                  "doctor_totalServiceTimeModerate": 0,
                  "doctor_totalServiceTimeLow": 0,
                  # 6.3 Waiting in queue
                  "doctor_totalWaitingInQueueTimeCritical": 0,
                  "doctor_totalWaitingInQueueTimeUrgent": 0,
                  "doctor_totalWaitingInQueueTimeModerate": 0,
                  "doctor_totalWaitingInQueueTimeLow": 0,
                  # 6.4 Doctor Assesment
                  "doctor_assesment_criticalEnterHospitalCount": 0,
                  "doctor_assesment_urgentEnterHospitalCount": 0,
                  "doctor_assesment_moderateEnterHospitalCount": 0,
                  "doctor_assesment_lowEnterHospitalCount": 0,         
                  # 7. Financials 
                  "financials_revenue_total": 0,
                  "financials_expenses_total": 0,
                  "financials_hospital_enterCount": 0,
                  "financials_hospital_exitCount": 0         
            }
            self.metrics = {
                  # 1. General metrics
                  "general_totalTime": 0,
                  "general_totalPatients": 0,
                  # 2. Proportions of patients
                  "proportion_CriticalPatients": 0,
                  "proportion_UrgentPatients": 0,
                  "proportion_ModeratePatients": 0,
                  "proportion_LowPatients": 0,
                  "proportion_NonUrgentPatients": 0,
                  "proportion_totalPatientsDeclinedAccess": 0,
                  "proportion_totalPatientsLeftDueToWaiting": 0,
                  # 3. Arrival metrics
                  "arrival_waitingTime_average": 0,
                  "arrival_waitingTime_total": 0,
                  # 4. Reception metrics
                  # 4.1 Service time
                  "reception_serviceTime_duration_average": 0,
                  "reception_serviceTime_duration_total": 0,
                  # 4.2 Waiting in queue
                  "reception_waitingInQueue_duration_average": 0,
                  "reception_waitingInQueue_duration_total": 0,
                  # 5. Nurse metrics
                  # 5.1 Proportions
                  "nurse_proportion_moderatePatients": 0,
                  "nurse_proportion_lowPatients": 0,
                  # 5.2 Service time
                  "nurse_serviceTime_duration_moderate_average": 0,
                  "nurse_serviceTime_duration_moderate_total": 0,
                  "nurse_serviceTime_duration_low_average": 0,
                  "nurse_serviceTime_duration_low_total": 0,
                  # 5.3 Waiting in queue
                  # 5.3.1 Moderate
                  "nurse_waitingInQueue_duration_moderate_average": 0,
                  "nurse_waitingInQueue_duration_moderate_total": 0,
                  # 5.3.2 Low
                  "nurse_waitingInQueue_duration_low_average": 0,
                  "nurse_waitingInQueue_duration_low_total": 0,
                  # 5.4 Revaluations
                  # 5.4.1 Moderate
                  "nurse_revaluations_moderate_toCritical": 0,
                  "nurse_revaluations_moderate_toUrgent": 0,
                  "nurse_revaluations_moderate_toModerate": 0,
                  "nurse_revaluations_moderate_toLow": 0,
                  "nurse_revaluations_moderate_toNon-urgent": 0,
                  # 5.4.2 Low
                  "nurse_revaluations_low_toCritical": 0,
                  "nurse_revaluations_low_toUrgent": 0,
                  "nurse_revaluations_low_toModerate": 0,
                  "nurse_revaluations_low_toLow": 0,
                  "nurse_revaluations_low_toNon-urgent": 0,
                  # 6 Doctor metrics
                  # 6.1 Proportions
                  "doctor_proportion_totalPatients": 0,
                  "doctor_proportion_criticalPatients": 0,
                  "doctor_proportion_urgentPatients": 0,
                  "doctor_proportion_moderatePatients": 0,
                  "doctor_proportion_lowPatients": 0,
                  # 6.2 Service time
                  # 6.2.1 Critical
                  "doctor_serviceTime_duration_critical_average": 0,
                  "doctor_serviceTime_duration_critical_total": 0,
                  # 6.2.2 Urgent
                  "doctor_serviceTime_duration_urgent_average": 0,
                  "doctor_serviceTime_duration_urgent_total": 0,
                  # 6.2.3 Moderate
                  "doctor_serviceTime_duration_moderate_average": 0,
                  "doctor_serviceTime_duration_moderate_total": 0,
                  # 6.2.4 Low
                  "doctor_serviceTime_duration_low_average": 0,
                  "doctor_serviceTime_duration_low_total": 0,
                  # 6.3 Waiting in queue
                  # 6.3.1 Critical
                  "doctor_waitingInQueue_duration_critical_average": 0,
                  "doctor_waitingInQueue_duration_critical_total": 0,
                  # 6.3.2 Urgent
                  "doctor_waitingInQueue_duration_urgent_average": 0,
                  "doctor_waitingInQueue_duration_urgent_total": 0,
                  # 6.3.3 Moderate
                  "doctor_waitingInQueue_duration_moderate_average": 0,
                  "doctor_waitingInQueue_duration_moderate_total": 0,
                  # 6.3.4 Low
                  "doctor_waitingInQueue_duration_low_average": 0,
                  "doctor_waitingInQueue_duration_low_total": 0,
                  # 6.4 Assesment
                  "doctor_assesment_criticalEnterHospitalRatio": 0,
                  "doctor_assesment_urgentEnterHospitalRatio": 0,
                  "doctor_assesment_moderateEnterHospitalRatio": 0,
                  "doctor_assesment_lowEnterHospitalRatio": 0,
                  # 7. Financials
                  # 7.0 General
                  "financials_entryRate": 0,
                  # 7.1 Revenue
                  "financials_revenue_total": 0,
                  "financials_revenue_perPatientAverage": 0,
                  # 7.2 Expenses
                  "financials_expenses_total": 0,
                  "financials_expenses_perPatientAverage": 0,
                  # 7.3 Profit
                  "financials_profit_total": 0,
                  "financials_profit_perPatientAverage": 0
            }

      def update_metrics(self):
            # Only calculate proportions if we have patients
            if self.metricsValues["general_totalPatients"] > 0:
                  try:
                        # 1. General metrics
                        self.metrics["general_totalTime"] = self.metricsValues["general_totalTime"]
                        self.metrics["general_totalPatients"] = self.metricsValues["general_totalPatients"]
                        # 2. Proportions of patients
                        self.metrics["proportion_CriticalPatients"] = self.metricsValues["proportion_totalCriticalPatients"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_UrgentPatients"] = self.metricsValues["proportion_totalUrgentPatients"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_ModeratePatients"] = self.metricsValues["proportion_totalModeratePatients"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_LowPatients"] = self.metricsValues["proportion_totalLowPatients"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_NonUrgentPatients"] = self.metricsValues["proportion_totalNonUrgentPatients"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_totalPatientsLeftDueToWaiting"] = self.metricsValues["proportion_totalPatientsLeftDueToWaiting"] / self.metricsValues["general_totalPatients"]
                        self.metrics["proportion_totalPatientsDeclinedAccess"] = self.metricsValues["proportion_totalPatientsDeclinedAccess"]
                        # 3. Arrival
                        self.metrics["arrival_waitingTime_average"] = self.metricsValues["arrival_totalArrivalTime"] / self.metricsValues["general_totalPatients"]
                        self.metrics["arrival_waitingTime_total"] = self.metricsValues["arrival_totalArrivalTime"] 
                        # 4. Reception
                        # 4.1 Service time
                        self.metrics["reception_serviceTime_duration_average"] = self.metricsValues["reception_totalServiceTime"] / self.metricsValues["general_totalPatients"]
                        self.metrics["reception_serviceTime_duration_total"] = self.metricsValues["reception_totalServiceTime"] 
                        # 4.2 Waiting in queue
                        self.metrics["reception_waitingInQueue_duration_average"] = self.metricsValues["reception_totalWaitingInQueueTime"] / self.metricsValues["general_totalPatients"]
                        self.metrics["reception_waitingInQueue_duration_total"] = self.metricsValues["reception_totalWaitingInQueueTime"] 
                        # 5. Nurse
                        # 5.1 Proportions
                        self.metrics["nurse_proportion_moderatePatients"] = self.metricsValues["nurse_totalPatientsModerate"] / self.metricsValues["nurse_totalPatients"]
                        self.metrics["nurse_proportion_lowPatients"] = self.metricsValues["nurse_totalPatientsLow"] / self.metricsValues["nurse_totalPatients"]
                        # 5.2 Service time
                        # 5.2.1 Moderate
                        self.metrics["nurse_serviceTime_duration_moderate_average"] = self.metricsValues["nurse_totalServiceTimeModerate"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_serviceTime_duration_moderate_total"] = self.metricsValues["nurse_totalServiceTimeModerate"]
                        # 5.2.2 Low
                        self.metrics["nurse_serviceTime_duration_low_average"] = self.metricsValues["nurse_totalServiceTimeLow"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_serviceTime_duration_low_total"] = self.metricsValues["nurse_totalServiceTimeLow"]
                        # 5.3 Waiting in queue
                        # 5.3.1 Moderate
                        self.metrics["nurse_waitingInQueue_duration_moderate_average"] = self.metricsValues["nurse_totalWaitingInQueueTimeModerate"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_waitingInQueue_duration_moderate_total"] = self.metricsValues["nurse_totalWaitingInQueueTimeModerate"]
                        # 5.3.2 Low
                        self.metrics["nurse_waitingInQueue_duration_low_average"] = self.metricsValues["nurse_totalWaitingInQueueTimeLow"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_waitingInQueue_duration_low_total"] = self.metricsValues["nurse_totalWaitingInQueueTimeLow"]
                        # 5.4 Revaluations
                        # 5.4.1 Moderate
                        self.metrics["nurse_revaluations_moderate_toCritical"] = self.metricsValues["nurse_revaluations_moderate_toCritical"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_revaluations_moderate_toUrgent"] = self.metricsValues["nurse_revaluations_moderate_toUrgent"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_revaluations_moderate_toModerate"] = self.metricsValues["nurse_revaluations_moderate_toModerate"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_revaluations_moderate_toLow"] = self.metricsValues["nurse_revaluations_moderate_toLow"] / self.metricsValues["nurse_totalPatientsModerate"]
                        self.metrics["nurse_revaluations_moderate_toNon-urgent"] = self.metricsValues["nurse_revaluations_moderate_toNon-urgent"] / self.metricsValues["nurse_totalPatientsModerate"]
                        # 5.4.2 Low
                        self.metrics["nurse_revaluations_low_toCritical"] = self.metricsValues["nurse_revaluations_low_toCritical"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_revaluations_low_toUrgent"] = self.metricsValues["nurse_revaluations_low_toUrgent"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_revaluations_low_toModerate"] = self.metricsValues["nurse_revaluations_low_toModerate"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_revaluations_low_toLow"] = self.metricsValues["nurse_revaluations_low_toLow"] / self.metricsValues["nurse_totalPatientsLow"]
                        self.metrics["nurse_revaluations_low_toNon-urgent"] = self.metricsValues["nurse_revaluations_low_toNon-urgent"] / self.metricsValues["nurse_totalPatientsLow"]
                        # 6. Doctor
                        # 6.1 Proportions
                        self.metrics["doctor_proportion_totalPatients"] = self.metricsValues["doctor_totalPatients"] 
                        self.metrics["doctor_proportion_criticalPatients"] = self.metricsValues["doctor_totalPatientsCritical"] / self.metricsValues["doctor_totalPatients"]
                        self.metrics["doctor_proportion_urgentPatients"] = self.metricsValues["doctor_totalPatientsUrgent"] / self.metricsValues["doctor_totalPatients"]
                        self.metrics["doctor_proportion_moderatePatients"] = self.metricsValues["doctor_totalPatientsModerate"] / self.metricsValues["doctor_totalPatients"]
                        self.metrics["doctor_proportion_lowPatients"] = self.metricsValues["doctor_totalPatientsLow"] / self.metricsValues["doctor_totalPatients"]
                        # 6.2 Service time
                        # 6.2.1 Critical
                        self.metrics["doctor_serviceTime_duration_critical_average"] = self.metricsValues["doctor_totalServiceTimeCritical"] / self.metricsValues["doctor_totalPatientsCritical"]
                        self.metrics["doctor_serviceTime_duration_critical_total"] = self.metricsValues["doctor_totalServiceTimeCritical"]
                        # 6.2.2 Urgent
                        self.metrics["doctor_serviceTime_duration_urgent_average"] = self.metricsValues["doctor_totalServiceTimeUrgent"] / self.metricsValues["doctor_totalPatientsUrgent"]
                        self.metrics["doctor_serviceTime_duration_urgent_total"] = self.metricsValues["doctor_totalServiceTimeUrgent"]
                        # 6.2.3 Moderate
                        self.metrics["doctor_serviceTime_duration_moderate_average"] = self.metricsValues["doctor_totalServiceTimeModerate"] / self.metricsValues["doctor_totalPatientsModerate"]
                        self.metrics["doctor_serviceTime_duration_moderate_total"] = self.metricsValues["doctor_totalServiceTimeModerate"]
                        # 6.2.4 Low
                        self.metrics["doctor_serviceTime_duration_low_average"] = self.metricsValues["doctor_totalServiceTimeLow"] / self.metricsValues["doctor_totalPatientsLow"]
                        self.metrics["doctor_serviceTime_duration_low_total"] = self.metricsValues["doctor_totalServiceTimeLow"]
                        # 6.3 Waiting in queue
                        # 6.3.1 Critical
                        self.metrics["doctor_waitingInQueue_duration_critical_average"] = self.metricsValues["doctor_totalWaitingInQueueTimeCritical"] / self.metricsValues["doctor_totalPatientsCritical"]
                        self.metrics["doctor_waitingInQueue_duration_critical_total"] = self.metricsValues["doctor_totalWaitingInQueueTimeCritical"]
                        # 6.3.2 Urgent
                        self.metrics["doctor_waitingInQueue_duration_urgent_average"] = self.metricsValues["doctor_totalWaitingInQueueTimeUrgent"] / self.metricsValues["doctor_totalPatientsUrgent"]
                        self.metrics["doctor_waitingInQueue_duration_urgent_total"] = self.metricsValues["doctor_totalWaitingInQueueTimeUrgent"]
                        # 6.3.3 Moderate
                        self.metrics["doctor_waitingInQueue_duration_moderate_average"] = self.metricsValues["doctor_totalWaitingInQueueTimeModerate"] / self.metricsValues["doctor_totalPatientsModerate"]
                        self.metrics["doctor_waitingInQueue_duration_moderate_total"] = self.metricsValues["doctor_totalWaitingInQueueTimeModerate"]
                        # 6.3.4 Low
                        self.metrics["doctor_waitingInQueue_duration_low_average"] = self.metricsValues["doctor_totalWaitingInQueueTimeLow"] / self.metricsValues["doctor_totalPatientsLow"]
                        self.metrics["doctor_waitingInQueue_duration_low_total"] = self.metricsValues["doctor_totalWaitingInQueueTimeLow"]
                        # 6.4 Assesment
                        self.metrics["doctor_assesment_criticalEnterHospitalRatio"] = self.metricsValues["doctor_assesment_criticalEnterHospitalCount"] / self.metricsValues["doctor_totalPatientsCritical"]
                        self.metrics["doctor_assesment_urgentEnterHospitalRatio"] = self.metricsValues["doctor_assesment_urgentEnterHospitalCount"] / self.metricsValues["doctor_totalPatientsUrgent"]
                        self.metrics["doctor_assesment_moderateEnterHospitalRatio"] = self.metricsValues["doctor_assesment_moderateEnterHospitalCount"] / self.metricsValues["doctor_totalPatientsModerate"]
                        self.metrics["doctor_assesment_lowEnterHospitalRatio"] = self.metricsValues["doctor_assesment_lowEnterHospitalCount"] / self.metricsValues["doctor_totalPatientsLow"]
                        # 7. Financials
                        # 7.0 General
                        self.metrics["financials_entryRate"] = self.metricsValues["financials_hospital_enterCount"] / self.metricsValues["general_totalPatients"]
                        # 7.1 Revenue
                        self.metrics["financials_revenue_total"] = self.metricsValues["financials_revenue_total"]
                        self.metrics["financials_revenue_perPatientAverage"] = self.metricsValues["financials_revenue_total"] / self.metricsValues["general_totalPatients"]
                        # 7.2 Expenses
                        self.metrics["financials_expenses_total"] = self.metricsValues["financials_expenses_total"]
                        self.metrics["financials_expenses_perPatientAverage"] = self.metricsValues["financials_expenses_total"] / self.metricsValues["general_totalPatients"]
                        # 7.3 Profit
                        self.metrics["financials_profit_total"] = self.metricsValues["financials_revenue_total"] - self.metricsValues["financials_expenses_total"]
                        self.metrics["financials_profit_perPatientAverage"] = (self.metricsValues["financials_revenue_total"] - self.metricsValues["financials_expenses_total"]) / self.metricsValues["general_totalPatients"]
                  except Exception as e:
                        print(f"ERROR UPDATING METRICS: {e}")
      def _isWarmUpOver_(self):
            """ Checks if the warm up period is over """
            return self.env.now >= self.variables["GENERAL_SETTINGS"]["warmUpPeriod"]
      
      def __generator__(self):
            """ Generates patients"""
            patient_id = 0  # Starting counter
            
            for i in range(self.variables["GENERAL_SETTINGS"]["totalPatients"]):
                  startGenarationTime = self.env.now
                  patient_id += 1  # Increment ID for each new patient
                  # Create a new patient object for each process
                  patient = {
                        "id": patient_id, 
                        "priority": None, 
                        "enterHospital": None
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
      
      def check_patient_leaves_due_to_waiting(self, patient, wait_time):
            """
            Checks if a non-urgent patient will leave due to excessive waiting time
            
            Args:
                patient: The patient object
                wait_time: The time the patient has been waiting in minutes
                
            Returns:
                bool: True if patient leaves, False if patient stays
            """
            # Only apply this rule to non-urgent patients
            if patient["priority"] != "non-urgent":
                  return False
                  
            # Check if wait time exceeds threshold (30 minutes)
            if wait_time >= self.variables["PATIENT"]["patienceTime"]:
                  # 80% chance of leaving (8 out of 10)
                  if random.random() < self.variables["PATIENT"]["leaveChance"]:
                        if self._isWarmUpOver_():
                              self.metricsValues["proportion_totalPatientsLeftDueToWaiting"] += 1
                        return True
            
            return False
      
      def __activity__(self, patient):
            """ Simulates activity of the patients """
            arrival_time = self.env.now
            
            if (self._isWarmUpOver_()):
                  self.metricsValues["general_totalPatients"] += 1

            # 1st Stage: Reception
            yield from self.activity_reception(patient)  # Use yield from to maintain generator
            
            # Check if patient leaves due to waiting time after reception
            current_wait_time = self.env.now - arrival_time
            
            # Check for impatience after reception (for non-urgent patients)
            if self.check_patient_leaves_due_to_waiting(patient, current_wait_time):
                  self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                   justArrived=False,
                                                   patient_id=patient["id"],
                                                   time=self.env.now,
                                                   otherInfo=f"Patient left due to impatience after waiting {current_wait_time:.1f} minutes (non-urgent)")
                  return  # Patient leaves the system due to impatience
            
            # 2nd Stage: Nurse - All patients go to nurse now, including non-urgent
            if (patient["priority"] not in ["critical", "urgent"]):
                  # Check if patient leaves due to waiting time before nurse stage
                  current_wait_time = self.env.now - arrival_time
                  if self.check_patient_leaves_due_to_waiting(patient, current_wait_time):
                        self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                         justArrived=False,
                                                         patient_id=patient["id"],
                                                         time=self.env.now,
                                                         otherInfo=f"Patient left due to impatience after waiting {current_wait_time:.1f} minutes (non-urgent)")
                        return  # Patient leaves the system due to impatience
                  
                  yield from self.activity_nurse(patient)
                  
                  # Non-urgent patients leave after nurse assessment
                  if (patient["priority"] == "non-urgent"):
                        if (self._isWarmUpOver_()):
                              self.metricsValues["proportion_totalNonUrgentPatients"] += 1
                        self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                         justArrived=False,
                                                         patient_id=patient["id"],
                                                         time=self.env.now,
                                                         otherInfo="Patient exited after nurse assessment due to non-urgent priority")
                        return  # Exit after nurse assessment
            
            # Check if patient leaves due to waiting time before doctor stage
            current_wait_time = self.env.now - arrival_time
            if self.check_patient_leaves_due_to_waiting(patient, current_wait_time):
                  self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                   justArrived=False,
                                                   patient_id=patient["id"],
                                                   time=self.env.now,
                                                   otherInfo=f"Patient left due to impatience after waiting {current_wait_time:.1f} minutes (non-urgent)")
                  return  # Patient leaves the system due to impatience
            
            # 3rd Stage: Doctor
            yield from self.activity_doctor(patient)

            # Calculate financials
            self.financials(patient)

            self.auxiliaryFunctions.eventPrint(eventStage="exit",
                                                 justArrived=False,
                                                 patient_id=patient["id"],
                                                 time=self.env.now,
                                                 otherInfo=f"{ 'entering hospital' if patient['enterHospital'] == 'yes' else 'not entering hospital' } -- priority: {patient['priority']}\
                                                      -- Financials: {self.metricsValues['financials_revenue_total']}")
      
      def __setUp__(self):
            """Set ups a simulation instance to be ran """
            self.env = sim.Environment()
            
            # Change the nurse resource to a PriorityResource
            self.receptionist = sim.Resource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["receptionist"])
            self.nurse = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["nurse"])
            self.doctor = sim.PriorityResource(self.env, capacity=self.variables["RESOURCES_CAPACITY"]["doctor"])
            
            # Initialize totalExpenses to 0
            self.metricsValues["totalExpenses"] = 0
            
            self.env.process(self.__generator__())
            self.env.run()

            # Calculate expenses
            self.expenses(currentTime = self.env.now)

            # Update metrics before storing results
            self.update_metrics()
            
            # Print financial summary
            print("\n===== FINANCIAL SUMMARY =====")
            print(f"Total Revenue: ${self.metricsValues['financials_revenue_total']:.2f}")
            print(f"Total Expenses: ${self.metricsValues['financials_expenses_total']:.2f}")
            print(f"Total Profit: ${self.metricsValues['financials_revenue_total'] - self.metricsValues['financials_expenses_total']:.2f}")
            print(f"Patients Entering Hospital: {self.metricsValues['financials_hospital_enterCount']} ({(self.metricsValues['financials_hospital_enterCount']/self.metricsValues['general_totalPatients']*100):.1f}%)")
            print(f"Average Revenue Per Patient: ${(self.metricsValues['financials_revenue_total']/self.metricsValues['general_totalPatients']):.2f}")
            print(f"Average Expenses Per Patient: ${(self.metricsValues['financials_expenses_total']/self.metricsValues['general_totalPatients']):.2f}")
            print(f"Average Profit Per Patient: ${(self.metricsValues['financials_revenue_total'] - self.metricsValues['financials_expenses_total'])/self.metricsValues['general_totalPatients']:.2f}")
            print("============================\n")
            
            # Print patient leaves due to impatience
            print("\n===== PATIENT SUMMARY =====")
            print(f"Total patients: {self.metricsValues['general_totalPatients']}")
            print(f"Patients left due to impatience: {self.metricsValues['proportion_totalPatientsDeclinedAccess']} patients  - ({self.metricsValues['proportion_totalPatientsDeclinedAccess']/self.metricsValues['general_totalPatients']*100:.1f}%)")
            print("============================\n")
            
            # Storing results
            print("Metrics:", self.metrics)
            with open(self.variables["GENERAL_SETTINGS"]["csvFilePath"], "a") as file:
                  writer = csv.writer(file, delimiter = ",")
                  writer.writerow([metricValue for metricValue in self.metrics.values()])
                  print(f"LENGTH OF METRICS VALUES: {len(self.metrics.values())} vs header: {len(self.metrics.keys())}")

      def start(self):
            # <<==>> ADD MULTIHIREADING HERE <<==>>
            with open(self.variables["GENERAL_SETTINGS"]["csvFilePath"], "w") as file:
                  writer = csv.writer(file, delimiter = ",")
                  writer.writerow([metricName for metricName in self.metrics.keys()])
                  print(f">>LENGTH OF METRICS VALUES: {len(self.metrics.values())} vs header: {len(self.metrics.keys())}")
            numberOfRuns = self.variables["GENERAL_SETTINGS"]["numberOfRuns"]
            for i in range(numberOfRuns):
                  self.__setUp__()
      
      def financials(self, patient):
            """ Calculates the financials of the simulation """

            # All patients pay the general urgency fee
            self.metricsValues["financials_revenue_total"] += self.variables["FINANCIALS"]["FEES"]["generalUrgenceFee"]
            
            if patient["enterHospital"] == "yes":
                  # Add the appropriate hospital entry fee based on priority
                  if patient["priority"] == "critical":
                        self.metricsValues["financials_revenue_total"] += self.variables["FINANCIALS"]["FEES"]["enterHospitalCritical"]
                  elif patient["priority"] == "urgent":
                        self.metricsValues["financials_revenue_total"] += self.variables["FINANCIALS"]["FEES"]["enterHospitalUrgent"]
                  elif patient["priority"] == "moderate":
                        self.metricsValues["financials_revenue_total"] += self.variables["FINANCIALS"]["FEES"]["enterHospitalModerate"]
                  elif patient["priority"] == "low":
                        self.metricsValues["financials_revenue_total"] += self.variables["FINANCIALS"]["FEES"]["enterHospitalLow"]
                  
                  self.metricsValues["financials_hospital_enterCount"] += 1
            else:
                  self.metricsValues["financials_hospital_exitCount"] += 1
      
      def expenses(self, currentTime):
            """ Calculates the expenses of the simulation """
            # Receptionist Expenses = simulation time * nº of receptionists * receptionist salary per minute
            receptionistExpenses = currentTime * self.variables["RESOURCES_CAPACITY"]["receptionist"] * self.variables["FINANCIALS"]["SALARIES"]["receptionistPerMinute"]
            # Nurse Expenses = simulation time * nº of nurses * nurse salary per minute
            nurseExpenses = currentTime * self.variables["RESOURCES_CAPACITY"]["nurse"] * self.variables["FINANCIALS"]["SALARIES"]["nursePerMinute"]
            # Doctor Expenses = simulation time * nº of doctors * doctor salary per minute
            doctorExpenses = currentTime * self.variables["RESOURCES_CAPACITY"]["doctor"] * self.variables["FINANCIALS"]["SALARIES"]["doctorPerMinute"]
            
            self.metricsValues["financials_expenses_total"] = receptionistExpenses + nurseExpenses + doctorExpenses
      
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
                              newPriority=  np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    self.metricsValues[f"nurse_revaluations_moderate_to{newPriority.capitalize()}"] += 1
                              return newPriority
                        case "low":
                              priorities = {
                                          "critical": self.variables["NURSE"]["nurseAssesment"]["low"]["critical"]/100,
                                          "urgent": self.variables["NURSE"]["nurseAssesment"]["low"]["urgent"]/100,
                                          "moderate": self.variables["NURSE"]["nurseAssesment"]["low"]["moderate"]/100,
                                          "low": self.variables["NURSE"]["nurseAssesment"]["low"]["low"]/100,
                                          "non-urgent": self.variables["NURSE"]["nurseAssesment"]["low"]["non-urgent"]/100
                                    }
                              newPriority=  np.random.choice(list(priorities.keys()), p=list(priorities.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    self.metricsValues[f"nurse_revaluations_low_to{newPriority.capitalize()}"] += 1
                              return newPriority

            self.metricsValues["nurse_totalPatients"] += 1
            
            # Fix for the key error - handle non-urgent priority differently
            if patient["priority"] == "non-urgent":
                  # Just increment the counter without trying to use the priority as part of the key
                  pass  # We don't have a specific counter for non-urgent patients in nurse
            else:
                  # For other priorities, use the capitalized priority in the key
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
            
            # Fix the method name - add trailing underscore
            if self._isWarmUpOver_() and patient["priority"] != "non-urgent":
                self.metricsValues[f"nurse_totalWaitingInQueueTime{patient['priority'].capitalize()}"] += self.env.now - startNurseRequestTime

            # Service time
            startNurseServiceTime = self.env.now
            
            # Fix for non-urgent patients - use "low" priority service time as fallback
            if patient["priority"] == "non-urgent" and "non-urgent" not in self.variables["NURSE"]["nurseServiceTime"]:
                  # Use "low" priority service time for non-urgent patients
                  nurseTime = random.expovariate(1/self.variables["NURSE"]["nurseServiceTime"]["low"]["mean"])
            else:
                  nurseTime = random.expovariate(1/self.variables["NURSE"]["nurseServiceTime"][patient["priority"]]["mean"])
            
            yield self.env.timeout(nurseTime)
            
            # Fix the method name here too - add trailing underscore
            if self._isWarmUpOver_() and patient["priority"] != "non-urgent":
                self.metricsValues[f"nurse_totalServiceTime{patient['priority'].capitalize()}"] += self.env.now - startNurseServiceTime

            # Releasing resource
            if patient["priority"] != "non-urgent":
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
                                          True: self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100,
                                          False: 1 - self.variables["DOCTOR"]["doctorAssesment"]["critical"]/100
                                    }
                              enterHospital = np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    if (enterHospital):
                                          self.metricsValues["doctor_assesment_criticalEnterHospitalCount"] += 1
                              return enterHospital
                        case "urgent":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalUrgentPatients"] += 1
                              enterHospital = {
                                          True: self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100,
                                          False: 1 - self.variables["DOCTOR"]["doctorAssesment"]["urgent"]/100
                                    }
                              enterHospital = np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    if (enterHospital):
                                          self.metricsValues["doctor_assesment_urgentEnterHospitalCount"] += 1
                              return enterHospital
                        case "moderate":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalModeratePatients"] += 1
                              enterHospital = {
                                          True: self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100,
                                          False: 1 - self.variables["DOCTOR"]["doctorAssesment"]["moderate"]/100
                                    }
                              enterHospital = np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    if (enterHospital):
                                          self.metricsValues["doctor_assesment_moderateEnterHospitalCount"] += 1
                              return enterHospital
                        case "low":
                              if (self._isWarmUpOver_()):
                                    self.metricsValues["proportion_totalLowPatients"] += 1
                              enterHospital = {
                                          True: self.variables["DOCTOR"]["doctorAssesment"]["low"]/100,
                                          False: 1 - self.variables["DOCTOR"]["doctorAssesment"]["low"]/100
                                    }
                              enterHospital = np.random.choice(list(enterHospital.keys()), p=list(enterHospital.values()), size=1)[0]
                              if (self._isWarmUpOver_()):
                                    if (enterHospital):
                                          self.metricsValues["doctor_assesment_lowEnterHospitalCount"] += 1
                              return enterHospital
            self.metricsValues["doctor_totalPatients"] += 1
            self.metricsValues[f"doctor_totalPatients{patient['priority'].capitalize()}"] += 1
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
            if (self._isWarmUpOver_()):
                  self.metricsValues[f"doctor_totalWaitingInQueueTime{patient['priority'].capitalize()}"] += self.env.now - startDoctorRequestTime

            # Service time
            startDoctorServiceTime = self.env.now
            doctorTime = random.expovariate(1/self.variables["DOCTOR"]["doctorServiceTime"][patient["priority"]]["mean"])
            yield self.env.timeout(doctorTime)
            endDoctorServiceTime = self.env.now
            if (self._isWarmUpOver_()):
                  self.metricsValues[f"doctor_totalServiceTime{patient['priority'].capitalize()}"] += endDoctorServiceTime - startDoctorServiceTime

            # Releasing resource
            patient["enterHospital"] = "yes" if doctorEvaluation(patient["priority"]) else "no"
            self.doctor.release(doctorRequest)

            self.auxiliaryFunctions.eventPrint(eventStage="doctor",
                                               justArrived=False,
                                               patient_id=patient["id"],
                                               time=self.env.now)

if __name__ == "__main__":
      simulation = Simulation()
      simulation.start()