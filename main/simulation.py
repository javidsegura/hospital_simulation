# BASIC CONFIGURATION

#ERROR: FROOM RED IT DOES NOT RESTART

import simpy as sim
import numpy as np
import random
import colorama 
import  csv

random.seed(2024)

colorama.init()

#PARAMETERS
end = 0.0 # Done 
total_reception_time, total_nurse_time, total_cubicle_time, total_bed_time = 0.0, 0.0, 0.0, 0.0 # Done
total_reception_queue, total_nurse_queue, total_cubicle_queue, total_bed_queue = 0.0, 0.0, 0.0, 0.0 # Done
total_time = 0.0 # Done
total_patients_reception, total_patients_nurse, total_patients_cubicle, total_patients_bed = 0,0,0,0 # Done
last_customer = 0.0 # Done
total_deceased = 0.0
total_recovered = 0.0
recepcionist_bill = 0
nurse_bill = 0
cubicle_bill = 0
bed_bill = 0
total_expense = 0
revenue_bill = 0


#VARIABLES 
home_waiting_interval = 30 # 30
mean_recepcionist = 7
mean_nurse = 25
mean_cubicle = 60
mean_bed = 180 # Some that arrive late may die sooner  
customers  = 100

#OTHERS 
n_of_runs = 1000 # 5000 runs
warm_up = 1140 # 1440

# Receptionist --> Nurse --> Doctor --> ICU (Bed) --> Deceased/Recovered
def generator(env, home_waiting_interval, mean_recepcionist,mean_nurse,
              mean_cubicle, mean_bed, bed,cubicle,nurse,recepcionist):
      patient_id = 1 
      global end, last_customer,total_time
      while True:
            env.process(activity(env,patient_id,mean_recepcionist, mean_nurse,
                                    mean_cubicle,mean_bed,bed,cubicle,nurse,recepcionist))
            if env.now > warm_up:
                  print("Warm up is over, the simulation is now running")
            time_between_arrivals = random.expovariate(1/home_waiting_interval)
            yield env.timeout(time_between_arrivals) #Register patient out 
            patient_id += 1 # Register new patient
            if env.now > warm_up:
                  total_time = env.now

