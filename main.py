import threading
import time

from pynput import mouse, keyboard

controller = keyboard.Controller()

MORSE = {

    # Letters
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',

    # Digits
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----',

    # Punctuation
    ',': '--..--',
    '.': '.-.-.-',
    '?': '..--..',
    '/': '-..-.',
    '-': '-....-',
    '(': '-.--.',
    ')': '-.--.-',
    '!': '-.-.--',
    '+': '.-.-.',
    '-': '-....-',
    '_': '..--.-',
    '"': '.-..-.',
    '$': '...-..-',
    '@': '.--.-.',
    '=': '-...-',

    # Getting creative with less useful chars
    '¿': '..-.-', # Left alt?
    '¡': '--...-', # Left ctrl?
    'ch': '----', # Space?
    'shift': '------', # Shift?
    'err': '......', # Backspace?
    'esc': '.......', # Esc?
}

MORSE_TO_CHAR = dict([(value, key) for key, value in MORSE.items()])

CURRENT_MODE = 'insert'  # or 'command'

LEFT_ALT_DOWN = False
LEFT_CTRL_DOWN = False
LEFT_SHIFT_DOWN = False


# The dits and dahs for the character that the user is currently trying to type:
current = []

# The characters that the user has successfully typed:
text = []

dit_timer = None
dah_timer = None

speed = 0.5


# TODO(DAN): keep trick of what was said, toggle SHIFT
#dit_sine = SineWave(pitch=12)
#dah_sine = SineWave(pitch=12)

def end_char():
    global current
    global controller
    global LEFT_ALT_DOWN
    global LEFT_CTRL_DOWN
    global LEFT_SHIFT_DOWN
    if current:
        # TODO(DAN): interpret dit/dahs as morse code key, make key press
        char = MORSE_TO_CHAR.get(''.join(current))
        
        if char:
            char_lower = char.lower()
            if char_lower == 'err':
                char_lower = keyboard.Key.backspace
                controller.press(char_lower)
                controller.release(char_lower)
                print(char_lower)
                if len(text):
                    text.pop()
            elif char_lower == 'esc':
                char_lower = keyboard.Key.esc
                controller.press(char_lower)
                controller.release(char_lower)
                print(char_lower)
            elif char_lower == 'ch':
                char_lower = keyboard.Key.space
                controller.press(char_lower)
                controller.release(char_lower)
                text.append(char_lower)
                print(char_lower)
            elif char_lower == '¿':
                char_lower = keyboard.Key.alt_l
                if LEFT_ALT_DOWN:
                    controller.release(char_lower)
                    LEFT_ALT_DOWN = False
                else: 
                    controller.press(char_lower)
                    LEFT_ALT_DOWN = True
            elif char_lower == 'shift':
                char_lower = keyboard.Key.shift_l
                if LEFT_SHIFT_DOWN:
                    controller.release(char_lower)
                    LEFT_SHIFT_DOWN = False
                else: 
                    controller.press(char_lower)
                    LEFT_SHIFT_DOWN = True
            elif char_lower == '¡':
                char_lower = keyboard.Key.ctrl_l
                if LEFT_CTRL_DOWN:
                    controller.release(char_lower)
                    LEFT_CTRL_DOWN = False
                else: 
                    controller.press(char_lower)
                    LEFT_CTRL_DOWN = True
            elif char_lower == '=' and LEFT_CTRL_DOWN:
                char_lower = keyboard.Key.enter
                controller.press(char_lower)
                controller.release(char_lower)
                LEFT_CTRL_DOWN = False
            else:
                controller.press(char_lower)
                controller.release(char_lower)
                if LEFT_CTRL_DOWN:
                    controller.release(keyboard.Key.ctrl_l)
                    LEFT_CTRL_DOWN = False
                elif LEFT_ALT_DOWN:
                    controller.release(keyboard.Key.alt_l)
                    LEFT_ALT_DOWN = False
                elif LEFT_SHIFT_DOWN:
                    controller.release(keyboard.Key.shift_l)
                    LEFT_SHIFT_DOWN = False
                else:
                    print(char_lower)
                    text.append(char_lower)

    current = []

char_timer = threading.Timer(1.0, end_char) 

def dit_complete():
    global dit_sine
    #print('dit complete')
    #dit_sine.stop()

def dah_complete():
    global sinewave
    #print('dah complete')
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
        dit_timer = threading.Timer(0.11 * speed, dit_complete) 
        current.append('.')
        print(current)
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
        dah_timer = threading.Timer(0.18 * speed, dah_complete) 
        current.append('-')
        dah_timer.start()

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


def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        #exit() #TODO(DAN): quit strategy
        pass


# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
   listener.join()


# TODO(DAN): event loop depleting queue
