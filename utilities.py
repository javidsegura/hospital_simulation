import simpy as sim
import colorama
import random 
import numpy as np


      
class AuxiliaryFunctions():
      def __init__(self,
                   variables: dict[str, int]
                   ):
            self.__stageColors__()
            self.variables = variables
            return None

      def __stageColors__(self):
            """ Returns the color of the stage """
            self.stageColors = {
                  "reception": colorama.Fore.BLUE,
                  "nurseWaiting": colorama.Fore.RED,
                  "nurse": colorama.Fore.YELLOW,
                  "doctorWaiting": colorama.Fore.GREEN,
                  "doctor": colorama.Fore.MAGENTA
            }

            self.stageIndentation = {
                  "reception": 1,
                  "nurseWaiting": 2,
                  "nurse": 3,
                  "doctorWaiting": 4,
                  "doctor": 5
            }
      
      def eventPrint(self,
                     eventStage: str,
                     isStart: bool,
                     patient_id: int,
                     time: float,
                     otherInfo: str = None
                     ):
            indentation = "\t" * self.stageIndentation[eventStage]
            if isStart:
                  print(f"{indentation}{self.stageColors[eventStage]} PATIENT {patient_id} -- START {eventStage}{colorama.Style.RESET_ALL}  -- {otherInfo}: entered at {round(time,2)} (clock)")
            else:
                  print(f"{indentation}{self.stageColors[eventStage]} PATIENT {patient_id} -- END {eventStage}{colorama.Style.RESET_ALL}  -- {otherInfo}: finished at {round(time,2)} (clock)")