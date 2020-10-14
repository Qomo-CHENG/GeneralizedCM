"""
@    Computing MI in parallel
@    This is the second option by equation: I(X; L) = H(L) - H(L|X)
@    Bonus: define the Gaussian mixture *straightforwardly* 
@    Wei Cheng, 28-08-2020
"""

from matplotlib import pyplot as plt
import numpy as np
import scipy.integrate
import scipy.special
import math
from tqdm import tqdm
import pickle
import collections
import scipy
from scipy.stats import multivariate_normal
import time
import multiprocessing  
from multiprocessing import Pool

def hammingw(z):
    '''Compute Hamming weights'''
    return bin(z).count('1') if type(z) != np.ndarray else np.array([hammingw(elem) for elem in z])

def normal2d(x_1, x_2, mu_1, mu_2, sigma): # Same sigma for the two leakages
    # 2D
    return 1./(2*np.pi*sigma**2) * np.exp(-((x_1-mu_1)**2+(x_2-mu_2)**2)/(2*sigma**2))

def leakage_function2d(t,x,y, sigma): 
    """Value of the bivariate leakage""" 
    #global sigma 
    leakages = Leakages_uniq[t]
    alphs = Leakages_alph[t]
    GMs = sum(alphs*normal2d(x, y, leakages[0,:], leakages[1,:], sigma))

    return GMs
 
def leakage_function2d_tot(x,y, sigma): 
    """Value of the bivariate leakage""" 
    #global sigma 
    leakages = Leakages_tot_uniq
    alphs = Leakages_tot_alph
    GMs_tot = sum(alphs*normal2d(x, y, leakages[0,:], leakages[1,:], sigma))
    #GMs_tot = sum(GMs_tot_tmp*alphs)

    return GMs_tot

def entropy_2d(t, sigma):
    #global sigma

    options={'limit':100, 'epsabs':1e-13, 'epsrel':1e-13}
    y = scipy.integrate.nquad(lambda x,y: -leakage_function2d(t,x,y,sigma) * math.log( leakage_function2d(t,x,y,sigma), 2) if leakage_function2d(t,x,y,sigma) != 0 else 0, 
        [[0-9*sigma, n+9*sigma], [0-9*sigma, n+9*sigma]], args=(), opts=[options, options])
        
    return y[0]

def entropy_2d_tot(sigma):
    #global sigma

    options={'limit':200, 'epsabs':1e-13, 'epsrel':1e-13}
    y = scipy.integrate.nquad(lambda x,y: -leakage_function2d_tot(x,y,sigma) * math.log( leakage_function2d_tot(x,y,sigma), 2) if leakage_function2d_tot(x,y,sigma) != 0 else 0, 
        [[0-9*sigma, n+9*sigma], [0-9*sigma, n+9*sigma]], args=(), opts=[options, options])

    return y[0]

def mi_2d(sigma):
    # Conditional entropy
    t2 = time.time()
    h = entropy_2d_tot(sigma)
    t3 = time.time()
    print("Time elapsed for tot: t=%0.08f \t sigma=%0.015f"%(t3-t2, sigma))
    t3 = time.time()
    for c in Classlist.keys():
        h -= len(Classlist[c]) * entropy_2d( Classlist[c][0], sigma ) / en
    
    t4 = time.time()
    print("Time elapsed for all k_i: t=%0.08f \t sigma=%0.015f"%(t4-t3, sigma))
    return h

def get_leak_noise_free(D, Nk, Nd, isSerial):
    """
        Generate the noise-free distribution
    """
    leakages = np.array([None for _ in range(Nk)])
    Nmodes = Nk**(D-1)
    
    for k in range(Nk): 
        # all possible randomness
        R = np.zeros((D, Nmodes),dtype=int)
        for i in range(D-1):
            R[i,:] = np.tile(np.repeat(np.arange(Nk),Nk**(D-2-i)),Nk**i)

        R_s = np.zeros(Nmodes,dtype=int) + k
        for i in range(D-1):
            R_s = np.bitwise_xor(R_s,R[i,:])

        R[-1,:] = R_s
        leakages[k] = hammingw(R)  # Taking Hamming weight model
        
        if not isSerial:
            leakages[k] = np.sum(leakages[k], axis=0, keepdims=True)
        
    return leakages

def get_leak_unique(leakages):
    leakages_uniq = np.array([None for _ in range(Nk)])
    leakages_alph = np.array([None for _ in range(Nk)])
    for k in range(len(leakages)):
        leakages_uniq[k], leakages_alph[k] = np.unique(leakages[k],axis=1,return_counts=True)
        leakages_alph[k] = leakages_alph[k] / np.sum(leakages_alph[k])

    return leakages_uniq, leakages_alph

def get_leak_unique_tot(leakages, D):
    leakages_tot = np.reshape(np.stack(leakages, axis=1), (D, -1))
    leakages_tot_uniq, leakages_tot_alph = np.unique(leakages_tot,axis=1,return_counts=True)
    leakages_tot_alph = leakages_tot_alph / np.sum(leakages_tot_alph)

    return leakages_tot_uniq, leakages_tot_alph

def get_equiv_classes(leakages_uniq, leakages_alph):
    classind = 0
    classlist = {}
    for k in range(Nk):
        new = True
        for i in range(classind):
            if np.array_equal(leakages_uniq[k], leakages_uniq[classlist[i][0]]) and np.array_equal(leakages_alph[k], leakages_alph[classlist[i][0]]):
                new = False
                classlist[i].append(k)
        if new:
            classlist[classind] = list([k])
            classind += 1
    classlen = np.array([len(classlist[i]) for i in range(len(classlist))])

    return classlist, classlen

n = 4
en = 1<<n
D = 2
Nk = 1<<n
Nd = D
isSerial = True

log_sigma = np.linspace(-1.,2,13)
log_var = 2*log_sigma

Leakages = get_leak_noise_free(D, Nk, Nd, isSerial)
Leakages_tot_uniq, Leakages_tot_alph = get_leak_unique_tot(Leakages, D)
Leakages_uniq, Leakages_alph = get_leak_unique(Leakages)
Classlist, Classlen = get_equiv_classes(Leakages_uniq, Leakages_alph)

if __name__ == '__main__':

    sigma_s = 10**log_sigma
    #sigma_s = np.array([0.8, 1, 2, 5, 10])
    mi_2d_all = np.zeros(len(sigma_s))

    with Pool(processes = 30) as pool:
        
        t0 = time.time()
        mi_2d_all = pool.map(mi_2d, sigma_s)
        t1 = time.time()
        print("The time for all mi_2d", t1-t0)

        for sig_s, mi in zip(sigma_s, mi_2d_all):
            print("The MI on sig_s of {} is {}".format(sig_s, mi))

    fig, ax = plt.subplots(1,1,figsize=(9, 7))
    plt.plot(log_var, np.log10(mi_2d_all), '--s', label="Boolean masking", c='r')
    ax.tick_params(axis = 'both', which = 'major', labelsize = 15)
    plt.xlabel("Noise level: log$_{10}(\sigma^2)$", fontsize=18)
    plt.ylabel("Mutual information: log$_{10}(I(\mathcal{L}; X))$", fontsize=18)
    plt.ylim([-12., 1])
    plt.xlim([-2., 4.])
    ax.set_yticks([i for i in range(-12, 2, 1)])
    ax.set_xticks([i for i in range(-2, 5, 1)])
    plt.legend(fontsize=14, ncol=1)
    plt.grid(which='major', axis='both',color='grey', linestyle='dashed')
        
    plt.show()