=== How to use DigitSpan and SART v2.0 ===
@author abizer@berkeley.edu

Introduction

These tasks are designed to be as plug-and-play as possible, with a simple CSV-based data output format.

The tasks have been tested to run on PsychoPy Standalone version 1.84.0 only. The PsychoPy development team is not very consistent about maintaining backwards compatability of experiment scripts between versions, and the tasks may need updating to work with future releases.

Usage:

	DigitSpan:
		1. Open PsychoPy 1.84.0
		2. Open argentometry/digitspan.py
		3. Click the green "run" button on the top row of the PsychoPy command ribbon
		4. The test will begin. The instructions for the user are on the initial screen.
		5. Once the test has successfully completed in its entirety, data will be written to a folder entitled "digitspan_data" in the working directory, to a file named '<subject_id>_<test_num>.csv'
		6. Once the test has completed, (i.e., the "Thank you for your participation." screen has shown), the test should quit, and you should take a look at the data that was printed to make sure it looks reasonable.
		7. If the test errors, or one needs to quit, the program can be ended by typing "q", or in the case of non-responsiveness, by pressing Command-Alt-Esc and selecting PsychoPy from the Force Quit menu.

	SART:
		1. Open PsychoPy 1.84.0
		2. Open argentometry/sart.py
		3. Click the green "run" button on the top row of the PsychoPy command ribbon
		4. The test will begin. Instructions for the user will be presented on the initial screen.
		5. Once the test has successfully completed, data will be written in a folder entitled "sart_data" (by default, this can be overridden in the settings) in the working directory, to a file file named '<subject_id>_<test_num>.csv'.
		6. Once the test has completed, (i.e. the "Thank you for your participation." screen has shown), the program will quit. You should take a look at the data that was printed and make sure it looks reasonable.
		7. If the test errors, pressing "q" at any time during the trials will quit the test immediately. Alternatively, Command-Alt-Esc can be used to force PsychoPy to quit from the Force Quit menu.

Known Bugs:
      Due to some problems in the audio libraries PsychoPy uses on x64 Macs, the program may occasionally have trouble quitting, or may have irregular sound. On failures to quit, the Command-Alt-Esc method seems to be the most reliable way to regain control, at the risk of losing data. On sound problems, one should see if changing the value of the sampling frequency in the sound initialization from 48000 to 44100 fixes the problem. Different computers may require different values.

Development Notes:
	The tasks have been written to be somewhat modular and adaptable. Changing parameters can be achieved by passing keyword arguments to the object created at the very bottom of each file. Please contibute any improvements, extensions, or bug fixes by contacting abizer@berkeley.edu or by filing an issue/pull request in the Git repository. Credit and attribution is given to Omid Rhezaii, who wrote the initial version of the task, as well as to Sahar Yousef, Dr. Michael Silver, Kelly Byrne, Liz Lawler, and other contributors at UC Berkeley, Silver Lab, and elsewhere.
