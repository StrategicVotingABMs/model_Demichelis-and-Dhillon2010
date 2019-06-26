#-----------------------------------------------------------------------------#
#
# Combined model: Cox (1994)'s Wasted Vote and Demichelis and Dhillon (2010)'s
#                 Strategic Abstention
# Date: 06-23-2018
#
#-----------------------------------------------------------------------------#


#-----------------------------------------------------------------------------#
# Engine commands (first lines required in ALL models; MAY NOT be changed)
#-----------------------------------------------------------------------------#
# from metadata import *
# model_metadata = get_model_metadata()
class Debug(object):
    
    isOn = False
    
    @staticmethod
    def Print(*args, **kwargs):
        print("".join(map(str,args)), **kwargs)

    @staticmethod
    def PrintIf(condition, *args, **kwargs):
        if condition:    
            print("".join(map(str,args)), **kwargs)


#-----------------------------------------------------------------------------#
# Importing libraries
#-----------------------------------------------------------------------------#
import copy
import importlib
import mpmath as mp
import numpy as np
from scipy.stats import skellam
import time


#-----------------------------------------------------------------------------#
#
# Hierarchical pseudo-RNG seeding
#
#-----------------------------------------------------------------------------#
mainSeed = np.random.randint(0, (2**32-1)/2)
Debug.Print("Started seed: " + str(mainSeed))

generalRNG = np.random.RandomState()
generalRNG.seed(mainSeed)

mainParamsRNG = np.random.RandomState(generalRNG.randint(0, (2**32-1)/2, 1)[0])
cParamsRNG = np.random.RandomState(generalRNG.randint(0, (2**32-1)/2, 1)[0])
qRNG = np.random.RandomState(generalRNG.randint(0, (2**32-1)/2, 1)[0])
cRNG = np.random.RandomState(generalRNG.randint(0, (2**32-1)/2, 1)[0])
utilsRNG = np.random.RandomState(generalRNG.randint(0, (2**32-1)/2, 1)[0])


#-----------------------------------------------------------------------------#
#
# Main simulation
# Strategic Abstention (Demichelis and Dhillon, 2010)
#
#-----------------------------------------------------------------------------#
initTime = time.time()

import globalFunctions as GlobalFuncs
importlib.reload(GlobalFuncs)

import globalVariables
importlib.reload(globalVariables)
from globalVariables import *

import electorClass
importlib.reload(electorClass)
from electorClass import *

# outputs = DatabaseAPI(mainSeed, model_metadata)


################################################################################
# Initializing the World
################################################################################

electors = [None] * N_ELECTORS
initialQs = [None] * N_ELECTORS
costs = [None] * N_ELECTORS
expVotes = [0] * N_PARTIES
idealVotes = [0] *N_PARTIES

ptyRankWeights = GlobalFuncs.randUtilities(N_PARTIES, UTILITIES_DISTRIBUTION, utilsRNG)
ptyRankWeights = ptyRankWeights - min(ptyRankWeights) if min(ptyRankWeights) < 0 else ptyRankWeights

for i in range(0, N_ELECTORS):
    elector = Elector()
    elector.defineUtilities(UTILITIES_DISTRIBUTION, ptyRankWeights)
    idealVotes[elector.mostPreferred] += 1
    elector.cost = cRNG.beta(COST_BETA_PARAM, COST_BETA_PARAM, 1)[0] if not IDENTICAL_Cs else IDENTICAL_Cs
    costs[i] = elector.cost
    elector.voteProb = qRNG.uniform(0,1) if not IDENTICAL_Qs else IDENTICAL_Qs
    expVotes[elector.currentVote] += elector.voteProb
    initialQs[i] = elector.voteProb
    electors[i] = elector

# import matplotlib.pyplot as plt
# plt.bar(range(len(idealVotes)),idealVotes);plt.show()
# import sys
# sys.exit()

Debug.Print("initial expected votes: " + str(expVotes))
Debug.Print("\n")


################################################################################
# Main simulation loop
################################################################################

iter = 0
hardConvergedIters = 0
bounceConvergedIters = 0
converged = False
histExpecVotes = [[None] * N_PARTIES] * N_ITERS_FOR_CONVERGENCE

skellamCDFvals = {}
skellam0PMFvals = {}
skellam1PMFvals = {}

