import time
import os

import wx
import numpy as np
from matplotlib.mlab import window_hanning,csv2rec

#Sound-generation function:
def sound_freq_sweep(startFreq, endFreq, duration, samples_per_sec=None):
    """   
    Creates a normalized sound vector (duration seconds long) where the
    frequency sweeps from startFreq to endFreq (on a log2 scale).

    Parameters
    ----------

    startFreq: float, the starting frequency of the sweep in Hz
    
    endFreq: float, the ending frequency of the sweep in Hz

    duration: float, the duration of the sweep in seconds

    samples_per_sec: float, the sampling rate, defaults to 44100 


    """
    if samples_per_sec is None:
        samples_per_sec = 44100

    time = np.arange(0,duration*samples_per_sec)

    if startFreq != endFreq:
        startFreq = np.log2(startFreq)
        endFreq = np.log2(endFreq)
        freq = 2**np.arange(startFreq,endFreq,(endFreq-startFreq)/(len(time)))
        freq = freq[:time.shape[0]]
    else:
        freq = startFreq
    
    snd = np.sin(time*freq*(2*np.pi)/samples_per_sec)

    # window the sound vector with a 50 ms raised cosine
    numAtten = np.round(samples_per_sec*.05);
    # don't window if requested sound is too short
    if len(snd) >= numAtten:
        snd[:numAtten/2] *= window_hanning(np.ones(numAtten))[:numAtten/2]
        snd[-(numAtten/2):] *= window_hanning(np.ones(numAtten))[-(numAtten/2):]

    # normalize
    snd = snd/np.max(np.abs(snd))

    return snd

#User input GUI:
class GetFromGui(wx.Dialog):
    """ Allows user to set input parameters of ss through a simple GUI"""    
    def __init__(self, parent, id, title, combo_choices=['No Choices Given']):
        wx.Dialog.__init__(self, parent, id, title, size=(280, 360))
        # Add text labels
        wx.StaticText(self, -1, 'Subject ID:', pos=(10,20))
        wx.StaticText(self, -1, 'Surround Orientation:', pos=(10,65))
        wx.StaticText(self, -1, 'Annulus Orientation:', pos=(10, 110))
        wx.StaticText(self, -1, 'Task:', pos=(10,155))
        wx.StaticText(self, -1, 'Surround or not:', pos=(10,190))
        self.replayStat = wx.StaticText(self, -1, 'No Replay Contrast Set', pos=(98, 230))
        # Add the subj id text box, drop down menu, radio buttons
        self.textbox = wx.TextCtrl(self, -1, pos=(100,18), size=(150, -1))
        self.replay_contrast = None
        
        #Spin control for the surround orientation:
        self.sc_surround = wx.SpinCtrl(self, -1, '', (155,58))
        self.sc_surround.SetRange(0,180)
        self.sc_surround.SetValue(0)

        #Spin control for the annulus orientation:
        self.sc_annulus = wx.SpinCtrl(self, -1, '', (155,103))
        self.sc_annulus.SetRange(0,180)
        self.sc_annulus.SetValue(0)
                      
        #Radio buttons for the different tasks:
        self.rb_task1 = wx.RadioButton(self, -1, 'Annulus', (55, 155),
                                  style=wx.RB_GROUP)
        self.rb_task2 = wx.RadioButton(self, -1, 'Fixation', (143, 155))
        self.rb_task1.SetValue(1)
        #Radio buttons for the different tasks:
        self.rb_task3 = wx.RadioButton(self, -1, 'Yes', (130, 190),
                                  style=wx.RB_GROUP)
        self.rb_task4 = wx.RadioButton(self, -1, 'No', (180, 190))
        self.rb_task3.SetValue(1)

        # Add OK/Cancel/Replay buttons
        wx.Button(self, 1, 'Done', (20, 300))
        wx.Button(self, 2, 'Quit', (180, 300))
        wx.Button(self, 3, 'Replay...', (10, 230))
        wx.Button(self,4, 'Clear', (100, 300))
        # Bind button press events to class methods for execution
        self.Bind(wx.EVT_BUTTON, self.OnDone, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnReplay, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=4)
        self.Centre()
        self.ShowModal()        

    # If "Done" is pressed, set important values and close the window
    def OnDone(self,event):
        self.success = True
        self.subject = self.textbox.GetValue()
        #If subjet is not set, default to 'test_subject':
        if self.subject == '':
            self.subject == 'test_subject'
        
        if self.rb_task1.GetValue():
            self.TaskType = 'Annulus'
        else:
            self.TaskType = 'Fixation'

        if self.rb_task3.GetValue():
            self.SurroundType = 'yes'
        else:
            self.SurroundType = 'no'

        self.surround_ori = self.sc_surround.GetValue()
        self.annulus_ori = self.sc_annulus.GetValue()
        
        self.Close()

    # If "Clear" is pressed, all values are set to defaults
    def OnClear(self, event):
        self.textbox.Clear()
        self.rb_task1.SetValue(1)
        self.sc_annulus.SetValue(0)
        self.sc_surround.SetValue(0)
        self.replayStat.SetLabel('No Replay Contrast Set')
        self.replay_contrast = None

    # If "Exit is pressed", toggle failure and close the window
    def OnClose(self, event):
        self.success = False
        self.Close()

    # If "Replay" is pressed, user can choose a file from which we will extract
    # the relevant contrast value (fix_target_start if user chooses annulus, 
    # start_target_contrast if user chooses fixation task)
    def OnReplay(self, event):
        # this will be our file dialog:
        dlg = wx.FileDialog(self, message="Choose SS Data File", defaultFile='',
            style=wx.OPEN)
        # if the user presses OK after choosing a file:
        if dlg.ShowModal() == wx.ID_OK:
            file_name = dlg.GetPath()
            # if "annulus" is picked, other_contrast comes from
            # fix_target_contrast:
            if self.rb_task1.GetValue():
                self.replay_id = 'fixation_target_contrast'
            # if "fixation" is picked, other_contrast comes from
            # start_target_contrast:
            else:
                self.replay_id = 'annulus_target_contrast'
            self.replay_contrast = staircase_from_file(file_name,self.replay_id)

            self.replayStat.SetLabel(self.replay_id)
            
