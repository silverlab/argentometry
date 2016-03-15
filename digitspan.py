#!/usr/bin/env python2
"""digitspan.py
A simple Digit Span psychological test using the PsychoPy python module. The 
test is comprised of two phases.
  1. NUM_PRACTICE_TRIALS of practice rounds, each with audio number 
    presentation of length PRACTICE_TRIAL_LENGTH.
  3. Actual rounds, beginning with a sequence of lengths within the ranges 
    FORWARD_RANGE and continuing until the sequences of length SET_SIZE_MAX or 
    the subject fails three rounds in a set size. This will be repeated 
    NUM_TRIAL_BLOCKS times.
  3. Actual rounds, beginning with a sequence of lengths within the ranges 
    REVERSE_RANGE and continuing until the sequences of length SET_SIZE_MAX or 
    the subject fails MAX_FAILS rounds. The subject must recall in reverse 
    order.  This will be repeated NUM_TRIAL_BLOCKS times.
In the actual experiment, the subject is presented with n digits, one at a 
time, each presented for STIMULI_TIME seconds. Then the user is asked to recall
the sequence.

Correctness is measured for each trial as follows: 
  'XY' pairs where X is 'T' if the position of  sequence at that position is 
  correct and 'F' if it is not, and Y is 'T' if the sequence at that position 
  has identity correctness or 'F' if not. Identity correctness is when the 
  letter entered was somewhere else in the set, not nocessarily in the position
  stated. Note - 'TF' is impossible to have.

Command-Line Execution: Instead of entering the subject initlas through the
psychopy gui, you can provide them as command line arguments when running 
with the terminal.

Log files:
  All log files are placed in the directory data/X/digitspan.txt, where X is 
  the initials of the participant. Each line of the log file describes 
  different actions occuring in the program. Here are the different possible 
  formats of each line in the log file:
    * Note: 'TIMESTAMP' indicates how many seconds have passed since the 
      initialization of the program
    * "MM/DD/YYYY HH:MM:SS" - at the beginning of the data file, indicates the 
      current date and time that the program began its execution.
    * "TIMESTAMP: SUBJECT: X" - indicates the subjects initials who this data 
      file belongs to.
    * "TIMESTAMP: Test Number: X" - indicates which iteration of the test the
      subject is on. X must be an integer >= 1.
    * "TIMESTAMP: Section [1-3]" - indicates that section data follows until 
      the next "Section X".
    * "TIMESTAMP: ([true/false],[correct response],[subject response],
      [accuracy],N,%f)" - indicates that a sequence of N letters have been 
      completed in %f time, incorrectly if false, and correctly if true.
    * "TIMESTAMP: Max Digit-Span BLOCK X: Y" - maximum Digit - Span for block 
      X is Y digits.
    * "TIMESTAMP: END SUCCESS" - test has successfully completed
    * "TIMESTAMP: ERROR! QUIT OUT OF SYSTEM" - test has been quit by user, by
      pressing the 'q' or 'Esc' keys.
After imports, there is a list of global variables that change various aspects
of the program, modifiable to the administrators content.
"""
from psychopy import visual,core,event,gui,sound
import random,numpy,sys,os
from datetime import datetime
__author__ = "Omid Rhezaii"
__email__ = "omid@rhezaii.com"
__copyright__ = "Copyright 2015, Michael Silver Lab"
__credits__ = ["Omid Rhezaii", "Sahar Yousef", "Michael Silver"]
__version__ = "3.0"
__status__ = "Final"

# GLOBAL VARIABLE DECLARATIONS
IN_BETWEEN_DIGITS_TIME = 0.5
DIGIT_DISPLAY_TIME = 0.500 # time each number is displayed
FORWARD_RANGE = (3,15)
REVERSE_RANGE = (2,15)
NUM_TRIAL_BLOCKS = 1 # if you change this please contact programmer
DIGIT_SIZE = 12 # size of digits on screen display
MAX_FAILS = 2 # in a row
CORRECT_FREQ = 440
INCORRECT_FREQ = 330
TONE_LENGTH = 0.5
HIGHLIGHT_COLOR = "DarkOrange"
# practice trial options
NUM_PRACTICE_TRIALS = 2
PRACTICE_TRIAL_LENGTH = 3