while hardConvergedIters < N_ITERS_FOR_CONVERGENCE \
    and bounceConvergedIters < N_ITERS_FOR_CONVERGENCE \
    and iter < MAX_ITER:

    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "iteration " + str(iter) + "     seed: " + str(mainSeed) + "    k: " + str(Elector.learnRate) )

    currentQs = [None] * N_ELECTORS

    newExpecVotes = [0] * N_PARTIES
    for elector in electors:
        elector.calcExpUtilities(expVotes, skellamCDFvals, skellam0PMFvals, skellam1PMFvals, ALGORITHM_UTILS_UPDATE)
        elector.update_voteProb()
        newExpecVotes[elector.currentVote] += elector.voteProb
        currentQs[elector.id] = elector.voteProb
    
    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "new expected votes: " + str(newExpecVotes))

    expVotes = copy.deepcopy(newExpecVotes)

    # outputs["avgQ"] = np.mean(currentQs)
    # for pty in range(N_PARTIES):
    #   outputs["n_" + pty] = expVotes[pty]

    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "first elector's q: " + str(electors[0].voteProb))
    
    #Check for convergence:
    expVotesIdenticalToLast = True
    expVotesBouncing = True
    if iter < N_ITERS_FOR_CONVERGENCE:
        histExpecVotes[iter] = copy.deepcopy(expVotes)
    else:
        for idx in range(N_ITERS_FOR_CONVERGENCE-1):
            histExpecVotes[idx] = copy.deepcopy(histExpecVotes[idx+1])
            for j in range(N_PARTIES):
                expVotesIdenticalToLast = expVotesIdenticalToLast and abs(expVotes[j] - histExpecVotes[idx][j]) < EPSILON
                if idx > 1:
                    expVotesBouncing = expVotesBouncing and abs(histExpecVotes[idx][j] - histExpecVotes[idx-2][j]) < EPSILON
        histExpecVotes[N_ITERS_FOR_CONVERGENCE-1] = copy.deepcopy(expVotes)
        
        if expVotesIdenticalToLast:
            hardConvergedIters += 1
        else:
            hardConvergedIters = 0

        if expVotesBouncing:
            bounceConvergedIters += 1
        else:
            bounceConvergedIters = 0

        # Decreasing K (learning rate) when bouncing convergence is detected:
        if DECREASING_K and bounceConvergedIters >= N_ITERS_FOR_CONVERGENCE:
             bounceConvergedIters = 0
             Elector.learnRate /= 10
             EPSILON = Elector.learnRate /10
    
    Debug.PrintIf(iter%PRINT_AT_N_ITER == 0, "\n")
    
    # for elector in electors:
    #     outputs["elec" + str(elector) + "q"] = float(elector.voteProb)
    #     outputs["elec" + str(elector) + "vote"] = int(elector.mostPreferred)

    if hardConvergedIters >= N_ITERS_FOR_CONVERGENCE or bounceConvergedIters >= N_ITERS_FOR_CONVERGENCE:
        converged = True

    # outputs.saveIterationToDatabase(iter, converged)

    iter += 1
    #end of the main while-loop


#after model stops:
if hardConvergedIters >= N_ITERS_FOR_CONVERGENCE:
    convergenceType = "hard_convergence"
elif bounceConvergedIters >= N_ITERS_FOR_CONVERGENCE:
    convergenceType = "bouncing_convergence"
else:
    convergenceType = "max_iteration_reached"


Debug.Print("Final expected votes: " + str(expVotes))
Debug.Print("Ended after " + str(iter) + " iterations.")
Debug.Print("With " + convergenceType + " convergence")
Debug.Print("Took " + str(round(time.time() - initTime, 3)) + " seconds.")


# outputs.update(TABLE_SIMULATIONS, T_SIM_VAR_EQUILIBRIUM_TYPE, convergenceType)
# outputs.update(TABLE_SIMULATIONS, T_SIM_VAR_RUNTIME, time.time() - initTime)
# outputs.update(TABLE_SIMULATIONS, T_SIM_VAR_TIME_CURRENT, 'current_timestamp')

Debug.Print("Finished seed: " + str(mainSeed) + " after " + str(round(time.time() - initTime, 3)) + " seconds.\n")


################################################################################
# Saving variables that are fixed across iterations:
################################################################################
# globalVars = {}
# globalVars["nElectors"] = N_ELECTORS
# for pty in range(N_PARTIES):
#     globalVars["sincereN_" + pty] = idealVotes[pty]
# globalVars["identical_Cs"] = not bool(IDENTICAL_Cs is False)
# globalVars["avgInitialCs"] = float(np.mean(costs))
# globalVars["sdInitialCs"] = float(np.std(costs))
# globalVars["identical_Qs"] = not bool(IDENTICAL_Qs is False)
# globalVars["avgInitialQs"] = float(np.mean(initialQs))
# globalVars["sdInitialQs"] = float(np.std(initialQs))
# globalVars["decreasingK"] = DECREASING_K
# globalVars["costBetaParam"] = COST_BETA_PARAM
# globalVars["initK"] = Elector.learnRate
# globalVars["final"] = Elector.learnRate
# for pty in range(N_PARTIES):
#     globalVars["finalN_" + pty] = expVotes[pty]
# for elector in electors:
#     globalVars["elec" + str(elector) + "c"] = float(elector.cost)
#     globalVars["elec" + str(elector) + "initQ"] = initialQs[elector.id]
#     globalVars["elec" + str(elector) + "finalQ"] = elector.voteProb
    
# outputs.update(TABLE_SIMULATIONS, T_SIM_VAR_SIM_VARS, globalVars)


#-----------------------------------------------------------------------------#
# End of file main.py
#-----------------------------------------------------------------------------#

