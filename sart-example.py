from argentometry import sart
import sys

def main():
    task = sart.SART(
        data_dir = "kelly_data_sart",
        monitor_resolution = (1600, 900),
        fullscreen = True) 
        # sound_init_samples = 44100
    task.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