def param_from_file(fileobj, paramName=None):
    """ Reads in parameters from a saved data file and returns the specified
        parameter value. If no value is given, returns the entire read dict """
    #intialize vars we will add to:
    read_params = {}
    raw_list = []
    #iterate over the file. We are interested in lines beginning with a hash:
    for line in fileobj:
        if line[0]=='#':
            #strip unnecessary chars and append line to our list:
            line = line.lstrip('#')
            line = line.rstrip('\n')
            raw_list.append(line)
    #the first and last lines are trash:
    raw_list =  raw_list[1:-1]
    for val in raw_list:
            #split string around the ':' and append to dict:
            val = val.split(':')
            read_params[val[0].strip()] = val[1].strip()
     #return the requested param, if it exists:
    if paramName is None:
        return read_params
    elif paramName in read_params.keys():
        return read_params[paramName]
    else:
        return None
        
def staircase_from_file(file_name,param_name):
    """Get a staircase from a previous run"""

    rec = csv2rec(file_name)
    return rec[param_name]

def start_data_file(subject_id):

    """Start a file object into which you will write the data, while making
    sure not to over-write previously existing files """
    
    #Check the data_file:
    
    list_data_dir = os.listdir('./data')

    i=1
    this_data_file = 'SS_%s_%s_%s.psydat'%(subject_id,time.strftime('%m%d%Y'),i)

    #This makes sure that you don't over-write previous data:
    while this_data_file in list_data_dir:
        i += 1
        this_data_file='SS_%s_%s_%s.psydat'%(subject_id,
                                             time.strftime('%m%d%Y'),i)
        
    #Open the file for writing into:
    f = file('./data/%s'%this_data_file,'w')
    #Write some header information
    f.write('## Parameters: ##\n')
    
    return f


