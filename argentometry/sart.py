
from psychopy import visual, core, event, gui, sound
import random
import numpy
import sys
import os
import csv
from datetime import datetime
from collections import namedtuple


class SART(object):

    def __init__(self, **kwargs):
        self.DIGIT_DISPLAY_TIME = kwargs.get('digit_display_time', 0.250)
        self.DIGIT_RANGE = kwargs.get('digit_range', (0, 9))
        self.DIGIT_SIZES = kwargs.get('digit_sizes', [1.8, 2.7, 3.5, 3.8, 4.5])
        self.TARGET_DIGIT = kwargs.get(
            'target_digit', random.randint(*self.DIGIT_RANGE))
        self.NUM_DIGIT_SETS = kwargs.get('num_digit_sets', 25)
        self.MASK_TIME = kwargs.get('mask_time', 0.900)
        self.MASK_DIAMETER = kwargs.get('mask_diameter', 3.0)
        self.MAX_FAILS = kwargs.get('max_fails', 3)
        self.CORRECT_FREQ = kwargs.get('correct_freq', 440)
        self.WRONG_FREQ = kwargs.get('wrong_freq', 330)
        self.TONE_LENGTH = kwargs.get('tone_length', 0.5)
        self.PRACTICE_DIGIT_SETS = kwargs.get('practice_digit_sets', 2)
        self.DATA_DIR = kwargs.get('data_dir', 'sart_data')
        self.MONITOR_RESOLUTION = kwargs.get('monitor_resolution', (1024, 768))

        # if the datadir doesn't exist, create it. 
        if not os.path.isdir(self.DATA_DIR):
            try:
                os.mkdir(self.DATA_DIR)
            except Exception as e:
                print e.getMessage()
                print "Error: cannot create data directory: " + self.DATA_DIR
                sys.exit(1)

        # then, collect the subject's ID and text number. If the file already exists, prompt to confirm overwrite
        while True:
            subject_info = self.get_subject_info(sys.argv[1:])
            self.log_file = os.path.join(
                self.DATA_DIR, '_'.join(subject_info) + '.csv')

            if os.path.isfile(self.log_file):
                rename_dialog = gui.Dlg(title='Error: Log File Exists')
                rename_dialog.addText(
                    'A log file with this subject id ({0}) and test number {1} already exists. Overwrite?'.format(*subject_info))
                rename_dialog.show()

                if rename_dialog.OK:
                    break
                else:
                    break
            else:
                break

        #self.log_file = open(self.log_file, "w")

        self.data = []

        # this is the basic data output format (to CSV)
        self.Datum = namedtuple(
            'Datum', ['trial', 'target', 'digit', 'success', 'rt', 'note'])

        sound.init(48000, buffer=128)

        # init components for rest of experiment
        self.sound_correct = sound.Sound(
            value=self.CORRECT_FREQ, secs=self.TONE_LENGTH)
        self.sound_incorrect = sound.Sound(
            value=self.WRONG_FREQ, secs=self.TONE_LENGTH)

        self.window = visual.Window(
            self.MONITOR_RESOLUTION, monitor='testMonitor', units='cm', fullscr=False)
        self.mouse = event.Mouse(win=self.window)

        self.MASTER_CLOCK = core.Clock() # this is never used, holdover from original code
        self.TIMER = core.Clock() 

    def run_task(self):
        instructions = visual.TextStim(self.window, text="Practice\n\nIn this task, a number will be shown on the screen.\n\n" +
                                       "If it is not {0}, then click your mouse anywhere on the screen. If it is a {0}, then do not click anywhere.\n\n".format(self.TARGET_DIGIT) +
                                       "Please give equal importance to accuracy and speed.\n\nClick anywhere to continue.", wrapWidth=30).draw()
        self.window.flip()

        # wait for a mouseclick to continue
        while 1 not in self.mouse.getPressed():
            pass

        visual.TextStim(
            self.window, text="This is the sound of a correct response.").draw()
        self.window.flip()
        self.sound_correct.play()
        core.wait(2)
        visual.TextStim(
            self.window, text="This is the sound of an incorrect response.").draw()
        self.window.flip()
        self.sound_incorrect.play()
        core.wait(2)

        # run the practice trial
        self.practice_trial()

        instructions = visual.TextStim(
            self.window,
            text="Sustained Attention\n\n" +
            "In this task, a number will be shown on the screen.\n\n" +
            "If it is not {0}, then click you rmouse anywhere on the screen. If it is {0}, do not click anywhere.\n\n".format(self.TARGET_DIGIT) +
            "Please give equal importance to accuracy and speed.\n\n" +
                 "Click anywhere to continue.",
            wrapWidth=30).draw()

        self.window.flip()

        # wait for mouse click
        while 1 not in self.mouse.getPressed():
            pass

        self.main_trial()

        with open(self.log_file, "w") as output:
            csvwriter = csv.writer(output, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.data:
                csvwriter.writerow(row)

        goodbye = visual.TextStim(self.window, "Thank you for your participation.", wrapWidth = 30).draw()
        self.window.flip()
        core.wait(2)

        self.window.close()
        pass

    def practice_trial(self):

       # clear the mouseclick buffers
        # while 1 not in self.mouse.getPressed():
        #     pass
        # while 1 in self.mouse.getPressed():
        #     pass

        mask1 = visual.Circle(
            self.window, radius=self.MASK_DIAMETER / 2, pos=[0.05, -0.39], lineWidth=10)
        mask2 = visual.TextStim(self.window, text="+",
                                height=(self.MASK_DIAMETER + 2.4))
        digitSet = range(self.DIGIT_RANGE[0], self.DIGIT_RANGE[
                         1] + 1) * self.PRACTICE_DIGIT_SETS
        random.shuffle(digitSet)

        correct = 0

        for digit in digitSet:
            pressed = False
            self.TIMER.reset()

            self.displayDigit(digit)

            reactionTime = 0
            success = False
            note = ''

            # in this loop the digit is visible
            while self.TIMER.getTime() < self.DIGIT_DISPLAY_TIME * 2:
                if 1 in self.mouse.getPressed() and not pressed:
                    reactionTime = self.TIMER.getTime()
                    pressed = True

                    success = (digit is not self.TARGET_DIGIT)
                    note = 'press nomask'

                    # mouseclick was registered before the mask was shown.
                    # The test was successful if the digit displayed
                    # was NOT the target digit.

                    if success:
                        correct += 1
                        self.sound_correct.play()
                    else:
                        self.sound_incorrect.play()

            mask1.draw()
            mask2.draw()
            self.window.flip()

            # in this loop the digit is hidden and the mask is visible
            while self.TIMER.getTime() < (self.DIGIT_DISPLAY_TIME + self.MASK_TIME) * 2:
                if 1 in self.mouse.getPressed() and not pressed:
                    reactionTime = self.TIMER.getTime()
                    pressed = True

                    success = (digit is not self.TARGET_DIGIT)
                    note = 'press mask'

                    # mouseclick was registered after the mask was shown.
                    # The test was successful if the digit displayed
                    # was NOT the target digit.

                    if success:
                        correct += 1
                        self.sound_correct.play()
                    else:
                        self.sound_incorrect.play()

                if event.getKeys(keyList=['q', 'excape']):
                    # need to write data
                    core.quit()

            if not pressed:
                reactionTime = self.TIMER.getTime()
                success = (digit is self.TARGET_DIGIT)
                note = 'nopress'

                # no mouseclick was registered.
                # the test was successful if the target digit WAS the digit
                # displayed.

                if success:
                    correct += 1
                    self.sound_correct.play()
                else:
                    self.sound_incorrect.play()

            d = self.Datum(trial='practice',
                           target=self.TARGET_DIGIT,
                           digit=digit,
                           success=success,
                           rt=reactionTime,
                           note=note)

            self.data.append(d)

        accuracy = (1.0 * correct) / len(digitSet)
        feedback = visual.TextStim(
            self.window, text="You had an accuracy of {:%}".format(accuracy))
        feedback.draw()
        self.window.flip()
        core.wait(5)

    def main_trial(self):

        # flush mouse click buffers
        # while 1 not in self.mouse.getPressed():
        #     pass
        # while 1 in self.mouse.getPressed():
        #     pass

        mask1 = visual.Circle(
            self.window, radius=self.MASK_DIAMETER / 2, pos=[0.01, -0.63], lineWidth=10)
        mask2 = visual.TextStim(self.window, text="+",
                                height=self.MASK_DIAMETER + 2.4)
        digitSet = range(self.DIGIT_RANGE[0], self.DIGIT_RANGE[
                         1] + 1) * self.NUM_DIGIT_SETS
        random.shuffle(digitSet)

        correct = 0

        for digit in digitSet:
            pressed = False
            self.TIMER.reset()
            self.displayDigit(digit)

            reactionTime = 0
            success = False
            note = ''

            while self.TIMER.getTime() < self.DIGIT_DISPLAY_TIME:
                if 1 in self.mouse.getPressed() and not pressed:
                    pressed = True
                    reactionTime = self.TIMER.getTime()
                    success = (digit is not self.TARGET_DIGIT)
                    note = 'press nomask'

                    if success:
                        correct += 1
                        self.sound_correct.play()
                    else:
                        self.sound_incorrect.play()

            mask1.draw()
            mask2.draw()
            self.window.flip()

            while self.TIMER.getTime() < self.DIGIT_DISPLAY_TIME + self.MASK_TIME:
                if 1 in self.mouse.getPressed() and not pressed:
                    pressed = True

                    reactionTime = self.TIMER.getTime()
                    success = (digit is not self.TARGET_DIGIT)
                    note = 'press mask'

                    if success:
                        correct += 1
                        self.sound_correct.play()
                    else:
                        self.sound_incorrect.play()

                if event.getKeys(keyList=['q', 'escape']):
                    core.quit()

            if not pressed:
                reactionTime = self.TIMER.getTime()
                success = (digit is self.TARGET_DIGIT)
                note = 'nopress'

                # no mouseclick was registered.
                # the test was successful if the target digit WAS the digit
                # displayed.

                if success:
                    correct += 1
                    self.sound_correct.play()
                else:
                    self.sound_incorrect.play()

            d = self.Datum(trial='main',
                           target=self.TARGET_DIGIT,
                           digit=digit,
                           success=success,
                           rt=reactionTime,
                           note=note)

            self.data.append(d)

            print d

        accuracy = (1.0 * correct) / len(digitSet)
        targetaccuracy = (1.0 * 5) / self.NUM_DIGIT_SETS
        feedback = visual.TextStim(
            self.window, text="--Disregard-- You had an accuracy of {:%}".format(targetaccuracy))
        feedback.draw()
        self.window.flip()

    def displayDigit(self, digit):
        digit = visual.TextStim(self.window, text=str(digit))
        digit.setHeight(random.choice(self.DIGIT_SIZES))
        digit.draw()
        self.window.flip()

    def get_subject_info(self, args=[]):
        # no cli args
        if len(args) == 0:
            subject_info = gui.DlgFromDict(
                dictionary={'Subject ID': '', 'Test Number': '1'},
                title='SART Task')

            if (subject_info.OK):
                subject_id = subject_info.data[0].upper()
                subject_test_number = subject_info.data[1]
            else:
                sys.exit(1)
        # all args recvd
        elif len(args) == 2:
            subject_id = args[0].upper()
            subject_test_number = args[1]
        else:
            print "Usage: sart.py [subject_id] [test_number] -- Warning: functionality not guaranteed when called from CLI"
            sys.exit(1)

        return subject_id, subject_test_number

if __name__ == '__main__':
    task = SART(monitor_resolution = (1600, 900))
    task.run_task()
