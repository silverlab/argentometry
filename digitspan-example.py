from argentometry import digitspan
import sys

def main():
    task = digitspan.DigitSpan(
        data_dir = "kelly_data_digitspan",
        monitor_resolution = (1600, 900),
        fullscreen = True) 
      # sound_init_samples = 44100
    task.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