# Keep master time for whole program
programTime = core.Clock()
# log file location
logFile = "digitspan"
dataPath = "digitspan"
# number sequences
fseqs = []
rseqs = []
# wav sound file array
soundFiles = []
def main(argv):
  """Main method to be runned at beginning"""
  global logFile, programTime, dataPath

  #do only if we werent given initials from the command line
  if len(argv) == 1:
    while True:
      dlg = gui.DlgFromDict(dictionary={'Class ID':'','Test Number':'1'},title="Digit-Span Task")
      if(dlg.OK):
        initials = dlg.data[0]
        testNo = int(dlg.data[1])
      else:
        sys.exit(1)
      if(os.path.isfile("data/"+initials+"/"+logFile+str(testNo)+".txt")):
        error = gui.Dlg(title="Existing Log File",labelButtonOK=u'Yes',labelButtonCancel=u'No')
        error.addText("A log file with initials " + initials+ " already exists. Are you sure you want to overwrite? If not, answer no and change your initials." )
        error.show()
        if error.OK:
          os.remove("data/"+initials+"/"+logFile+str(testNo)+".txt")
          break
        else:
          continue
      else:
        break
  elif(len(argv)==3):
    initials = argv[1]
    testNo = int(argv[2])
  else:
    print "Too many command line arguments. Please read documentation."
    sys.exit(1)
  initials = initials.upper()
  dataPath = "data/"+initials+"/" + dataPath

  if not os.path.isdir("data"):
    os.mkdir("data")
  if not os.path.isdir("data/"+initials):
    os.mkdir("data/"+initials)
  logFile = open("data/"+initials+"/"+logFile+str(testNo)+".txt","w+")
  log(datetime.now().strftime("%d/%m/%y %H:%M"))
  log("Subject: " + initials)
  log("Test Number: " + str(testNo))
  win = visual.Window([800,600],monitor="testMonitor",units="deg",fullscr=True)
  mouse = event.Mouse(win=win)
  winsound = sound.SoundPygame(value=CORRECT_FREQ, secs=TONE_LENGTH-0.1)
  losesound = sound.SoundPygame(value=INCORRECT_FREQ, secs=TONE_LENGTH-0.1)
  loadSoundFiles()
  loadSequences()

  ### SECTION 1 BEGIN
  log("Section 1")
  instructions = visual.TextStim(win,text="Practice\n\nIn this task, you will hear a sequence of numbers. When the audio finishes, "+
                                          "enter all of the numbers in same order they were recited.\n\nPress any key to continue",wrapWidth=30)
  instructions.draw()
  win.flip()
  #while 1 not in mouse.getPressed():
  #  pass
  #while 1 in mouse.getPressed():
  #  pass
  event.waitKeys()
  visual.TextStim(win,text="This is the sound of a correct response.").draw()
  win.flip()
  winsound.play()
  core.wait(2)
  visual.TextStim(win,text="This is the sound of an incorrect response.").draw()
  win.flip()
  losesound.play()
  core.wait(2)

  # begin practice trial
  for j in range(NUM_PRACTICE_TRIALS):
    x = range(10)
    random.shuffle(x)
    for i in x[:PRACTICE_TRIAL_LENGTH]:
      displayDigit(win,i)
      win.flip()
      core.wait(IN_BETWEEN_DIGITS_TIME)
    temp = validateSequence(win,mouse)
    correctSeq = x[:PRACTICE_TRIAL_LENGTH]
    if(temp[0]==correctSeq):
      tempLog = "(True,"
      winsound.play()
    else:
      tempLog = "(False,"
      losesound.play()
    core.wait(TONE_LENGTH)
    log(tempLog+str(correctSeq)+","+str(temp[0])+","+str(correctness(temp[0],correctSeq))+","+str(PRACTICE_TRIAL_LENGTH)+","+str(temp[1])+")")
  ### SECTION 1 END

  ### SECTION 2 BEGIN
  log("Section 2")
  instructions = visual.TextStim(win,text="Again, listen to the sequence of numbers, and when the audio finishes, "+
                                          "enter all of the numbers in same order they were recited.\n\nPress any key to continue",wrapWidth=30)
  instructions.draw()
  win.flip()
  event.waitKeys()
  results_forward = dict()
  maxForSpan = []
  for block in range(NUM_TRIAL_BLOCKS):
    numWrong = 0
    maxForSpan.append(0)
    fi = 0
    lastss = 0
    sscount = 1
    while True:
      if fi < len(fseqs):
        x = fseqs[fi]
        fi += 1
      else:
        if sscount >= 2:
          if lastss == FORWARD_RANGE[1]:
            visual.TextStim(win,text="This block is over. Your max forward Digit-Span was {0}".format(maxForSpan[-1])).draw()
            win.flip()
            log("Max Forward Digit Span BLOCK "+str(block)+": " + str(maxForSpan[-1]))
            core.wait(5)
            break
          else:
            ss2 = lastss + 1
            sscount = 1
        else:
          ss2 = lastss
        x = []
        while len(x)<ss2:
          temp = random.randint(0,9)
          if not x or temp != x[-1]:
            x.append(temp)
      ss = len(x)
      if lastss == ss:
        sscount += 1
      else:
        sscount = 1
        numWrong = 0
      if ss not in results_forward:
        results_forward[ss] = []
      for dig in x:
        displayDigit(win,dig)
        win.flip()
        core.wait(IN_BETWEEN_DIGITS_TIME)
      temp = validateSequence(win,mouse)
      correctSeq = x
      results_forward[ss].append(1.0*sum([2 if l=='TT' else 1 if l=='FT' else 0 for l in correctness(temp[0],correctSeq)])/(2.0*ss))
      if(temp[0]==correctSeq):
        tempLog = "(True,"
        winsound.play()
        maxForSpan[-1] = ss
        numWrong = 0
      else:
        tempLog = "(False,"
        losesound.play()
        numWrong += 1
      log(tempLog+str(correctSeq)+","+str(temp[0])+","+str(correctness(temp[0],correctSeq))+","+str(ss)+","+str(temp[1])+")")
      if numWrong >= MAX_FAILS:
        core.wait(TONE_LENGTH)
        visual.TextStim(win,text="This block is over. Your max forward Digit-Span was {0}".format(maxForSpan[-1])).draw()
        win.flip()
        log("Max Forward Digit Span BLOCK "+str(block)+": " + str(maxForSpan[-1]))
        core.wait(5)
        break
      win.flip()
      core.wait(TONE_LENGTH)
      lastss = ss
  ### SECTION 2 END

  ### SECTION 3 BEGIN
  log("Section 3")
  win.flip()
  instructions = visual.TextStim(win,text="Reverse Practice\n\nNow you will hear a sequence of numbers, and when the audio is finished, "+
                                          "enter the numbers you heard in REVERSE order. For example, if you hear 1,2,3, then you would "+
                                          "type 3,2,1.\n\nPress any key to continue",wrapWidth=30)
  instructions.draw()
  win.flip()
  event.waitKeys()
  ri = 0
  for i in range(2):
    x = rseqs[ri]
    ri += 1
    for dig in x:
      displayDigit(win,dig)
      win.flip()
      core.wait(IN_BETWEEN_DIGITS_TIME)
    temp = validateSequence(win,mouse,reverse=" reverse")
    correctSeq = x[::-1]
    if(temp[0]==correctSeq):
      tempLog = "(True,"
      winsound.play()
    else:
      tempLog = "(False,"
      losesound.play()
    log(tempLog+str(correctSeq)+","+str(temp[0])+","+str(correctness(temp[0],correctSeq))+","+str(ss)+","+str(temp[1])+")")
    core.wait(TONE_LENGTH)

  # end practice

  win.flip()
  instructions = visual.TextStim(win,text="Again, you will hear a sequence of numbers, and when the audio is finished, "+
                                          "enter the numbers you heard in REVERSE order. For example, if you hear 1,2,3, then you would "+
                                          "type 3,2,1.\n\nPress any key to continue",wrapWidth=30)
  instructions.draw()
  win.flip()
  event.waitKeys()
  results_reverse = dict()
  maxRevSpan = []
  for block in range(NUM_TRIAL_BLOCKS):
    numWrong = 0
    maxRevSpan.append(0)
    lastss = 0
    sscount = 1
    while True:
      if ri < len(rseqs):
        x = rseqs[ri]
        ri += 1
      else:
        if sscount >= 2:
          if lastss == REVERSE_RANGE[1]:
            visual.TextStim(win,text="This block is over. Your max reverse Digit-Span was {0}".format(maxRevSpan[-1])).draw()
            win.flip()
            log("Max Reverse Digit Span BLOCK "+str(block)+": " + str(maxRevSpan[-1]))
            core.wait(5)
            break
          else:
            ss2 = lastss + 1
            sscount = 1
        else:
          ss2 = lastss
        x = []
        while len(x)<ss2:
          temp = random.randint(0,9)
          if not x or temp != x[-1]:
            x.append(temp)
      ss = len(x)
      if lastss == ss:
        sscount += 1
      else:
        sscount = 1
        numWrong = 0
      if ss not in results_reverse:
        results_reverse[ss] = []
      for dig in x:
        displayDigit(win,dig)
        win.flip()
        core.wait(IN_BETWEEN_DIGITS_TIME)
      temp = validateSequence(win,mouse,reverse=" reverse")
      correctSeq = x[::-1]
      results_reverse[ss].append(1.0*sum([2 if l=='TT' else 1 if l=='FT' else 0 for l in correctness(temp[0],correctSeq)])/(2.0*ss))
      if(temp[0]==correctSeq):
        tempLog = "(True,"
        winsound.play()
        maxRevSpan[-1] = ss
        numWrong = 0
      else:
        tempLog = "(False,"
        losesound.play()
        numWrong += 1
      log(tempLog+str(correctSeq)+","+str(temp[0])+","+str(correctness(temp[0],correctSeq))+","+str(ss)+","+str(temp[1])+")")
      if numWrong >= MAX_FAILS:
        core.wait(TONE_LENGTH)
        visual.TextStim(win,text="This block is over. Your max reverse Digit-Span was {0}".format(maxRevSpan[-1])).draw()
        win.flip()
        log("Max Reverse Digit Span BLOCK "+str(block)+": " + str(maxRevSpan[-1]))
        core.wait(5)
        break
      win.flip()
      core.wait(TONE_LENGTH)
      lastss = ss
  ### SECTION 3 END
  visual.TextStim(win,text="Thank you for your participation.").draw()
  win.flip()
  core.wait(3)

  dfscores = []
  drscores = []
  for key in results_forward.keys():
    dfscores.append((100.0*sum(results_forward[key]))/len(results_forward[key]))
  for key in results_reverse.keys():
    drscores.append((100.0*sum(results_reverse[key]))/len(results_reverse[key]))
  visual.SimpleImageStim(win, image=makeresultsplot(testNo,"Set Size","Percentage Correct(%)",results_forward.keys(),results_reverse.keys(),dfscores,drscores)).draw()
  win.flip()
  core.wait(8)

  # write results to a xls file with all other subjects
  try:
    import xlrd,xlwt,xlutils.copy
    excelfile = "data/digitspan.xls"
    if not os.path.isfile(excelfile):
      w = xlwt.Workbook()
      ws = w.add_sheet("Data")
      style = xlwt.easyxf("font: bold on")
      ws.write(0,0,"Initials",style)
      ws.write(0,1,"Day",style)
      ws.write(0,2,"Avg Forward Digit-SPAN",style)
      ws.write(0,3,"Avg Reverse Digit-SPAN",style)
      w.save(excelfile)
    oldfile = xlrd.open_workbook(excelfile,formatting_info=True)
    row = oldfile.sheet_by_index(0).nrows
    newfile = xlutils.copy.copy(oldfile)
    sheet = newfile.get_sheet(0)
    sheet.write(row,0,initials)
    sheet.write(row,1,testNo)
    sheet.write(row,2,(1.0*sum(maxForSpan))/len(maxForSpan))
    sheet.write(row,3,(1.0*sum(maxRevSpan))/len(maxRevSpan))
    newfile.save(excelfile)
  except ImportError:
    print "ERROR: NO XLRD,XLWT, or XLUTILS installed."

  log("END SUCCESS")
  logFile.close()
  core.quit()
  # end of main

