# -*- coding: utf-8 -*-
"""
@what: ABM implementation of Stefano and Amrita (2010)
"""

#It is important to import the project's other files after setting the seed
#to assure that the same seed will be used throughout
import csv
import random as rng
import numpy as np
from scipy.stats import skellam
from debug import Debug

#to turn printing off/on, simply set the following to False/True
Debug.isOn = True


seed = rng.randint(0, 2**32-1)
#set seed for BOTH numpy and random
rng.seed(seed)
np.random.seed(seed)

Debug.Print(seed)

#-----------------------------------------------------------------------------#
#Global variables:
#-----------------------------------------------------------------------------#
MAX_ITER = 10
SAVE_AT_N_ITER = 2
N_VOTERS = 1000             #N in the paper, must be natural
VOTING_COST = None          #C in the paper
EXPEC_BENEFIT = None        #R in the paper
CIVIC_DUTY = None           #D in the paper
DIFF_EXPEC_BENEFIT = 1      #B in the paper; set to 1 on page 877


################################################################################
# Initializing the World
################################################################################

# We use the rescale factor so we are not stuck with really small alphas
Krescale_factor = 0.01
TIED_CASE = skellam.pmf(0, N_VOTERS/2, N_VOTERS/2)
ONE_BEHIND_CASE = skellam.pmf(-1, N_VOTERS/2, N_VOTERS/2)
rescale_factor = 1 #1/(TIED_CASE+ONE_BEHIND_CASE)

Debug.Print("rescale factor is: " + str(rescale_factor))

# Initialize mu_A and mu_B randomly 
mu_A = N_VOTERS_PREF_A = int(np.random.uniform(0, N_VOTERS))
mu_B = N_VOTERS_PREF_B = N_VOTERS - mu_A

Debug.Print("mu_A is: " + str(mu_A))
Debug.Print("mu_B is: " + str(mu_B))

#First two alphas are drawn from a skellam distribution with some upward rescale
alpha1 = skellam.pmf(0, mu_A, mu_B) #prob n1 == n2
alpha2 = skellam.pmf(-1, mu_A, mu_B)  #prob n1 == n2 - 1
alpha1 *= rescale_factor
alpha2 *= rescale_factor

Debug.Print("alpha1 is: " + str(alpha1))
Debug.Print("alpha2 is: " + str(alpha2))
Debug.Print("\n")

# GLOBAL_COST_DUTY is little c in paper
GLOBAL_COST_DUTY = 0.1 #(alpha1 + alpha2)/2 * 0.1

# Init empty lists of length N_VOTERS_PREF A and B
electorsA = [None] * N_VOTERS_PREF_A
electorsB = [None] * N_VOTERS_PREF_B

from electorClass import Elector

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

################################################################################
# Main simulation loop
################################################################################

iter = 0
while iter < MAX_ITER:

    Debug.PrintIf(iter%SAVE_AT_N_ITER == 0, "iteration " + str(iter))
    Debug.PrintIf(iter%SAVE_AT_N_ITER == 0, "first elector's q: " + str(electorsA[0].q))
    
    new_n_A = 0
    for elector in electorsA:
        elector.update_q(n_A, n_B)
        new_n_A += elector.q
    
    new_n_B = 0
    for elector in electorsB:
        elector.update_q(n_A, n_B)
        new_n_B += elector.q

    Debug.PrintIf(iter%SAVE_AT_N_ITER == 0, "new n_A: " + str(new_n_A))
    Debug.PrintIf(iter%SAVE_AT_N_ITER == 0, "new n_B: " + str(new_n_B))


    n_A = new_n_A
    n_B = new_n_B
    
    Debug.PrintIf(iter%SAVE_AT_N_ITER == 0, "\n")
    
    iter += 1
    
Debug.Print("Ended after " + str(iter) + " iterations.")



