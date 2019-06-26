# -*- coding: utf-8 -*-
"""
@what: ABM implementation of Demichelis and Dhillon (2010)
"""

#from __main__ import *


#It is important to import the project's other files after setting the seed
#to assure that the same seed will be used throughout
import csv
import random as rng
import numpy as np
from scipy.stats import skellam
from debug import Debug
from dataset import Dataset
from globalVariables import *
from electorClass import Elector


#to turn printing off/on, simply set the following to False/True
Debug.isOn = False


seed = rng.randint(0, 2**32-1)
#set seed for BOTH numpy and random
rng.seed(seed)
np.random.seed(seed)

Debug.Print(seed)

output = Dataset(1)

################################################################################
# Initializing the World
################################################################################




Debug.Print("rescale factor is: " + str(G_RESCALE_FACTOR))

# Initialize mu_A and mu_B randomly 
mu_A = N_VOTERS_PREF_A = int(np.random.uniform(0, N_VOTERS))
mu_B = N_VOTERS_PREF_B = N_VOTERS - mu_A

Debug.Print("mu_A is: " + str(mu_A))
Debug.Print("mu_B is: " + str(mu_B))

#First two alphas are drawn from a skellam distribution with some upward rescale
alpha1 = skellam.pmf(0, mu_A, mu_B) #prob n1 == n2
alpha2 = skellam.pmf(-1, mu_A, mu_B)  #prob n1 == n2 - 1
alpha1 *= G_RESCALE_FACTOR
alpha2 *= G_RESCALE_FACTOR

Debug.Print("alpha1 is: " + str(alpha1))
Debug.Print("alpha2 is: " + str(alpha2) + "\n")

# Init empty lists of length N_VOTERS_PREF A and B
electorsA = [None] * N_VOTERS_PREF_A
electorsB = [None] * N_VOTERS_PREF_B



n_A = 0
for i in range(0, N_VOTERS_PREF_A):
    elector = Elector("A")
    n_A += elector.q
    electorsA[i] = elector

n_B = 0    
for i in range(0, N_VOTERS_PREF_B):
    elector = Elector("B")
    n_B += elector.q
    electorsB[i] = elector
    
Debug.Print("initial n_A: " + str(n_A))
Debug.Print("initial n_B: " + str(n_B))
Debug.Print("\n")


################################################################################
# Main simulation loop
################################################################################

iter = 0
convergedIters = 0
pastN_As = [None] * N_ITERS_FOR_CONVERGENCE
avgPastN_As = 0

while convergedIters < N_ITERS_FOR_CONVERGENCE and iter < MAX_ITER:

    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "iteration " + str(iter))
    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "first elector's q: " + str(electorsA[0].q))
    
    new_n_A = 0
    for elector in electorsA:
        elector.update_q(n_A, n_B)
        new_n_A += elector.q
    
    new_n_B = 0
    for elector in electorsB:
        elector.update_q(n_A, n_B)
        new_n_B += elector.q

    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "new n_A: " + str(new_n_A))
    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "new n_B: " + str(new_n_B))

    n_A = new_n_A
    n_B = new_n_B
    
    #Check for convergence:
    if iter < N_ITERS_FOR_CONVERGENCE:
        pastN_As[iter] = n_A
    else:
        for i in range(N_ITERS_FOR_CONVERGENCE-1):
            avgPastN_As += pastN_As[i]
            pastN_As[i] = pastN_As[i+1]
        pastN_As[N_ITERS_FOR_CONVERGENCE-1] = n_A
        avgPastN_As /= N_ITERS_FOR_CONVERGENCE
    
    if round(n_A,0) == round(avgPastN_As,0):
        convergedIters += 1
    else:
        convergedIters = 0
    
    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "\n")
    
    iter += 1

Debug.Print("Ended after " + str(iter) + " iterations.")


################################################################################
# Saving output of the convergence iteration:
################################################################################
output[0, "seed"] = seed

output[0, "mu_A"] = mu_A
output[0, "mu_B"] = mu_B

output[0, "identical_qs"] = IDENTICAL_Qs
output[0, "c"] = GLOBAL_COST_DUTY
output[0, "k_rescale"] = K_RESCALE_FACTOR
output[0, "g_rescale"] = G_RESCALE_FACTOR

output[0, "iter"] = iter

output[0, "n_A"] = n_A
output[0, "n_B"] = n_B


for elector in electorsA:
    output[0, "q_elec" + str(elector) + "ofA"] = elector.q
for elector in electorsB:
    output[0, "q_elec" + str(elector) + "ofB"] = elector.q

output.saveToFile(SAVE_FOLDER_CONVERGED + "detailed_" + str(seed) + ".csv")