def log(line):
  """Write line to logFile.

  Arguments:
  @param line: string to write to logFile
  """
  global logFile,programTime
  logFile.write(str(programTime.getTime())+": "+line+"\n")

def loadSoundFiles():
  """Load wav files from sounds directory for audio presentation."""
  global soundFiles
  for i in range(10):
    soundFiles.append(sound.SoundPygame(value=str("sounds/female_"+str(i)+".wav")))

def loadSequences():
  """Loads preset sequences into memory"""
  global fseqs, rseqs
  fseqs.append([9,7])
  fseqs.append([6,3])
  fseqs.append([5,8,2])
  fseqs.append([6,9,4])
  fseqs.append([7,2,8,6])
  fseqs.append([6,4,3,9])
  fseqs.append([4,2,7,3,1])
  fseqs.append([7,5,8,3,6])
  fseqs.append([3,9,2,4,8,7])
  fseqs.append([6,1,9,4,7,3])
  fseqs.append([4,1,7,9,3,8,6])
  fseqs.append([6,9,1,7,4,2,8])
  fseqs.append([3,8,2,9,6,1,7,4])
  fseqs.append([5,8,1,3,2,6,4,7])
  fseqs.append([2,7,5,8,6,3,1,9,4])
  fseqs.append([7,1,3,9,4,2,5,6,8])
  rseqs.append([3,1])
  rseqs.append([2,4])
  rseqs.append([4,6])
  rseqs.append([5,7])
  rseqs.append([6,2,9])
  rseqs.append([4,7,5])
  rseqs.append([8,2,7,9])
  rseqs.append([4,9,6,8])
  rseqs.append([6,5,8,4,3])
  rseqs.append([1,5,4,8,6])
  rseqs.append([5,3,7,4,1,8])
  rseqs.append([7,2,4,8,5,6])
  rseqs.append([8,1,4,9,3,6,2])
  rseqs.append([4,7,3,9,6,2,8])
  rseqs.append([9,4,3,7,6,2,1,8])
  rseqs.append([7,2,8,1,5,6,4,3])

