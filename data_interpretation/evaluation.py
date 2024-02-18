import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

pd.set_option('display.float_format', '{:.2f}'.format)

df = pd.read_csv('/Users/javierdominguezsegura/Academics/College/Courses/SMUC/Topic 3 - DES/Theory/Final_project/md_andersons_results.csv')

average = df.mean() # Get average outcomes

la = df.describe() # Get descriptive statistics for each variable (column)

print(average ,la)

