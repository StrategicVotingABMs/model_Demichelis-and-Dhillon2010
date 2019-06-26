from __main__ import *
from globalVariables import *

PIVOT_PROB_MATRIX = [[None] * N_PARTIES] * N_PARTIES

class Elector(object):
    
    __idCounter = 0
    learnRate = K_RESCALE_FACTOR
    
    @staticmethod
    def resetIDs():
        Elector.__idCounter = 0
        
    def __init__(self):
        self.id = Elector.__idCounter
        Elector.__idCounter += 1
        self.cost = None
        self.voteProb = None
        self.utilities = [None] * N_PARTIES
        self.expUtilities = [None] * N_PARTIES
        self.mostPreferred = None
        self.leastPreferred = None
        self.currentVote = None

    def __repr__(self):
        return str(self.__ID)
        
    def __eq__(self, other):
        return self.ID == other.ID

    #calculate the sincere utility - that is, without/before strategic conside-
    #rations - that this elector assigns for all parties and stores them:
    def defineUtilities(self, distribution, ptyRankWeights):
        #Generate utilities of each party for this elector:
        utilities = GlobalFuncs.randUtilities(N_PARTIES, distribution, utilsRNG)
        utilities = -np.sort(-utilities)
        #rescale utilities bounding the from below at zero:
        if RESCALE_UTILITIES:
            minUtils = min(utilities)
            utilitiesRange = (max(utilities)-minUtils)
            utilities = (utilities - minUtils) / utilitiesRange
        #Make sure utilities match with party ranks:
        ptyRanks = list(range(N_PARTIES)) #randomly rank preference over parties
        ptyRanks = GlobalFuncs.weighted_shuffle(ptyRanks, ptyRankWeights+1, utilsRNG)
        # utilsRNG.shuffle(ptyRanks)
        for u, rank in enumerate(ptyRanks):
            self.utilities[rank] = utilities[u]
        #identify who's the sincerely least prefered party of this elector:
        self.leastPrefered = ptyRanks[-1]
        #identify this elector's current vote as the one with greatest utility:
        self.mostPreferred = GlobalFuncs.argmax_randTies(self.utilities, utilsRNG)
        self.currentVote = self.mostPreferred


    def calcExpUtilities(self, expVotes, skellamCDFvals, skellam0PMFvals, skellam1PMFvals, algorithm):
        #parties' expected votes disregarding this elector's vote:
        expVotesMinus1 = copy.deepcopy(expVotes)
        expVotesMinus1[self.currentVote] -= 1
        # in case decreasing 1 from expected votes leads to a negative value,
        # we should default it back to zero since negative expected votes
        # make no sense:
        if expVotesMinus1[self.currentVote] < 0:
            expVotesMinus1[self.currentVote] = 0
        
        #current strategic utility calculation for each party, given each
        #pair of parties:
        for i in range(N_PARTIES):
            nu_ll = 0
            for j in range(N_PARTIES):
                if i != j: #don't compare utility of a party against itself

                    if algorithm == "naive_64bits_precision":
                        nu_ll += self.utilsUpdate_naive_64(i, j, expVotes, expVotesMinus1)
                    elif algorithm == "mem_64bits_precision":
                        nu_ll += self.utilsUpdate_mem_64(i, j, expVotes, expVotesMinus1,\
                                                          skellamCDFvals, skellam0PMFvals, skellam1PMFvals)
                    elif algorithm == "mem_arbitrary_precision":
                        nu_ll += self.utilsUpdate_mem_arbitrary(i, j, expVotes, expVotesMinus1,\
                                                          skellamCDFvals, skellam0PMFvals, skellam1PMFvals)
                    else:
                        sys.exit("ERROR: algorithm type passed to function " \
                                 "calcStrategicUtils() doesn't exist.")                    
            self.expUtilities[i] = nu_ll

        #force weighted utility of the originally least prefered party to
        #be the smalles for this elector:
        self.expUtilities[self.leastPrefered] = -INFINITY
        #update this elector's vote choice:
        self.currentVote = GlobalFuncs.argmax_randTies(self.expUtilities, utilsRNG)


    def utilsUpdate_naive_64(self, i, j, expectedVotes, expVotesMinus1):
        #Pivot probs; parties i,j
        equalProb = skellam.pmf(0, max(MACHINE_EPSILON, expVotesMinus1[i]),
                                   max(MACHINE_EPSILON, expVotesMinus1[j]))
        oneLessProb = skellam.pmf(-1, max(MACHINE_EPSILON, expVotesMinus1[i]),
                                   max(MACHINE_EPSILON, expVotesMinus1[j]))
        #Pivot probs; other pairs, given i or j:
        not_i_or_j = [x for x in range(N_PARTIES) if x not in [i,j]]
        pairs = [(x,y) for x in [i,j] for y in not_i_or_j]
        topTwoProb = 1
        for pair in pairs:
            topTwoProb *= 1 - skellam.cdf(-1, max(MACHINE_EPSILON, expectedVotes[pair[0]]),
                                             max(MACHINE_EPSILON, expectedVotes[pair[1]]))
        #new weighted utilities:
        pivotProb = ((1/2)*equalProb + (3/2)*oneLessProb) * topTwoProb
        utilityDiff = self.utilities[i] - self.utilities[j]
        return utilityDiff * pivotProb
    

    def utilsUpdate_mem_64(self, i, j, expectedVotes, expVotesMinus1, skellamCDFvals, skellam0PMFvals, skellam1PMFvals):
        #Pivot probs; parties i,j
        skPMFparams = (max(MACHINE_EPSILON,expVotesMinus1[i]), max(MACHINE_EPSILON,expVotesMinus1[j]))
        if skPMFparams not in skellam0PMFvals:
            skellam0PMFvals[skPMFparams] = skellam.pmf(0,skPMFparams[0], skPMFparams[1])
            skellam1PMFvals[skPMFparams] = skellam.pmf(-1,skPMFparams[0], skPMFparams[1])
        equalProb = skellam0PMFvals[skPMFparams]
        oneLessProb = skellam1PMFvals[skPMFparams]

        #Pivot probs; other pairs, given i or j:
        not_i_or_j = [x for x in range(N_PARTIES) if x not in [i,j]]
        pairs = [(x,y) for x in [i,j] for y in not_i_or_j]
        topTwoProb = 1
        for pair in pairs:
            skCDFparams = (max(MACHINE_EPSILON,expectedVotes[pair[0]]), max(MACHINE_EPSILON,expectedVotes[pair[1]]))
            if skCDFparams not in skellamCDFvals:
                skellamCDFvals[skCDFparams] = 1 - skellam.cdf(-1,skCDFparams[0], skCDFparams[1])
            topTwoProb *= skellamCDFvals[skCDFparams]
            
        #new weighted utilities:
        pivotProb = ((1/2)*equalProb + (3/2)*oneLessProb) * topTwoProb
        utilityDiff = self.utilities[i] - self.utilities[j]
        return utilityDiff * pivotProb

            
    def utilsUpdate_mem_arbitrary(self, i, j, expectedVotes, expVotesMinus1, skellamCDFvals, skellam0PMFvals, skellam1PMFvals):
        #Pivot probs; parties i,j
        skPMFparams = (max(MACHINE_EPSILON,expVotesMinus1[i]), max(MACHINE_EPSILON,expVotesMinus1[j]))
        if skPMFparams not in skellam0PMFvals:
            skellam0PMFvals[skPMFparams] = mp.mpmathify(skellam.pmf(0,skPMFparams[0], skPMFparams[1]), strings=True)
            skellam1PMFvals[skPMFparams] = mp.mpmathify(skellam.pmf(-1,skPMFparams[0], skPMFparams[1]), strings=True)
        equalProb = skellam0PMFvals[skPMFparams]
        oneLessProb = skellam1PMFvals[skPMFparams]
        
        #Pivot probs; other pairs, given i or j:
        not_i_or_j = [x for x in range(N_PARTIES) if x not in [i,j]]
        pairs = [(x,y) for x in [i,j] for y in not_i_or_j]
        topTwoProb = 1
        for pair in pairs:
            skCDFparams = (max(MACHINE_EPSILON,expectedVotes[pair[0]]), max(MACHINE_EPSILON,expectedVotes[pair[1]]))
            if skCDFparams not in skellamCDFvals:
                skellamCDFvals[skCDFparams] = mp.fsub(1, mp.mpmathify(skellam.cdf(-1,skCDFparams[0], skCDFparams[1]), strings=True), exact=True)
            topTwoProb = mp.fmul(topTwoProb, skellamCDFvals[skCDFparams])
            
        #new weighted utilities:
        pivotProb = mp.fmul(mp.fadd(mp.fmul(1/2,equalProb),mp.fmul(3/2,oneLessProb)), topTwoProb, exact=True)
        utilityDiff = mp.fsub(self.utilities[i], self.utilities[j], exact=True)
        return mp.fmul(utilityDiff, pivotProb, exact=True)


    # @staticmethod
    # def updatePivotalProbs(expVotes):
    #     PIVOT_PROB_MATRIX

    #voteProb (q) is initialized randomly, but it needs to be updated at each iteration    
    def update_voteProb(self):
        self.voteProb += np.sign( self.expUtilities[self.currentVote]- self.cost) * Elector.learnRate
        if self.voteProb < 0:
            self.voteProb = 0
        elif self.voteProb > 1:
            self.voteProb = 1


#-----------------------------------------------------------------------------#
# End of file electorClass.py
#-----------------------------------------------------------------------------#

