from psychopy import visual, core, event, gui, sound
from datetime import datetime
import random
import numpy
import sys
import os
import csv
from collections import defaultdict
import json
from pprint import pprint


class DigitSpan(object):

    def __init__(self, **kwargs):
        self.DATA_DIR = kwargs.get('data_dir', 'digitspan_data')
        self.MONITOR = kwargs.get('monitor', 'testMonitor')
        self.MONITOR_RESOLUTION = kwargs.get('monitor_resolution', (1024, 768))
        self.SOUND_GENDER = kwargs.get('sound_gender', 'female')
        self.SOUND_PATH = kwargs.get('sound_path', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sounds'))
        self.SOUND_INIT_SAMPLES = kwargs.get('sound_init_samples', 48000)
        self.N_PRACTICE_TRIALS = kwargs.get('practice_trials', 2)
        self.LEN_PRACTICE_TRIAL = kwargs.get('practice_trial_len', 3)
        self.DIGIT_DISPLAY_TIME = kwargs.get('digit_display_time', 0.500)
        # renamed from "IN_BETWEEN_DIGITS_TIME"
        self.DIGIT_DISPLAY_GAP = kwargs.get('digit_display_gap', 0.300)
        self.NUM_TRIAL_BLOCKS = kwargs.get('trial_blocks', 1)
        self.INTER_TRIAL_DELAY = kwargs.get('inter_trial_delay', 0.500)
        self.sequence_range = {
            'forward': {
                'min': kwargs.get('forward_min', 3),
                'max': kwargs.get('forward_max', 15)
            },
            'reverse': {
                'min': kwargs.get('reverse_min', 2),
                'max': kwargs.get('reverse_max', 15)
            }
        }
        self.MAX_TRIALS_WRONG = kwargs.get('max_wrong_trials', 2)
        self.FULLSCREEN = kwargs.get('fullscreen', True)

        if not os.path.isdir(self.DATA_DIR):
            try:
                os.mkdir(self.DATA_DIR)
            except Exception as e:
                print e.getMessage()
                print "Error: cannot create data directory: " + self.DATA_DIR
                sys.exit(1)

        while True:
            # tuple of form: (subject_id, test_number)
            subject_info = self.get_subject_info(sys.argv[1:])
            self.log_file = os.path.join(
                self.DATA_DIR, '_'.join(subject_info) + '.csv')

            if os.path.isfile(self.log_file):
                rename_dialog = gui.Dlg(title='Error: Log File Exists')
                rename_dialog.addText("A log file with the subject ID " + subject_info[0] +
                                      " and test number " + subject_info[1] + " already exists. Overwrite?")
                rename_dialog.show()

                if rename_dialog.OK:
                    self.log_file = open(self.log_file, "w")
                    break
                else:
                    # not exactly necessary but w/e
                    continue
            else:
                self.log_file = open(self.log_file, "w")
                break

        # now log_file is a proper file
        self.data = []

        # this should load Pyo. However, it may require manually symlinking in
        # the newest liblo.
        sound.init(self.SOUND_INIT_SAMPLES, buffer=128)

        self.sound_correct = sound.Sound(value=440, secs=0.4)
        self.sound_incorrect = sound.Sound(value=330, secs=0.4)
        self.sound_files = [sound.Sound(value=os.path.join('sounds', fn)) for fn in os.listdir(self.SOUND_PATH)
                            if fn.startswith(self.SOUND_GENDER) and fn.endswith('.wav')]

        # this is a bad way of doing this. Should load from a file.
        self.sequences = {
            'forward':  [(9, 7),
                         (6, 3),
                         (5, 8, 2),
                         (6, 9, 4),
                         (7, 2, 8, 6),
                         (6, 4, 3, 9),
                         (4, 2, 7, 3, 1),
                         (7, 5, 8, 3, 6),
                         (3, 9, 2, 4, 8, 7),
                         (6, 1, 9, 4, 7, 3),
                         (4, 1, 7, 9, 3, 8, 6),
                         (6, 9, 1, 7, 4, 2, 8),
                         (3, 8, 2, 9, 6, 1, 7, 4),
                         (5, 8, 1, 3, 2, 6, 4, 7),
                         (2, 7, 5, 8, 6, 3, 1, 9, 4),
                         (7, 1, 3, 9, 4, 2, 5, 6, 8)],
            'reverse':  [(3, 1),
                         (2, 4),
                         (4, 6),
                         (5, 7),
                         (6, 2, 9),
                         (4, 7, 5),
                         (8, 2, 7, 9),
                         (4, 9, 6, 8),
                         (6, 5, 8, 4, 3),
                         (1, 5, 4, 8, 6),
                         (5, 3, 7, 4, 1, 8),
                         (7, 2, 4, 8, 5, 6),
                         (8, 1, 4, 9, 3, 6, 2),
                         (4, 7, 3, 9, 6, 2, 8),
                         (9, 4, 3, 7, 6, 2, 1, 8),
                         (7, 2, 8, 1, 5, 6, 4, 3)]
        }

        # after this line executes, the window is showing.
        self.window = visual.Window(
            self.MONITOR_RESOLUTION, monitor=self.MONITOR, units='deg', fullscr=self.FULLSCREEN)
        self.mouse = event.Mouse(win=self.window)

    def run(self):
        # initialization
        visual.TextStim(self.window,
                        text="Practice" + "\n\n" +
                        "In this task, you will hear a sequence of numbers. When the " +
                        "audio has finished, enter all of the numbers in the same " +
                        "order as they were recited." + "\n\n" +
                        "Press any key to continue.",
                        wrapWidth=30).draw()

        self.window.flip()
        event.waitKeys()
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

        # now we start section 1, practice trials
        self.practice_trial()

        # begin section 2
        self.main_trial('forward')

        # start section 3 - reverse digit span
        self.main_trial('reverse')

        # we can show the user some additonal things, but we prefer to end.
        self.quit()
        

    def quit(self):

        csvwriter = csv.writer(self.log_file, delimiter=',',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in self.data:
            csvwriter.writerow(row)

        visual.TextStim(
            self.window, "Thank you for your participation.").draw()
        self.window.flip()
        core.wait(3)

        # print self.data

        # self.log_file.write(json.dumps(self.data))
        self.log_file.close()
        self.window.close()
        sys.exit(0)


    def practice_trial(self):
        for trial_num in range(self.N_PRACTICE_TRIALS):
            expected = random.sample(xrange(10), self.LEN_PRACTICE_TRIAL)
            for num in expected:
                self.display_digit(num)
            self.window.flip()
            core.wait(self.DIGIT_DISPLAY_GAP)

            actual, timestamp = self.accept_sequence()
            if actual == expected:
                self.sound_correct.play()
            else:
                self.sound_incorrect.play()

            # we're going to offload ALL analysis to later stages. Task only records data.
            # new data format is [trial_type, trial_num, expected, actual,
            # timestamp]
            self.write_data('practice', trial_num, expected, actual, timestamp)

            core.wait(self.INTER_TRIAL_DELAY)  # between trials

    def main_trial(self, direction):
        intro_text = """In this section, listen to the sequence of numbers, \
and when the audio finishes, enter all the numbers in the {0} order \
as they were recited.""".format('same' if direction is 'forward' else 'REVERSE')

        if direction is 'reverse':
            intro_text += ' For example, if you hear 1, 2, 3, you would enter 3, 2, 1.\n'

        intro_text += '\nPress any key to continue.'

        visual.TextStim(self.window, text=intro_text, wrapWidth=30).draw()

        self.window.flip()
        event.waitKeys()

        for block_num in range(self.NUM_TRIAL_BLOCKS):
            trials_wrong = 0
            max_span = 0
            sequence = []
            sequence_index = 0
            sequence_size = len(sequence)
            repeat = 0

            def bye(self):
                visual.TextStim(self.window,
                                text="This block is over. Your max {0} digitspan was {1}.".format(direction, max_span)).draw()
                self.window.flip()
                core.wait(5)

            # while true is a bad habit
            while True:
                # if there's a pre-defined seq we can use, use it
                if sequence_index < len(self.sequences[direction]):
                    sequence = self.sequences[direction][sequence_index]
                    sequence_size = len(sequence)
                    sequence_index += 1
                else:
                    if repeat >= 2:
                        # else, define a new random seq, but only until
                        # FORWARD_MAX
                        if sequence_size >= self.sequence_range[direction]['max']:
                            bye(self)
                            break
                        else:
                            sequence_size += 1
                            repeat = 0
                    else:
                        repeat += 1

                    # this functionality differs a little from 3.0: repetitions in line are allowed
                    # whereas 3.0 specifically does not allow the same number
                    # to occur twice in series
                    sequence = numpy.random.choice(
                        10, size=sequence_size, replace=True)

                # at this point sequence and sequence_size are defined

                # read out all the digits in the sequence
                for digit in sequence:
                    self.display_digit(digit)
                    self.window.flip()
                    core.wait(self.DIGIT_DISPLAY_GAP)

                # take user input and log immediately -> this is the function
                # that actually reads in the data from the user
                actual, timestamp = self.accept_sequence(
                    direction is 'reverse')

                # write data...
                self.write_data(direction, block_num,
                                sequence, actual, timestamp)
                #self.data.append([direction, block_num, '-'.join(sequence), '-'.join(user_sequence[0]), user_sequence[1]])

                if all(map(lambda x, y: x == y, actual, sequence)):
                    self.sound_correct.play()
                    max_span = max(max_span, sequence_size)
                    trials_wrong = 0
                else:
                    self.sound_incorrect.play()
                    trials_wrong += 1

                # if you fail N times (2 default) in a row, you're done
                if trials_wrong >= self.MAX_TRIALS_WRONG:
                    core.wait(0.5)  # ?
                    bye(self)
                    break

                self.window.flip()
                core.wait(0.5)

    def get_subject_info(self, args=[]):
        # no cli args
        if len(args) == 0:
            subject_info = gui.DlgFromDict(
                dictionary={'Subject ID': '', 'Test Number': '1'},
                title='Digit-Span Task')

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
            print "Usage: digitspan.py [subject_id] [subject_test_number] -- Warning: functionality not guaranteed when called from CLI"
            sys.exit(1)

        return subject_id, subject_test_number

    def display_digit(self, digit):
        self.window.flip()
        self.sound_files[digit].play()
        core.wait(self.DIGIT_DISPLAY_TIME +
                  self.sound_files[digit].getDuration())

    # returns (<list: clicked>, <timestemp: time_elapsed>)
    def accept_sequence(self, reverse=False):
        instructions = visual.TextStim(self.window,
                                       text="Type the digits in the {0}".format('reverse ' if reverse else '') +
                                       "order in which they were recited." +
                                       "Press the delete button if you want to erase the last letter " +
                                       "you typed. For any digits you do not remember, press the letter x " +
                                       "instead of guessing. Press enter when you are done.",
                                       pos=(0, 6),
                                       wrapWidth=30)
        instructions.setAutoDraw(True)  # auto-rerender on each windowflip
        instructions.draw()
        self.window.flip()

        # NUMBERS = ramge(10)
        timer = core.Clock()
        clicked = []  # list for return to user
        numbers = []  # list to hold pointers for display
        event.clearEvents()

        # my thinking for this loop was:
        #   1. get the current keybuffer.
        #   2. loop through several possibilities and act accordingly
        #   3. repeat until the user hits enter, then break the loop and return.
        # However, this doesn't work apparently, and the documentation for how getKeys()
        # works is rather limited, even in Pygame

        while True:
            if event.getKeys(keyList=['q', 'escape']):
                # self.log_file.write(json.dumps(self.data))
                self.quit()

            if event.getKeys(keyList=['backspace', 'delete', '[.]', 'period', '.']) and len(clicked) > 0:
                clicked = clicked[:-1]
                # I don't think this is necessary before the next step.
                numbers[-1].setAutoDraw(False)
                # ...[-1] should get GC'd and autoremoved from the window. I think.
                numbers = numbers[:-1]
                self.window.flip()
                core.wait(0.200)

            if event.getKeys(keyList=['num_enter', 'return']):
                # I highly doubt these two are necessary. But apparently they
                # are.
                map(lambda n: n.setAutoDraw(False), numbers)
                instructions.setAutoDraw(False)
                if reverse:
                    clicked.reverse()
                return (clicked, timer.getTime())
                # this is where it returns out from the while true loop!

            if event.getKeys(keyList=['x']):
                clicked.append('x')
                ast = visual.TextStim(self.window, text="x", color="DarkMagenta",
                                      pos=(-10 + 2 * len(numbers), 0))
                ast.setAutoDraw(True)
                ast.draw()
                numbers.append(ast)
                self.window.flip()
                core.wait(0.200)

            for i in range(10):  # we're looking for nums 0..9
                capture_list = "{0},num_{0},[{0}]".format(i).split(',')
                if event.getKeys(keyList=capture_list):
                    clicked.append(i)
                    num = visual.TextStim(self.window, text=str(i), color="DarkMagenta",
                                          pos=(-10 + 2 * len(numbers), 0))
                    num.setAutoDraw(True)
                    num.draw()
                    numbers.append(num)
                    self.window.flip()
                    core.wait(0.200)
                    break

    def write_data(self, direction, trial_num, expected, actual, timestamp):
        # '-'.join(...) for csv compat
        self.data.append([direction, trial_num,
                          '-'.join(str(i) for i in expected), '-'.join(str(i) for i in actual), timestamp])

# if __name__ == '__main__':
#     ds = DigitSpan(data_dir = "kelly_data_digitspan", monitor_resolution=(1600, 900))
#     ds.run()
#     sys.exit(0)
