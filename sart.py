#!/usr/bin/env python2
"""sart.py
A simple Sustained Attention(SART) psychological test using the PsychoPy python
module.
  1. Practice Round: There will be NUM_PRACTICE_DIGIT_SETS of digits in 
    DIGIT_RANGE presented to the subject, and the subject needs to press a key
    each time a non-TARGET_DIGIT is displayed, otherwise it will count as a 
    'timeout'.
  3. Actual Round: The same TARGET_DIGIT will be used, but this time there will
    be NUM_DIGIT_SETS of digits in DIGIT_RANGE presented to the subject. 

Command-Line Execution: Instead of entering the subject initials through the
psychopy gui, you can provide them as command line arguments when running 
with the terminal.

Log files:
  All log files are placed in the directory data/X/sart.txt, where X is 
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
    * "TIMESTAMP: TARGET: X" - indicates what the target number was
    * "TIMESTAMP: Section [1-2]" - indicates that section data follows until 
      the next "Section X".
    * "TIMESTAMP: ([true/false/timeout], N, reaction time)" - for each showing
      of a number, the subject will get true if it was a non-target number and 
      they pressed the key, otherwise if it is the target and they press a 
      digit, then they get false, otherwise they get a true. A timeout occurs
      when they don't respond within the MASK_TIME to a non-target digit. The
      reaction time is measured from the beginning of when the digit is 
      displayed.
    * "TIMESTAMP: Accuracy: Y" - overall accuracy including non-targets and
      targets.
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
__version__ = "1.1"
__status__ = "Final"

# GLOBAL VARIABLE DECLARATIONS
DIGIT_DISPLAY_TIME = 0.250 # time each number is displayed
DIGIT_RANGE = (0,9)
DIGIT_SIZES = [1.8,2.7,3.5,3.8,4.5] # display sizes in cm
TARGET_DIGIT = -1 # a random digit will be assigned in the beginning if -1
NUM_DIGIT_SETS = 25
MASK_TIME = 0.900
MASK_DIAMETER = 3.0
# sound settings
MAX_FAILS = 3
CORRECT_FREQ = 440
INCORRECT_FREQ = 330
TONE_LENGTH = 0.5
# practice trial options
NUM_PRACTICE_DIGIT_SETS = 2

# Keep master time for whole program
programTime = core.Clock()
# log file location
logFile = "sart"
dataPath = "sart"
def main(argv):
  """Main method to be runned at beginning"""
  global logFile, programTime, dataPath, TARGET_DIGIT

  #do only if we werent given initials from the command line
  if len(argv) == 1:
    while True:
      dlg = gui.DlgFromDict(dictionary={'Class ID':'','Test Number':'1'},title="SART Task")
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
  if TARGET_DIGIT == -1:
    TARGET_DIGIT = random.randint(*DIGIT_RANGE)
  log("TARGET: " + str(TARGET_DIGIT))
  win = visual.Window([800,600],monitor="testMonitor",units="cm",fullscr=True)
  mouse = event.Mouse(win=win)
  winsound = sound.SoundPygame(value=CORRECT_FREQ, secs=TONE_LENGTH)
  losesound = sound.SoundPygame(value=INCORRECT_FREQ, secs=TONE_LENGTH)
  timer = core.Clock()

  ### SECTION 1 BEGIN
  log("Section 1")
  instructions = visual.TextStim(win,text="Practice\n\nIn this task, a number will be shown on the screen. "+
                                          "If it is not a %d, then click your mouse anywhere on the screen. If it is a %d" % (TARGET_DIGIT, TARGET_DIGIT) +
                                          ", then do not click anywhere. Please give equal importance to accuracy and speed.\n\nClick to Continue", wrapWidth=40)
  instructions.draw()
  win.flip()
  while 1 not in mouse.getPressed():
    pass
  while 1 in mouse.getPressed():
    pass
  visual.TextStim(win,text="This is the sound of a correct response.").draw()
  win.flip()
  winsound.play()
  core.wait(2)
  visual.TextStim(win,text="This is the sound of an incorrect response.").draw()
  win.flip()
  losesound.play()
  core.wait(2)

  # begin practice trial
  mask1 = visual.Circle(win,radius=MASK_DIAMETER/2,pos=[0.05,-0.39],lineWidth=10)
  mask2 = visual.TextStim(win,text="+",height=(MASK_DIAMETER+2.4))
  digitSet = range(DIGIT_RANGE[0],DIGIT_RANGE[1]+1) * NUM_PRACTICE_DIGIT_SETS
  random.shuffle(digitSet)
  correct = 0
  for i in digitSet:
    pressed = False
    timer.reset()
    displayDigit(win,i)
    tempLog = "(timeout,"
    reactionTime = 0
    while timer.getTime() < DIGIT_DISPLAY_TIME*2:
      if 1 in mouse.getPressed() and not pressed:
        reactionTime = timer.getTime()
        pressed = True
        if i == TARGET_DIGIT:
          losesound.play()
          tempLog = "(False,"
        else:
          correct += 1
          winsound.play()
          tempLog = "(True,"
    mask1.draw()
    mask2.draw()
    win.flip()
    while timer.getTime() < (DIGIT_DISPLAY_TIME + MASK_TIME)*2:
      if 1 in mouse.getPressed() and not pressed:
        reactionTime = timer.getTime()
        pressed = True
        if i == TARGET_DIGIT:
          losesound.play()
          tempLog = "(False,"
        else:
          correct += 1
          winsound.play()
          tempLog = "(True,"
      if(event.getKeys(keyList=['q','escape'])):
        quit()
    if not pressed and i == TARGET_DIGIT:
      reactionTime = timer.getTime()
      correct += 1
      tempLog = "(True,"
    log(tempLog+str(i)+","+str(reactionTime)+")")
  accuracy = (1.0*correct)/len(digitSet)
  feedback = visual.TextStim(win, text=("You had an accuracy of: %.0f%%" % (accuracy*100)) )
  feedback.draw()
  log("Accuracy: "+str(accuracy))
  win.flip()
  core.wait(5)
  ### SECTION 1 END

  ### SECTION 2 BEGIN
  log("Section 2")
  instructions = visual.TextStim(win,text="Sustained Attention\n\nIn this task, a number will be shown on the screen. "+
                                          "If it is not %d, then click your mouse anywhere on the screen. If it is %d" % (TARGET_DIGIT, TARGET_DIGIT) +
                                          ", then do not click anywhere. Please give equal importance to accuracy and speed.\n\nClick to Continue", wrapWidth=40)
  instructions.draw()
  win.flip()
  while 1 not in mouse.getPressed():
    pass
  while 1 in mouse.getPressed():
    pass

  mask1 = visual.Circle(win,radius=MASK_DIAMETER/2,pos=[0.01,-0.63],lineWidth=10)
  mask2 = visual.TextStim(win,text="+",height=(MASK_DIAMETER+2.4))
  digitSet = range(DIGIT_RANGE[0],DIGIT_RANGE[1]+1) * NUM_DIGIT_SETS
  random.shuffle(digitSet)
  correct = 0
  targetcorrect = 0
  correctrt = []
  incorrectrt = []
  temprts = []
  for i in digitSet:
    pressed = False
    timer.reset()
    displayDigit(win,i)
    tempLog = "(timeout,"
    reactionTime = 0
    while timer.getTime() < DIGIT_DISPLAY_TIME:
      if 1 in mouse.getPressed() and not pressed:
        reactionTime = timer.getTime()
        pressed = True
        if i == TARGET_DIGIT:
          incorrectrt.append(reactionTime)
          temprts = []
          losesound.play()
          tempLog = "(False,"
        else:
          correct += 1
          winsound.play()
          temprts.append(reactionTime)
          tempLog = "(True,"
    mask1.draw()
    mask2.draw()
    win.flip()
    while timer.getTime() < DIGIT_DISPLAY_TIME + MASK_TIME:
      if 1 in mouse.getPressed() and not pressed:
        reactionTime = timer.getTime()
        pressed = True
        if i == TARGET_DIGIT:
          incorrectrt.append(reactionTime)
          temprts = []
          losesound.play()
          tempLog = "(False,"
        else:
          correct += 1
          winsound.play()
          temprts.append(reactionTime)
          tempLog = "(True,"
      if(event.getKeys(keyList=['q','escape'])):
        quit()
    if not pressed and i == TARGET_DIGIT:
      reactionTime = timer.getTime()
      if len(temprts)>0:
        correctrt.append((sum(temprts)*1.0)/len(temprts))
      temprts = []
      targetcorrect += 1
      correct += 1
      tempLog = "(True,"
    log(tempLog+str(i)+","+str(reactionTime)+")")
  accuracy = (1.0*correct)/len(digitSet)
  targetaccuracy = (1.0*targetcorrect)/NUM_DIGIT_SETS
  feedback = visual.TextStim(win, text=("You had an accuracy of: %.0f%%" % (targetaccuracy*100.0)) )
  feedback.draw()
  win.flip()
  log("Accuracy: "+str(accuracy))
  core.wait(5)
  visual.TextStim(win, text="Thank You for your participation." ).draw()
  win.flip()
  core.wait(5)

  # write results to a xls file with all other subjects
  try:
    avgcorrectrt = 0
    if len(correctrt) > 0:
      avgcorrectrt = (1.0*sum(correctrt))/len(correctrt)
    avgincorrectrt = 0
    if len(incorrectrt) > 0:
      avgincorrectrt = (1.0*sum(incorrectrt))/len(incorrectrt)
    import xlrd,xlwt,xlutils.copy
    excelfile = "data/sart.xls"
    if not os.path.isfile(excelfile):
      w = xlwt.Workbook()
      ws = w.add_sheet("Data")
      style = xlwt.easyxf("font: bold on")
      ws.write(0,0,"Initials",style)
      ws.write(0,1,"Day",style)
      ws.write(0,2,"Accuracy",style)
      ws.write(0,3,"Target Accuracy",style)
      ws.write(0,4,"Avg RT when incorrect",style)
      ws.write(0,5,"Avg RT when correct",style)
      w.save(excelfile)
    oldfile = xlrd.open_workbook(excelfile,formatting_info=True)
    row = oldfile.sheet_by_index(0).nrows
    newfile = xlutils.copy.copy(oldfile)
    sheet = newfile.get_sheet(0)
    sheet.write(row,0,initials)
    sheet.write(row,1,testNo)
    sheet.write(row,2,accuracy)
    sheet.write(row,3,targetaccuracy)
    sheet.write(row,4,avgincorrectrt)
    sheet.write(row,5,avgcorrectrt)
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
  digit = visual.TextStim(win,text=str(digit))
  digit.setHeight(random.choice(DIGIT_SIZES))
  digit.draw()
  win.flip()

if __name__ == "__main__": main(sys.argv)
