#It is important to import the project's other files after setting the seed
#to assure that the same seed will be used throughout
import csv
import random as rng
import numpy as np
from scipy.stats import skellam
from debug import Debug
from dataset import Dataset


#Declare the number of different seeds to try, and the number of times
#to use each seed
numRuns = 1



for run in range(numRuns):

    #If this is the first run, import the main simulation file
    if run == 0:
        import main
    #If this is not the first run, reload the main simulation file
    else:
        reload(main)