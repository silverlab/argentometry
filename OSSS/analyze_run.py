import sys
from psychopy import gui
from matplotlib.mlab import csv2rec
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq
#from pypsignifit import (BootstrapInference,GoodnessOfFit,ParameterPlot,
#                        ThresholdPlot)

def weibull(x,threshx,slope,guess,flake,threshy=None):

    if threshy is None:
        threshy = 1-(1-guess)*np.exp(-1)
        
    k = (-np.log( (1-threshy)/(1-guess) ))**(1/slope)
    weib = flake - (flake-guess)*np.exp(-(k*x/threshx)**slope)
    return weib 
 
def weib_fit(pars):
    thresh,slope = pars
    
    return weibull(x,thresh,slope,guess,flake)
    
def err_func(pars):
    return y-weib_fit(pars)

if __name__=="__main__":

    bootstrap_n = 1000

    #Weibull params:
    guess = 0.5 #The guessing rate is 0.5
    flake = 0.99
    slope = 3.5
    file_name = str(gui.fileOpenDlg(tryFilePath='./data')[0])
    #file_name='./data/SS_kelly_09082015_6.psydat'
    file_read = file(file_name,'r')
    p = {} #This will hold the params
    l = file_read.readline()

    while l[0]=='#':
        try:
            p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 

        #Not all the parameters can be cast as float (the task and the
        #subject): 
        except:
            p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]

        l = file_read.readline()
    data_rec = csv2rec(file_name)
    annulus_target_contrast = data_rec['annulus_target_contrast']-p[' annulus_contrast']
    contrast = data_rec['annulus_target_contrast']-p[' annulus_contrast']
    correct = data_rec['correct']   

    #Which staircase to analyze:
    if p['task'] == ' Fixation ':
        contrast_all = data_rec['fixation_target_contrast']
    elif p['task']== ' Annulus ':
        contrast_all = data_rec['annulus_target_contrast']-p[' annulus_contrast']

    labelit = ['annulus_off','annulus_on']
    if p[' surround_contrast']%180 == 0 :
       print 'Surround: vertical'
    else:
       print 'Surround: horizontal'
       
    if p[' annulus_contrast']%180 == 0 :
       print 'Annulus: vertical'
    else:
       print 'Annulus: horizontal'
       
    if p['SurroundType'] == ' yes ':
       print 'Surround contrast: %1.1f' % (p[' surround_contrast'])
    else:
       print 'Surround contrast: 0'

 
    #Switch on the two annulus tasks (annulus on vs. annulus off):
#    for idx_annulus,operator in enumerate(['<','>=']):
    hit_amps = contrast[correct==1]
    miss_amps = contrast[correct==0]
    all_amps = np.hstack([hit_amps,miss_amps])
        #Get the data into this form:
        #(stimulus_intensities,n_correct,n_trials)
    stim_intensities = np.unique(all_amps)
    n_correct = [len(np.where(hit_amps==i)[0]) for i in stim_intensities]
    n_trials = [len(np.where(all_amps==i)[0]) for i in stim_intensities]

    Data = zip(stim_intensities,n_correct,n_trials)

    x = []
    y = []

#        for idx,this in enumerate(Data):
            #Take only cases where there were at least 3 observations:
#    labelit = p['annulus_ori'] 
    for idx,this in enumerate(Data):
        if n_trials>=3:
    
        #Contrast values: 
            x = np.hstack([x,this[2] * [this[0]]])
                #% correct:
            y = np.hstack([y,this[2] * [this[1]/float(this[2])]])
    
    initial = np.mean(x),slope
    this_fit , msg = leastsq(err_func,initial)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(x,y,'o')
    x_for_plot = np.linspace(np.min(x),np.max(x),100)
    ax.plot(x_for_plot,weibull(x_for_plot,this_fit[0],
                                   this_fit[1],
                                   guess,
                                   flake))
    ax.set_title('%s:thresh=%1.2f::slope=%1.2f'
                     %(p['task'],this_fit[0],this_fit[1]))
    ax.set_ylabel('Percentage correct')
    ax.set_xlabel('Target contrast - annulus contrast')
    file_stem = file_name.split('/')[-1].split('.')[0]
    fig.savefig('%s.png'%(file_stem))
            
    bootstrap_th = []
    bootstrap_slope = []
    keep_x = x
    keep_y = y
    keep_th = this_fit[0]
    for b in xrange(bootstrap_n):
            b_idx = np.random.randint(0,x.shape[0],x.shape[0])
            x = keep_x[b_idx]
            y = keep_y[b_idx]
            initial = np.mean(x),slope
            this_fit , msg = leastsq(err_func,initial)
            bootstrap_th.append(this_fit[0])
            bootstrap_slope.append(this_fit[0])
    upper = np.sort(bootstrap_th)[bootstrap_n*0.975]
    lower = np.sort(bootstrap_th)[bootstrap_n*0.025]
    print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th,
                                                                    lower,
                                                                    upper)

    #bootstrap inference of the psignifit package
        #Both tasks are honest-to-god 2AFC:
    #constraints = ( 'unconstrained', 'unconstrained', 'unconstrained') 
    #B = BootstrapInference ( Data, priors=constraints, nafc=2 )
    #B.sample()
    #print 'Threshold: %s'%(B.getThres())
    #print 'Slope: %s' % (B.getSlope())
    #print 'CI: [%s,  %s]'%(B.getCI(1)[0],
                           #B.getCI(1)[1])
    #print 'Last value in the staircase: %s'%contrast[-1]