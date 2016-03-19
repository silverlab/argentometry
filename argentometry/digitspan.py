from psychopy import visual, core, event, gui, sound
from datetime import datetime
import random, numpy, sys, os
from collections import defaultdict
import simplejson as json
from pprint import pprint

class DigitSpan(object):
    def __init__(self, **kwargs):
        self.DATA_DIR = kwargs.get('data_dir', 'digitspan_data')
        self.MONITOR = kwargs.get('monitor', 'testMonitor')
        self.MONITOR_RESOLUTION = kwargs.get('monitor_resolution', (800, 600))
        self.SOUND_GENDER = kwargs.get('sound_gender', 'female')
        self.N_PRACTICE_TRIALS = kwargs.get('practice_trials', 2)
        self.LEN_PRACTICE_TRIAL = kwargs.get('practice_trial_len', 3)
        self.DIGIT_DISPLAY_TIME = kwargs.get('digit_display_time', 0.500)
        self.DIGIT_DISPLAY_GAP = kwargs.get('digit_display_gap', 0.500) # renamed from "IN_BETWEEN_DIGITS_TIME"
        self.NUM_TRIAL_BLOCKS = kwargs.get('trial_blocks', 1)
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
            self.log_file = os.path.join(self.DATA_DIR, '_'.join(subject_info) + '.json')

            if os.path.isfile(self.log_file):
                rename_dialog = gui.Dlg(title = 'Error: Log File Exists')
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
        self.data = {}
        self.section = {}  # better logging
        self.section_num = 0
        
        sound.init(48000, buffer=128)

        self.sound_correct = sound.Sound(value = 440, secs = 0.4)
        self.sound_incorrect = sound.Sound(value = 330, secs = 0.4)
        self.sound_files = [sound.Sound(value = os.path.join('sounds', fn)) for fn in os.listdir('sounds') 
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
        self.window = visual.Window(self.MONITOR_RESOLUTION, monitor = self.MONITOR, units = 'deg', fullscr = False)
        self.mouse = event.Mouse(win = self.window)

    def run_task(self):
        # initialization
        visual.TextStim(self.window,
            text = "Practice" + "\n\n" +
                   "In this task, you will hear a sequence of numbers. When the " +
                   "audio has finished, enter all of the numbers in the same " +
                   "order as they were recited." + "\n\n" +
                   "Press any key to continue.",
                                wrapWidth = 30).draw()

        self.window.flip()
        event.waitKeys()
        visual.TextStim(self.window, text = "This is the sound of a correct response.").draw()
        self.window.flip()
        self.sound_correct.play()
        core.wait(2)
        visual.TextStim(self.window, text = "This is the sound of an incorrect response.").draw()
        self.window.flip()
        self.sound_incorrect.play()
        core.wait(2)

        # now we start section 1, practice trials
        # every time we end a section, we save self.section to self.data and restart self.section.
        self.section_num += 1

        self.practice_trial()

        # end section 1, self.data[section_num] is set in the trial block itself 
        
        # begin section 2
        self.section_num += 1
        self.section = {}

        self.main_trial('forward')
        # end of section 2 - forward digit span

        # start section 3 - reverse digit span
        self.section_num += 1
        self.section = {}

        self.main_trial('reverse')
        # end section 3 - reverse digit span
        
        # we can show the user some additonal things, but we prefer to end.
        visual.TextStim(self.window, "Thank you for your participation.").draw()
        self.window.flip()

        self.log_file.write(json.dumps(self.data))
        self.log_file.close()
        core.wait(3)
        core.quit()
        sys.exit(0)

    def practice_trial(self):
        for trial_num in range(self.N_PRACTICE_TRIALS):
            trial = random.sample(xrange(10), self.LEN_PRACTICE_TRIAL)
            for num in trial:
               self.display_digit(num)
            self.window.flip()
            core.wait(self.DIGIT_DISPLAY_GAP)

            user_sequence = self.accept_sequence()
            if user_sequence[0] == trial:
                self.sound_correct.play()
            else:
                self.sound_incorrect.play()

            # we're going to offload ALL analysis to later stages. Task only records data.
            self.section[trial_num] = {'expected': trial,
                                       'actual': user_sequence[0],
                                       'timestamp': user_sequence[1]}
                                       
            core.wait(0.500)  # between trials
        self.data[self.section_num] = self.section

    def main_trial(self, direction):
        intro_text = """In this section, listen to the sequence of numbers, \
and when the audio finishes, enter all the numbers in the {0} order \
as they were recited.""".format('same' if direction is 'forward' else 'REVERSE')

        if direction is 'reverse':
            intro_text += ' For example, if you hear 1, 2, 3, you would enter 3, 2, 1.\n'

        intro_text += '\nPress any key to continue.'
      
        visual.TextStim(self.window, text = intro_text, wrapWidth = 30).draw()

        self.window.flip()
        event.waitKeys()

        for block_num in range(self.NUM_TRIAL_BLOCKS):
            trials_wrong = 0
            max_span = 0
            sequence = []
            sequence_index = 0
            sequence_size = len(sequence)
            repeat = 0

            block = defaultdict(list)
            block['meta'] = {}

            def bye(self):
                visual.TextStim(self.window,
                    text = "This block is over. Your max {0} digitspan was {1}.".format(direction, max_span)).draw()
                self.window.flip()
                block['meta']['max'] = max_span
                core.wait(5)

            # while true is a bad habit
            while True:
                # if there's a pre-defined seq we can use, use it
                if sequence_index < len(self.sequences[direction]):
                    # easy
                    sequence = self.sequences[direction][sequence_index]
                    sequence_size = len(sequence)
                    sequence_index += 1
                    self.section[sequence_size] = []
                else:
                    if repeat >= 2:
                        # else, define a new random seq, but only until FORWARD_MAX
                        if sequence_size >= self.sequence_range[direction]['max']:
                            bye(self)
                            break
                        else:
                            sequence_size += 1
                            repeat = 0
                    else:
                        repeat += 1

                    # this functionality differs a little from 3.0: repetitions in line are allowed
                    # whereas 3.0 specifically does not allow the same number to occur twice in series
                    sequence = numpy.random.choice(10, size = sequence_size, replace = True)

                # at this point sequence and sequence_size are defined

                # read out all the digits in the sequence
                for digit in sequence:
                    self.display_digit(digit)
                    self.window.flip()
                    core.wait(self.DIGIT_DISPLAY_GAP)

                # take user input and log immediately 
                user_sequence = self.accept_sequence(direction is 'reverse')
                block[sequence_size].append({'expected': sequence,
                                             'actual': user_sequence[0],
                                             'timestamp': user_sequence[1]})
       
                if all(map(lambda x, y: x == y, user_sequence[0], sequence)):
                    self.sound_correct.play()
                    max_span = max(max_span, sequence_size)
                    trials_wrong = 0
                else:
                    self.sound_incorrect.play()
                    trials_wrong += 1

                # if you fail twice in a row, you're done
                if trials_wrong >= self.MAX_TRIALS_WRONG:
                    core.wait(0.5)  # ?
                    bye(self)
                    break

                self.window.flip()
                core.wait(0.5)

            self.section[block_num] = dict(block)

        self.data[self.section_num] = {direction: self.section}

    def get_subject_info(self, args = []):
        # no cli args
        if len(args) == 0:
            subject_info = gui.DlgFromDict(
                dictionary={'Subject ID': '', 'Test Number': '1'},
                title = 'Digit-Span Task')

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
            print "Usage: digitspan.py [subject_id] [subject_test_number]"
            sys.exit(1)

        return subject_id, subject_test_number

    def display_digit(self, digit):
        self.window.flip()
        self.sound_files[digit].play()
        core.wait(self.DIGIT_DISPLAY_TIME + self.sound_files[digit].getDuration())

    # returns (<list: clicked>, <timestemp: time_elapsed>)
    def accept_sequence(self, reverse = False):
        instructions = visual.TextStim(self.window, 
            text = "Type the digits in the {0}".format('reverse ' if reverse else '') +
                   "order in which they were recited." +
                   "Press the delete button if you want to erase the last letter " +
                   "you typed. For any digits you do not remember, use the asterisk (*) " +
                   "button instead of guessing. Press enter when you are done.", 
            pos = (0, 6),
            wrapWidth = 30)
        instructions.setAutoDraw(True)  # auto-rerender on each windowflip
        instructions.draw()
        self.window.flip()

        # NUMBERS = ramge(10)
        timer = core.Clock()
        clicked = []  # list for return to user
        numbers = []  # list to hold pointers for display
        event.clearEvents()

        # my thinking for this loop is as such:
        #   1. get the current keybuffer.
        #   2. loop through several possibilities and act accordingly
        #   3. repeat until the user hits enter, then break the loop and return.

        while True:
            if event.getKeys(keyList = ['q', 'escape']):
                self.log_file.write(json.dumps(self.data))
                self.log_file.close()
                core.quit()
                sys.exit(0)

            if event.getKeys(keyList = ['backspace', 'delete', '[.]', 'period', '.']) and len(clicked) > 0:
                clicked = clicked[:-1]
                numbers[-1].setAutoDraw(False) # I don't think this is necessary
                numbers = numbers[:-1] # ...[-1] should get GC'd and autoremoved from the window.
                self.window.flip()
                core.wait(0.200)

            if event.getKeys(keyList = ['num_enter', 'return']):
                map(lambda n: n.setAutoDraw(False), numbers)
                instructions.setAutoDraw(False)
                # I highly doubt these last two are necessary. But apparently they are.
                if reverse:
                    clicked.reverse();
                return (clicked, timer.getTime())
                # this is where it returns out from the while true loop!

            if event.getKeys(keyList=['asterisk']):
                clicked.append('*')
                ast = visual.TextStim(self.window, text="*", color="DarkMagenta",
                                      pos=(-10 + 2 * len(numbers), 0))
                ast.setAutoDraw(True)
                ast.draw()
                numbers.append(ast)
                self.window.flip()
                core.wait(0.200)

            for i in range(10):  # range(10) because we're looking for nums 0..9
                capture_list = "{0},num_{0},[{0}]".format(i).split(',')
                if event.getKeys(keyList=capture_list):
                    clicked.append(i)
                    num = visual.TextStim(self.window, text = str(i), color = "DarkMagenta",
                                          pos = (-10 + 2 * len(numbers), 0))
                    num.setAutoDraw(True)
                    num.draw()
                    numbers.append(num)
                    self.window.flip()
                    core.wait(0.200)
                    break

if __name__ == '__main__':
    ds = DigitSpan()
    ds.run_task()