def quit():
  """Quit the program, logging an error and then exiting."""
  log(": ERROR! QUIT OUT OF SYSTEM")
  logFile.close()
  core.quit()

def displayDigit(win,digit):
  """Display number to screen.

  Arguments:
  @param win: psychopy Window to be used for display
  @param digit: digit to be displayed
  """
  #letter = visual.TextStim(win,text=str(digit))
  #letter.setHeight(DIGIT_SIZE)
  #letter.draw()
  win.flip()
  soundFiles[digit].setVolume(1)
  soundFiles[digit].play()
  core.wait(DIGIT_DISPLAY_TIME)

def makeresultsplot(name, xtext, ytext, xvalues, xvalues2, yvalues, yvalues2):
  """A simple plotter using matplotlib. 

  Arguments:
  @param name - file name prefixed by 'digitspan' for saving
  @param xtext - text for the x-axis
  @param ytext - text for the y-axis
  @param xvalues - values for the x-axis
  @param yvalues - values for the OSPAN scores
  @param yvalues2 - values for the Math scores

  @return path to the image where the graph is saved
  """
  try:
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xvalues,yvalues,marker='o',label="Forward Digit Span")
    ax.plot(xvalues2,yvalues2,marker='o',label="Reverse Digit Span")
    plt.xlabel(xtext)
    plt.ylabel(ytext)
    plt.legend(loc=0)
    plt.axis([min(FORWARD_RANGE[0],REVERSE_RANGE[0]),max(FORWARD_RANGE[1],REVERSE_RANGE[1]),0,101])
    plt.title("Graph of performance")
    plt.savefig(dataPath+str(name)+".png")
    return dataPath+str(name)+".png"
  except ImportError:
    print "ERROR: NO MATPLOTLIB.PYPLOT installed."

