from __main__ import *

#-----------------------------------------------------------------------------#
# Global variables:
#-----------------------------------------------------------------------------#

INFINITY = float('inf')
MACHINE_EPSILON = np.finfo(float).eps

### Initialize basic parameter values:
N_ELECTORS = int(mainParamsRNG.poisson(10000, 1)[0])
N_PARTIES = mainParamsRNG.randint(2,6)
MAX_ITER = 100000
N_ITERS_FOR_CONVERGENCE = 50
PRINT_AT_N_ITER = 1
DECREASING_K = True

### How to handle utilities:
RESCALE_UTILITIES = True
UTILITIES_DISTRIBUTION = "powerlaw"

#Calculates elector's expected utilities of candidates. Notice that
#algorithm type has to be defined, among the options:
#"naive_64bits_precision": no memoization, double precision
#"mem_64bits_precision": memoized, double precision
#"mem_arbitrary_precision": memoized, arbitrary precision
ALGORITHM_UTILS_UPDATE = "mem_64bits_precision"

### Initialize learning rate K and the epsilon factor:
K_RESCALE_FACTOR = 0.001
EPSILON = K_RESCALE_FACTOR /10
    
### defining whether Qs start identical or not:
#IDENTICAL_Qs = qRNG.choice([False, round(qRNG.uniform(0,1,1)[0], 2)], 1)[0]
IDENTICAL_Qs = False #round(qRNG.uniform(0,1,1)[0],2)

### initializing costs:
IDENTICAL_Cs = False #round(cRNG.uniform(0,1,1)[0],2)
COST_BETA_PARAM = cParamsRNG.choice([0.5, 1, 10], 1)[0]


#-----------------------------------------------------------------------------#
# End of file globalVariables.py
#-----------------------------------------------------------------------------#

