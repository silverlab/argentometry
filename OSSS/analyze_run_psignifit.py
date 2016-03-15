import sys

from matplotlib.mlab import csv2rec
import matplotlib.pyplot as plt
import numpy as np
from pypsignifit import (BootstrapInference,GoodnessOfFit,ParameterPlot,
                         ThresholdPlot)

#User input GUI- not currently running, but soon?:
#class GetFromGui(wx.Dialog):
#    """ Allows user to set input parameters of ss through a simple GUI"""    
#    def __init__(self, parent, id, title, combo_choices=['No Choices Given']):
#        wx.Dialog.__init__(self, parent, id, title, size=(280, 300))
#        # Add text labels
#        wx.StaticText(self, -1, 'FileName:', pos=(10,20))
#        # Add the subj id text box, drop down menu, radio buttons
#        self.textbox = wx.TextCtrl(self, -1, pos=(100,18), size=(150, -1))
#        self.replay_contrast = None        
#        # Add OK/Cancel/Replay buttons
#        wx.Button(self, 1, 'Done', (20, 240))
#        wx.Button(self, 2, 'Quit', (180, 240))
#        # Bind button press events to class methods for execution
#        self.Bind(wx.EVT_BUTTON, self.OnDone, id=1)
#        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
#        self.Centre()
#        self.ShowModal()        
#    # If "Done" is pressed, set important values and close the window
#    def OnDone(self,event):
#        self.success = True
#        self.filename = self.textbox.GetValue()
#        #If subjet is not set, default to 'test_subject':
#        self.Close()
#    # If "Clear" is pressed, all values are set to defaults
#    def OnClear(self, event):
#        self.textbox.Clear()
#    # If "Exit is pressed", toggle failure and close the window
#    def OnClose(self, event):
#        self.success = False
#        self.Close()
contrast = []

if __name__=="__main__":
    
    file_name = sys.argv[1]
    file_read = file(file_name,'r')
    p = {} #This will hold the params
    l = file_read.readline()
    
    while l[0]=='#':
        try:
            p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 

        #Not all the parameters can be cast as float (the task and the subject)
        except:
            p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]
            
        l = file_read.readline()
    data_rec = csv2rec(file_name)
    annulus_target_contrast = data_rec['annulus_target_contrast']
    correct = data_rec['correct']
    #Which staircase to analyze:
    if p['task'] == ' Fixation ':
        contrast = 1-data_rec['fixation_target_contrast']
        hit_amps = contrast[correct==1]
        miss_amps = contrast[correct==0]
    elif p['task']== ' Annulus ':
        #if data_rec['annulus_target_contrast'] >= 0.75#params.targetA_contrast_min
        contrast_all = data_rec['annulus_target_contrast'] - p[' annulus_contrast']
        print contrast_all
#        contrast = data_rec.find(annulus_target_contrast>=0.75)
        contrast = contrast_all[annulus_target_contrast>=0.75]
        this_correct = correct[annulus_target_contrast>=0.75]
        hit_amps = contrast[this_correct==1]
        miss_amps = contrast[this_correct==0]
    all_amps = np.hstack([hit_amps,miss_amps])
    #For psignifit, the data needs to have the form:
    #(stimulus_intensities,n_correct,n_trials)
    stim_intensities = np.unique(all_amps)
    n_correct = [len(np.where(hit_amps==i)[0]) for i in stim_intensities]
    n_trials = [len(np.where(all_amps==i)[0]) for i in stim_intensities]

    constraints = ( 'unconstrained', 'unconstrained', 'unconstrained') 

    #Do the psignifit thing for the psychometric curve:
    data = zip(stim_intensities,n_correct,n_trials)

    #Both tasks are honest-to-god 2AFC:
    B = BootstrapInference ( data, priors=constraints, nafc=2 )
    B.sample()
    print 'Threshold: %s'%(B.getThres())
    print 'CI: [%s,  %s]'%(B.getCI(1)[0],
                           B.getCI(1)[1])
    print 'Last value in the staircase: %s'%contrast[-1]
           
