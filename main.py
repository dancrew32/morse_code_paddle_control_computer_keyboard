import threading
import time

from pynput import mouse, keyboard

# TODO(DAN): find something the plays asynchronously and isn't so laggy
from pysinewave import SineWave


MORSE = {
        'A':'.-',
        'B':'-...',
        'C':'-.-.',
        'D':'-..',
        'E':'.',
        'F':'..-.',
        'G':'--.',
        'H':'....',
        'I':'..',
        'J':'.---',
        'K':'-.-',
        'L':'.-..',
        'M':'--',
        'N':'-.',
        'O':'---',
        'P':'.--.',
        'Q':'--.-',
        'R':'.-.',
        'S':'...',
        'T':'-',
        'U':'..-',
        'V':'...-',
        'W':'.--',
        'X':'-..-',
        'Y':'-.--',
        'Z':'--..',
        '1':'.----',
        '2':'..---',
        '3':'...--',
        '4':'....-',
        '5':'.....',
        '6':'-....',
        '7':'--...',
        '8':'---..',
        '9':'----.',
        '0':'-----',
        ', ':'--..--',
        '.':'.-.-.-',
        '?':'..--..',
        '/':'-..-.',
        '-':'-....-',
        '(':'-.--.',
        ')':'-.--.-',
        '!':'-.-.--',
  
        ## TODO(DAN): come up with common shortcuts for CW prosigns
        'esc':'........',
        '=':'-...-',
        }

MORSE_TO_CHAR = dict([(value, key) for key, value in MORSE.items()])

# Use this controller to trigger actual keyboard key presses
controller = keyboard.Controller()

# Current sequency of dits & dahs.
# When the timer is up, this is the letter that is interpreted.
current = []

# dit and dah timer used to make sure we don't send too many and get crazy
dit_timer = None
dah_timer = None

# TODO(DAN): use an actual event loop with predictable timing
speed = 0.5

# TODO(DAN): find better sinewave tone generator, use variable pitch e.g. 600Hz
dit_sine = SineWave(pitch=12)
dah_sine = SineWave(pitch=12)

def end_char():
    global current
    global controller
    if current:
        # TODO(DAN): interpret dit/dahs as morse code key, make key press
        char = MORSE_TO_CHAR.get(''.join(current))
        if char:
            char_lower = char.lower()
            
            # TODO(DAN): use map for special chars
            if char_lower == 'esc':
                char_lower = keyboard.Key.esc
            elif char_lower == '=':
                char_lower = keyboard.Key.enter
                
            print(char_lower)
            controller.press(char_lower)
            controller.release(char_lower)
    current = []

# Global for keeping track of when a letter has been completed
char_timer = threading.Timer(1.0, end_char) 

# Kill the dit sine wave
def dit_complete():
    global dit_sine
    #dit_sine.stop()

# Kill the dah sine wave
def dah_complete():
    global sinewave
    #dah_sine.stop()

    
def handle_dit():
    global dit_sine
    global speed
    global dit_timer
    global dah_timer
    global current

    if not dit_timer or not dit_timer.is_alive():
        #dit_sine.stop()
        #dit_sine.play()
        print('dit');
        dit_timer = threading.Timer(0.11 * speed, dit_complete) # TODO(DAN): timer should be .1 * speed
        current.append('.')
        dit_timer.start()

def handle_dah():
    global dah_sine
    global speed
    global dit_timer
    global dah_timer
    global current
    if not dah_timer or not dah_timer.is_alive():
        #dah_sine.stop()
        #dah_sine.play()
        print('dah');
        dah_timer = threading.Timer(0.18 * speed, dah_complete) # TODO(DAN): timer should be .3 * speed
        current.append('-')
        dah_timer.start()

        
# TODO(DAN): this should not be what triggers the actual sounds,
# rather changes modifiers that an event loop (TODO) picks up.
# We use Left-Control for dit and Right-Control for dah
# This is to match the VBand USB Paddle adapter protocol:
# https://hamradio.solutions/vband/ (see store $25 USD)
def on_press(key):
    global speed
    global char_timer

    if key == keyboard.Key.ctrl_l:
        if char_timer:
            char_timer.cancel()
        handle_dit()
        char_timer = threading.Timer(1.0 * speed, end_char) 
        char_timer.start()

    if key == keyboard.Key.ctrl_r:
        if char_timer:
            char_timer.cancel()
        handle_dah()
        char_timer = threading.Timer(1.0 * speed, end_char) 
        char_timer.start()


# TODO(DAN): on release should affect modifiers in the event loop
# TODO(DAN): come up with an application pause or quit routine based on SK prosigns or something cool
def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        # exit() #TODO(DAN): quit strategy
        pass


# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
   listener.join()


# TODO(DAN): event loop depleting queue
