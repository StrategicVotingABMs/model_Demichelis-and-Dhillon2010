from __main__ import *

#-----------------------------------------------------------------------------#
#Global variables:
#-----------------------------------------------------------------------------#
MAX_ITER = 1000
PRINT_AT_N_ITER = 1
SAVING_INTERVAL = 1
SAVE_FOLDER_DETAILED = "outputs_detailed/"
SAVE_FOLDER_CONVERGED = "outputs_converged/"
N_VOTERS = 1000             #N in the paper, must be natural

N_ITERS_FOR_CONVERGENCE = 10

TIED_CASE = skellam.pmf(0, N_VOTERS/2, N_VOTERS/2)
ONE_BEHIND_CASE = skellam.pmf(-1, N_VOTERS/2, N_VOTERS/2)

IDENTICAL_Qs = np.random.choice([False,np.random.uniform(0,1)], 1)[0]
Q_UNIF_PARAM = np.random.uniform(0,0.5)

# GLOBAL_COST_DUTY is little c in paper
GLOBAL_COST_DUTY = np.random.uniform(0,0.5) #(alpha1 + alpha2)/2 * 0.1
# We use the rescale factor so we are not stuck with really small alphas
K_RESCALE_FACTOR = np.random.uniform(0.00000000001,0.001)

G_RESCALE_FACTOR = 1 #1/(TIED_CASE+ONE_BEHIND_CASE)


DIFF_EXPEC_BENEFIT = 1      #B in the paper; set to 1 on page 877