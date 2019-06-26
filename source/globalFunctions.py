 #-----------------------------------------------------------------------------#
# Global functions:
#-----------------------------------------------------------------------------#
from __main__ import *
from bisect import bisect_right

def argmax_randTies(data, RNGengine=np.random):
    data = np.array(data)
    max_vals = max(data)
    mask = data == max_vals
    temp = mask * RNGengine.random_sample(mask.shape)
    return temp.argmax()
    #return np.argmax(data)

def countVoteIntentions(passedElectors):
    nCandidates = len(passedElectors[0].utilities)
    voteIntentions = [0] * nCandidates
    for elector in passedElectors:
        voteIntentions[elector.currentVote] += 1
    return voteIntentions

#Function that efficiently checks whether two lists are identical:
def areIdentical(lhs, rhs):
    result = True
    if len(lhs) != len(rhs):
        result = False
    else:
        i = 0
        while result == True and i < len(lhs):
            if lhs[i] != rhs[i]:
                result = False
            i += 1
    return result

def randUtilities(nCandidates, distribution, RNGengine=np.random):
    if distribution == "uniform":
        #Sample 1-D policy preference from an uniform distribution:
        return RNGengine.uniform(0, 1, nCandidates)
    elif distribution == "stdnormal":
        #Sample 1-D policy preference from a normal distribution:
        return  RNGengine.normal(0, 1, nCandidates)
    elif distribution == "1dirichlet":
        #Sample 1-d policy preference from one dirichlet distribution:
        return RNGengine.dirichlet(range(1, nCandidates+1))
    elif distribution == "2dirichlets":
        #Sample 1-d policy preference from two dirichlet distributions:
        coin = RNGengine.randint(0,2)
        if coin == 0:
            return RNGengine.dirichlet(range(1, nCandidates+1))
        else:
            return RNGengine.dirichlet(range(nCandidates, 0, -1))
    elif distribution == "3dirichlets":
        #Sample 1-d policy preference from three dirichlet distributions:
        coin = RNGengine.randint(0,3)
        if coin == 0:
            return RNGengine.dirichlet(range(1, nCandidates+1))
        elif coin == 1:
            return RNGengine.dirichlet(range(nCandidates, 0, -1))
        else:
            x = range(1, nCandidates+1)
            RNGengine.shuffle(x)
            return RNGengine.dirichlet(x)
    elif distribution == "logistic":
        return RNGengine.logistic(2,1,nCandidates)
    elif distribution == "beta":
        return RNGengine.beta(RNGengine.uniform(0.01,5),RNGengine.uniform(0.01,5),nCandidates).transpose()
    elif distribution == "powerlaw":
        return RNGengine.power(2,nCandidates)
    else:
        sys.exit("ERROR: invalid distribution name was passed to the " \
                 "randUtilities() function.")

# below function was taken from Nicky van Foreest's blog:
# http://nicky.vanforeest.com/probability/weightedRandomShuffling/weighted.html
def weighted_shuffle(a, w, RNGengine=np.random):
    r = np.empty_like(a)
    cumWeights = np.cumsum(w)
    for i in range(len(a)):
         rnd = RNGengine.random_sample() * cumWeights[-1]
         j = bisect_right(cumWeights,rnd)
         #j = np.searchsorted(cumWeights, rnd, side='right')
         r[i]=a[j]
         cumWeights[j:] -= w[j]
    return r


#-----------------------------------------------------------------------------#
# End of file globalFunctions.py
#-----------------------------------------------------------------------------#