def correctness(sequence, correct):
  """Compares @param sequence to @param correct sequence for correctness.

  Arguments:
  @param sequence - the sequence from the subject
  @param correct - the correct sequence to be expected

  @return an array of 'XY' pairs where X is 'T' if the position of @param 
  sequence at that position is correct and 'F' if it is not, and Y is 'T' if 
  the sequence at that position has identity correctness or 'F' if not. 
  """
  measure = []
  i = 0
  while i < len(sequence):
    if i >= len(correct):
      measure.append('F')
    else:
      measure.append('T' if sequence[i]==correct[i] else 'F')
    measure[-1] += 'T' if sequence[i] in correct else 'F'
    i += 1
  return measure

def validateSequence(win,mouse,reverse=''):
  """Display a screen where users pick digits in the order they remember.
  
  Arguments:
  @param win: psychopy Window to be used for display
  @param mouse: psychopy Mouse used in display
  
  @return a tuple of the form: ([list of digits], time taken)
  """
  instructions = visual.TextStim(win,text="Type the digits in the"+reverse+" order they were recited. Press the delete button if you want to erase the last letter you typed. "+
                                          "For any digits that you do not remember, use the asterisk (*) button instead of guessing. Press enter when you are done.", pos=(0,6),wrapWidth=30)
  instructions.setAutoDraw(True)
  instructions.draw()
  win.flip()
  LETTERS = ["1","2","3","4","5","6","7","8","9","0"]
  timer = core.Clock()
  clicked = []
  numbers2 = []
  event.clearEvents()
  while(True):
    for i in range(len(LETTERS)):
      if event.getKeys(keyList=['num_'+LETTERS[i],LETTERS[i],'['+LETTERS[i]+']']):
        clicked.append(int(LETTERS[i]))
        numbers2.append(visual.TextStim(win,text=LETTERS[i],color="DarkMagenta",pos=(-10+2*len(numbers2),0)))
        numbers2[-1].setAutoDraw(True)
        numbers2[-1].draw()
        win.flip()
        core.wait(0.200)
    if event.getKeys(keyList=['asterisk']):
        clicked.append("*")
        numbers2.append(visual.TextStim(win,text="*",color="DarkMagenta",pos=(-10+2*len(numbers2),0)))
        numbers2[-1].setAutoDraw(True)
        numbers2[-1].draw()
        win.flip()
        core.wait(0.200)
    if event.getKeys(keyList=['backspace','delete','[.]','period','.']) and len(clicked) > 0:
      clicked.remove(clicked[len(clicked)-1])
      numbers2[-1].setAutoDraw(False)
      numbers2.remove(numbers2[-1])
      win.flip()
      core.wait(0.250)
    if event.getKeys(keyList=['num_enter','return']):
      #erase display
      for n in numbers2:
        n.setAutoDraw(False)
      instructions.setAutoDraw(False)
      return (clicked,timer.getTime())
    if(event.getKeys(keyList=['q','escape'])):
      quit()

if __name__ == "__main__": main(sys.argv)
