from __main__ import *
from globalVariables import *


class Elector(object):
    
    __idCounter = 0
    
    def __init__(self, passedCandidate):
        self.__ID = Elector.__idCounter
        Elector.__idCounter += 1
        self.candidate = passedCandidate
        
        self.B = DIFF_EXPEC_BENEFIT
        self.c = GLOBAL_COST_DUTY
        if IDENTICAL_Qs:
            self.q = IDENTICAL_Qs
        else:
            self.q = np.random.uniform(0+Q_UNIF_PARAM,1-Q_UNIF_PARAM)
         
    def __repr__(self):
        return str(self.__ID)
        
    def __eq__(self, other):
        return self.ID == other.ID

    def netUtilFromVote(self, alpha1, alpha2):
        #Net utility from voting is given by equation 3 in the paper:
        return (alpha1 + alpha2) * self.B/2 - self.c #gives R in the paper

    #Equation 5 in the paper
    def g(self, n_A, n_B):
        """ g(q, M) denotes the probability of being pivotal as a function
        of the equilibrium probability of voting of all voters """
        if self.candidate == "A":
            new_n_A = n_A - self.q # everyone else's preferred candidate
            new_n_B = n_B
            if new_n_A != 0 and new_n_B != 0:
                result = skellam.pmf(-1, new_n_A, new_n_B)
                result += skellam.pmf(0, new_n_A, new_n_B)
            else:
                result = 0
        elif self.candidate == "B":
            new_n_A = n_A
            new_n_B = n_B - self.q # everyone else's preferred candidate
            if new_n_A != 0 and new_n_B != 0:
                result = skellam.pmf(-1, new_n_B, new_n_A)
                result += skellam.pmf(0, new_n_B, new_n_A)
            else:
                result = 0
        else:
            print "ERROR: elector " + str(self.ID) + " has no prefered candidate."
    
        return result * G_RESCALE_FACTOR
   
    def K(self, n_A, n_B):
        return K_RESCALE_FACTOR * np.sign( self.g(n_A, n_B) - 2*self.c)
    
    # q is initialized randomly, but it needs to be updated at each iteration    
    def update_q(self, n_A, n_B):
        self.q += self.K(n_A, n_B)
        if self.q < 0:
            self.q = 0
        elif self.q > 1:
            self.q = 1
            
            