def activity(env,patient_id, mean_recepcionist,mean_nurse, 
            mean_cubicle,mean_bed,bed,cubicle, nurse, recepcionist):
            global total_reception_queue, total_nurse_queue, total_cubicle_queue,total_bed_queue, total_patients_reception, total_patients_nurse, total_patients_cubicle, total_patients_bed, total_reception_time, total_nurse_time, total_cubicle_time, total_bed_time
            global total_recovered,total_deceased, last_customer

            # RECEPTION
            time_in_reception = env.now 
            print(f"{colorama.Fore.BLUE} ARRIVAL RECEPTION PATIENT {patient_id}{colorama.Style.RESET_ALL}: entered at {round(time_in_reception,2)} (clock)")
            req_reception = recepcionist.request()
            yield req_reception
            time_out_reception = env.now
            time_balance_reception = time_out_reception - time_in_reception
            
            print(f"{colorama.Fore.CYAN} \t START SERVICE RECEPTION PATIENT {patient_id}{colorama.Style.RESET_ALL}: entered reception at {round(time_out_reception,2)} (clock), after waiting {round(time_balance_reception,2)} minutes")
            reception_time = random.expovariate(1/mean_recepcionist)
            yield env.timeout(reception_time)
            recepcionist.release(req_reception)

            print(f"{colorama.Fore.MAGENTA} \t \t END SERVICE RECEPTION PATIENT {patient_id}{colorama.Style.RESET_ALL}: finished reception at {round(time_out_reception + reception_time,2)} (clock) in {round(reception_time,2)} minutes")
            if env.now > warm_up:
                  total_patients_reception += 1
                  total_reception_queue += time_balance_reception
                  total_reception_time += reception_time

                  
            # NURSE
            time_in_nurse = env.now
            print(f"{colorama.Fore.YELLOW} \t \t \t ARRIVAL NURSE PATIENT {patient_id}{colorama.Style.RESET_ALL} has started waiting for the nurse at {round(time_in_nurse,2)} (clock)")
            req_nurse = nurse.request()
            yield req_nurse
            time_out_nurse = env.now
            time_balance_nurse = time_out_nurse - time_in_nurse

            print(f"{colorama.Fore.CYAN} \t \t \t \t  START SERVICE NURSE PATIENT  {patient_id}{colorama.Style.RESET_ALL}: entered nurse at {round(time_out_nurse,2)} (clock), after waiting {round(time_balance_nurse,2)} minutes")
            nurse_time = random.expovariate(1 / mean_nurse)
            yield env.timeout(nurse_time)
            nurse.release(req_nurse)

            print(f"{colorama.Fore.MAGENTA} \t \t \t \t \t END SERVICE NURSE PATIENT {patient_id}{colorama.Style.RESET_ALL}: finished nurse at {round((time_out_nurse + nurse_time),2)} (clock) in {round(nurse_time,2)} minutes") 
            if env.now > warm_up:
                        total_patients_nurse += 1
                        total_nurse_queue += time_balance_nurse
                        total_nurse_time += nurse_time

            branching_1 = np.random.choice(["Doctor","Out"] ,p = [.95,.05])
            if branching_1 == "Doctor":
                        # CUBICLE
                        cublicle_in = env.now
                        print(f" {colorama.Fore.BLUE} \t \t \t \t \t \t ARRIVAL PATIENT CUBICLE {patient_id}{colorama.Style.RESET_ALL} has started waiting for the doctor at {round(cublicle_in,2)} (clock)")
                        req_cubicle = cubicle.request()
                        yield req_cubicle
                        cubicle_out = env.now
                        cubicle_balance = cubicle_out - cublicle_in

                        print(f"{colorama.Fore.CYAN} \t \t \t \t \t \t \t START SERVICE CUBICLE PATIENT {patient_id}{colorama.Style.RESET_ALL}: entered cubicle at {round(cubicle_out,2)} (clock), after waiting {round(cubicle_balance,2)} minutes")
                        cubicle_time = random.expovariate(1 / mean_cubicle)
                        yield env.timeout(cubicle_time)
                        cubicle.release(req_cubicle)
                        
                        print(f"{colorama.Fore.MAGENTA} \t \t \t \t \t \t \t \t END SERVICE CUBICLE PATIENT {patient_id}{colorama.Style.RESET_ALL}: finished cubicle at {round((cubicle_out + cubicle_time),2)} (clock) in {round(cubicle_time,2)} minutes")
                        if env.now > warm_up:
                              total_patients_cubicle += 1
                              total_cubicle_queue += cubicle_balance
                              total_cubicle_time += cubicle_time

                        branching_2 = np.random.choice(["Deceased", "ICU", "Out2"], p = [.03,.95,.02])
                        
                        if branching_2 == "ICU":
                              # ICU
                              bed_in = env.now
                              print(f"{colorama.Fore.BLUE}\t \t \t \t \t \t \t \t \tARRIVAL PATIENT ICU {patient_id}{colorama.Style.RESET_ALL} has started waiting for the bed at {round(bed_in,2)} (clock)")
                              req_bed = bed.request()
                              yield req_bed
                              bed_out = env.now
                              bed_balance = bed_out - bed_in

                                   
                              print(f"{colorama.Fore.CYAN} \t \t \t \t \t \t \t \t \t \t START SERVICE ICU PATIENT {patient_id}{colorama.Style.RESET_ALL}: entered ICU at {round(bed_out,2)} (clock), after waiting {round(bed_balance if bed_balance <60 else (bed_balance/60),2)} {"minutes" if bed_balance <60 else "hours"}")
                              bed_time = random.expovariate(1 / mean_bed)
                              yield env.timeout(bed_time)
                              bed.release(req_bed)

                              print(f"{colorama.Fore.MAGENTA} \t \t \t \t \t \t \t \t \t \t END SERVICE ICU PATIENT {patient_id}{colorama.Style.RESET_ALL}: finished ICU at {round((bed_out + bed_time),2)} (clock) in {round(bed_time,2)} hours")
                              if env.now > warm_up:
                                    total_patients_bed += 1
                                    total_bed_queue += bed_balance
                                    total_bed_time += bed_time

                              branching_3 = np.random.choice(["Deceased", "Out3"], p = [.25,.75]) 
                              # DECEASED BRANCHING 3
                              if branching_3 == "Deceased":
                                    print(f"{colorama.Fore.RED} \t \t \t \t \t \t \t \t \t \t \t DECEASED PATIENT {patient_id} {colorama.Style.RESET_ALL} has deceased at bed branch at {round((bed_time+bed_out)/60,2)} hours")
                                    if env.now > warm_up:
                                          total_deceased += 1
                                          last_customer += 1
                              else:
                                    # RECOVERED BRANCHING 3
                                    print(f"{colorama.Fore.GREEN} \t \t \t \t \t \t \t \t \t \t \t RECOVERED PATIENT {patient_id} {colorama.Style.RESET_ALL} has been recovered sucesfully after bed branch at {round((bed_time + bed_out)/60,2)} hours")
                                    if env.now > warm_up:
                                          total_recovered += 1
                                          last_customer += 1
                             
                        # DECEASED BRANCHING 2
                        elif branching_2 == "Deceased":
                                    print(f"{colorama.Fore.RED} \t \t \t \t \t \t \t \t \t DECEASED PATIENT {patient_id} {colorama.Style.RESET_ALL} has deceased at cubicle branch at {round((cubicle_time + cubicle_out)/60,2)} hours")
                                    if env.now > warm_up:
                                          total_deceased += 1
                                          last_customer += 1 # Know total amount of patients 
                        # RECOVERED BRANCHING 2
                        elif branching_2 == "Out2":
                              print(f"{colorama.Fore.GREEN} \t \t \t \t \t \t \t \t \t RECOVERED PATIENT{patient_id} {colorama.Style.RESET_ALL} has been recovered sucesfully after cubicle branch at {round((cubicle_time + cubicle_out)/60,2)} hours")
                              if env.now > warm_up:
                                    total_recovered += 1
                                    last_customer += 1
                                         
            # DECEASED BRANCHING 1                               
            elif branching_1 == "Out":
                        print(f"{colorama.Fore.GREEN} \t \t \t \t \t \t RECOVERED PATIENT {patient_id} {colorama.Style.RESET_ALL} has been said by the doctor to be okay at {round(nurse_time/60,2)} hours")
                        if env.now > warm_up:
                              total_recovered += 1
                              last_customer += 1 # Know total amount of patients 

