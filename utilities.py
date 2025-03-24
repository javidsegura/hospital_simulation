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
                  "nurse": colorama.Fore.YELLOW,
                  "doctor": colorama.Fore.MAGENTA,
                  "exit": colorama.Fore.GREEN
            }

            self.stageIndentation = {
                  "reception": 1,
                  "nurse": 2,
                  "doctor": 3,
                  "exit": 4
            }
      
      def eventPrint(self,
                     eventStage: str,
                     justArrived: bool,
                     patient_id: int,
                     time: float,
                     otherInfo: str = None
                     ):
            indentation = "\t" * self.stageIndentation[eventStage]
            if justArrived:
                  print(f"{indentation}{self.stageColors[eventStage]} PATIENT {patient_id} -- START {eventStage}{colorama.Style.RESET_ALL}  -- {otherInfo if otherInfo else ''}: entered at {round(time,2)} (clock)")
            else:
                  print(f"{indentation}{self.stageColors[eventStage]} PATIENT {patient_id} -- END {eventStage}{colorama.Style.RESET_ALL}  -- {otherInfo if otherInfo else ''}: finished at {round(time,2)} (clock)")