print("\n ------------------- Welcome to the MD Anderson Cancer Center, Austin (TX) ------------------ \n")

with open("/Users/javierdominguezsegura/Academics/College/Courses/SMUC/Topic 3 - DES/Theory/Final_project/md_andersons_results.csv", "w") as file:
      writer = csv.writer(file, delimiter = ",")
      writer.writerow(["Average reception service time (min)", "Average nurse service time(min)","Average cubicle service time(hours)","Average bed service time(hours)",
                       "Average reception queue time(min)", "Average nurse queue time(min)","Average cubicle queue time(min)","Average bed queue time(min)",
                        "Total time operating(days)","Total patients","Total deceased", "Total recovered", "Ration deceased","Ratio recovered", "Total ratio",
                       "Receptionist bill ($)","Nurse bill ($)","Cubicle bill ($)","Bed bill ($)","Total expenditure ($)","Total revenue ($)","Total profit ($)",])



def run_simulation():

      env = sim.Environment()
      # Is the most optimized set of values for the resources?
      recepcionist = sim.Resource(env, capacity = 1) 
      nurse = sim.Resource(env, capacity = 2) 
      cubicle = sim.Resource(env, capacity = 4)
      bed = sim.Resource(env, capacity = 8) # ICU (intensive care unit)


      env.process(generator(env,home_waiting_interval,mean_recepcionist,mean_nurse,
                        mean_cubicle,mean_bed,bed,cubicle,nurse,recepcionist))
      
      env.run(until = 10080) # 7 days + 1 day (warm-up) - 11520

      recepcionist_bill = total_time * 2.25 * recepcionist.capacity
      nurse_bill = total_time * 3.50 * nurse.capacity
      cubicle_bill = total_time * 4 * cubicle.capacity
      bed_bill = total_time * 6 * bed.capacity
      total_expense = recepcionist_bill + nurse_bill + cubicle_bill + bed_bill
      revenue_bill = last_customer * 7500 
      
      with open("/Users/javierdominguezsegura/Academics/College/Courses/SMUC/Topic 3 - DES/Theory/Final_project/md_andersons_results.csv", "a") as file:
            writer = csv.writer(file, delimiter = ",")
            writer.writerow([round(total_reception_time/total_patients_reception,2) if total_patients_reception != 0 else 0 ,round(total_nurse_time/total_patients_nurse,2) if total_patients_nurse != 0 else 0,
                       round((total_cubicle_time/total_patients_cubicle)/60,2) if total_patients_cubicle != 0 else 0 ,round((total_bed_time/total_patients_bed)/60,2) if total_patients_bed != 0 else 0,
                       round(total_reception_queue/total_patients_reception,2) if total_patients_reception != 0 else 0 ,round(total_nurse_queue/total_patients_nurse,2),
                       round((total_cubicle_queue/total_patients_cubicle),2) if total_patients_cubicle != 0 else 0 ,round(total_bed_queue/total_patients_bed,2) if total_patients_bed != 0 else 0,
                       round((total_time/60)/24,2),last_customer,total_deceased, total_recovered, (total_deceased/last_customer) if last_customer != 0 else 0 ,(total_recovered/last_customer) if last_customer != 0 else 0, (total_deceased/last_customer + total_recovered/last_customer) if last_customer != 0 else 0,
                       round(recepcionist_bill,2),round(nurse_bill,2),round(cubicle_bill,2),round(bed_bill,2),
                       round(total_expense,2),round(revenue_bill,2),round(revenue_bill - total_expense,2)])
       

for i in range(n_of_runs): # Restart all parameters to 0, in order to avoid overlapping
      end = 0.0 # Done  
      total_reception_time, total_nurse_time, total_cubicle_time, total_bed_time = 0.0, 0.0, 0.0, 0.0 # Done
      total_reception_queue, total_nurse_queue, total_cubicle_queue, total_bed_queue = 0.0, 0.0, 0.0, 0.0 # Done
      total_time = 0.0 # Done
      total_patients_reception, total_patients_nurse, total_patients_cubicle, total_patients_bed = 0,0,0,0 # Done
      last_customer = 0 # Done
      total_deceased = 0.0
      total_recovered = 0.0
      recepcionist_bill = 0
      nurse_bill = 0
      cubicle_bill = 0  
      bed_bill = 0
      total_expense = 0
      revenue_bill = 0
      run_simulation()
      

