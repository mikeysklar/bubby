import board
import displayio
import terminalio
import digitalio as dio
import microcontroller as mc
import time
import supervisor
import usb_hid
import storage
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_display_text import label

#kb = Keyboard(usb_hid.devices)

# files / chording buffers
filename = "/notes.txt"
word_buf = ''
key_buf = ''
time_buf = ''
map_char = ''
last_detected_time = None  # Variable to store the time when map_char == '40' is detected
usbmode = False

# built-in display
display = board.DISPLAY

# Make the display context
main_group = displayio.Group()
display.root_group = main_group

# string of keys entered
word_label = label.Label(font=terminalio.FONT)
word_label.text = word_buf
word_label.scale = 6
word_label.anchor_point = (1, 0)
word_label.anchored_position = (display.width, 0)
                                                                               # create the label
# last key entered
mcode_label = label.Label(font=terminalio.FONT)
mcode_label.text = key_buf
mcode_label.scale = 6
mcode_label.anchor_point = (1, 1)
mcode_label.anchored_position = (display.width, display.height)                

# timer label
time_label = label.Label(font=terminalio.FONT)
time_label.text = time_buf
time_label.scale = 6
time_label.anchor_point = (0, 1)
time_label.anchored_position = (0, display.height)                

# add label to group that is showing on display
main_group.append(word_label)
main_group.append(mcode_label)
main_group.append(time_label)

DEBOUNCE_DURATION = 30_000_000

CONFIG_INPUT_PINS = [
    mc.pin.GPIO17, # Pinky finger
    mc.pin.GPIO16, # Ring finger
    mc.pin.GPIO15, # Middle finger
    mc.pin.GPIO14, # Index finger
    mc.pin.GPIO5, # Leftmost thumb 
    mc.pin.GPIO6, # Middle thumb 
    mc.pin.GPIO9, # Rightmost thumb 
]

KEYS = []

# HID Keycode to character mapping for a comprehensive set of keys
hid_keycode_to_char = {
    # Alphabets
    4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g',
    11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n',
    18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't',
    24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z',
    # Digits
    30: '1', 31: '2', 32: '3', 33: '4', 34: '5',
    35: '6', 36: '7', 37: '8', 38: '9', 39: '0',
    # Commonly used punctuation/symbols
    40: '\n', 41: 'esc', 42: 'backspace', 43: 'tab', 44: ' ',
    45: '-', 46: '=', 47: '[', 48: ']', 49: '\\',  # \ is escape char in strings
    51: ';', 52: "'", 53: '`', 54: ',', 55: '.', 56: '/',
    # Function Keys
    58: 'F1', 59: 'F2', 60: 'F3', 61: 'F4', 62: 'F5',
    63: 'F6', 64: 'F7', 65: 'F8', 66: 'F9', 67: 'F10', 68: 'F11', 69: 'F12',
    # Control Keys
    70: 'print_screen', 71: 'scroll_lock', 72: 'pause', 73: 'insert', 
    74: 'home', 75: 'page_up', 76: 'delete', 77: 'end', 78: 'page_down',
    79: 'right_arrow', 80: 'left_arrow', 81: 'down_arrow', 82: 'up_arrow',
    83: 'num_lock', 84: 'keypad /', 85: 'keypad *', 86: 'keypad -', 
    87: 'keypad +', 88: 'keypad enter', 89: 'keypad 1', 90: 'keypad 2',
    91: 'keypad 3', 92: 'keypad 4', 93: 'keypad 5', 94: 'keypad 6',
    95: 'keypad 7', 96: 'keypad 8', 97: 'keypad 9', 98: 'keypad 0',
    99: 'keypad .',
    # Modifier Keys
    224: 'l_ctrl', 225: 'l_shift', 226: 'l_alt', 227: 'l_gui',
    228: 'r_ctrl', 229: 'r_shift', 230: 'r_alt', 231: 'r_gui',
}

CAN_CHORD = False
CHORD_TABLE = {
    (False, False, False, True, False, False, False): Keycode.E,
    (False, False, True, False, False, False, False): Keycode.I,
    (False, True, False, False, False, False, False): Keycode.A,
    (True, False, False, False, False, False, False): Keycode.S,
    (False, False, True, True, False, False, False): Keycode.R,
    (False, True, True, False, False, False, False): Keycode.N,
    (True, True, False, False, False, False, False): Keycode.T,
    (False, True, False, True, False, False, False): Keycode.O,
    (True, False, True, False, False, False, False): Keycode.L,
    (True, False, False, True, False, False, False): Keycode.C,
    (False, True, True, True, False, False, False): Keycode.D,
    (True, True, True, False, False, False, False): Keycode.P,
    (True, True, True, True, False, False, False): Keycode.U,
    (False, False, False, True, False, True, False): Keycode.M,
    (False, False, True, False, False, True, False): Keycode.G,
    (False, True, False, False, False, True, False): Keycode.H,
    (True, False, False, False, False, True, False): Keycode.B,
    (False, False, True, True, False, True, False): Keycode.Y,
    (False, True, True, False, False, True, False): Keycode.F,
    (True, True, False, False, False, True, False): Keycode.V,
    (False, True, False, True, False, True, False): Keycode.W,
    (True, False, True, False, False, True, False): Keycode.K,
    (True, False, False, True, False, True, False): Keycode.X,
    (False, True, True, True, False, True, False): Keycode.J,
    (True, True, True, False, False, True, False): Keycode.Z,
    (True, True, True, True, False, True, False): Keycode.Q,
    (False, False, False, True, True, False, False): Keycode.SPACE,
    (False, False, True, False, True, False, False): Keycode.TAB,
    (False, False, False, False, False, True, False): Keycode.SHIFT,
    (False, False, False, False, True, False, False): Keycode.ALT,
    (False, False, False, False, False, False, True): Keycode.CONTROL,
    (False, False, True, True, True, False, False): Keycode.ENTER,
    (False, False, False, True, False, False, True): Keycode.ONE,
    (False, False, True, False, False, False, True): Keycode.TWO,
    (False, True, False, False, False, False, True): Keycode.THREE,
    (True, False, False, False, False, False, True): Keycode.FOUR,
    (False, False, True, True, False, False, True): Keycode.FIVE,
    (False, True, True, False, False, False, True): Keycode.SIX,
    (True, True, False, False, False, False, True): Keycode.SEVEN,
    (False, True, False, True, False, False, True): Keycode.EIGHT,
    (True, False, True, False, False, False, True): Keycode.NINE,
    (False, True, True, True, False, False, True): Keycode.ZERO,
    (False, True, False, False, True, False, False): Keycode.PERIOD,
    (False, True, False, True, True, False, False): Keycode.COMMA,
    (True, True, False, False, True, False, False): Keycode.FORWARD_SLASH,
    (True, True, True, True, True, False, False): Keycode.GRAVE_ACCENT,
    (True, False, False, False, True, False, False): Keycode.MINUS,
    (False, True, True, True, True, False, False): Keycode.EQUALS,
    (True, False, True, False, True, False, False): Keycode.LEFT_BRACKET,
    (True, False, False, True, True, False, False): Keycode.RIGHT_BRACKET,
    (True, True, True, False, True, False, False): Keycode.BACKSLASH,
    (True, True, False, True, True, False, False): Keycode.SEMICOLON,
    (True, False, True, True, True, False, False): Keycode.QUOTE,
    (False, True, True, False, True, False, False): Keycode.BACKSPACE,
    (True, False, True, True, False, False, True): Keycode.RIGHT_ARROW,
    (True, True, False, True, False, False, True): Keycode.LEFT_ARROW,
    (True, False, False, True, False, False, True): Keycode.UP_ARROW,
    (True, True, True, True, False, False, True): Keycode.DOWN_ARROW,
    (True, True, True, False, False, False, True): Keycode.ESCAPE,
    (True, False, True, True, False, False, False): Keycode.HOME,
    (True, True, False, True, False, False, False): Keycode.END,
    (True, True, False, True, False, True, False): Keycode.WINDOWS,
    (True, False, True, True, False, True, False): Keycode.DELETE,
    (True, True, False, True, False, False, False): Keycode.F1,
    (True, False, True, True, False, False, False): Keycode.F2,
    (True, False, True, True, False, True, False): Keycode.F3,
    (True, True, False, True, False, True, False): Keycode.F4,
}

current_modifiers = 0
sticky_modifiers = 0
last_modifier = 0
start_time = time.monotonic_ns() # Reference point
last_modifier_time = time.monotonic_ns()

def get_char_from_hid_keycode(keycode):
    return hid_keycode_to_char.get(keycode, "Unknown keycode")

def send_kb_report():
    kb.report_modifier[0] = current_modifiers
    kb._keyboard_device.send_report(kb.report)

def prime_chord():
    global CAN_CHORD

    CAN_CHORD = True

def send_chord():
    global CAN_CHORD
    global last_modifier
    global last_modifier_time
    global current_modifiers
    global sticky_modifiers
    global word_buf
    global last_detected_time
    global time_buf
    global kb
    global usbmode

    if not CAN_CHORD:
        # We need this, otherwise keyups for one chord would trigger multiple chords
        return

    # CHORD_TABLE uses True if the key was pressed, while the actual pins
    # say True if the key is not pressed. So we invert it.
    current_key_comb = tuple(not key.lastvalue for key in KEYS)

    try:
        # We can index dicts with immutable values such as tuples
        key_to_send = CHORD_TABLE[current_key_comb]
        print("current_key_comb", current_key_comb)
    except KeyError:
        # No chord found
        # Don't reset CAN_CHORD
        print("No chord found:", current_key_comb)
        return

    CAN_CHORD = False

    print("Sending text:", key_to_send)

    # update display
    map_char = CHORD_TABLE[(current_key_comb)]

    # limit to basic characters + function keys
    if map_char < 57:
        key_buf = get_char_from_hid_keycode(map_char)

    #
    # backspace :: G-23
    #
    # save      :: 124  clear   :: G-124
    # timer     :: 134  USB       :: G-134
    #
    if map_char == 42:                # backspace
        if len(word_buf) > 0:
            word_buf = word_buf[:-1]    # Remove last character from string
            key_buf = ''                # Empty single char

    elif map_char == 58:                # timer start (stole F1 keycode)
        last_detected_time = time.monotonic()  # Capture the current time
        key_buf = ''                    # Empty single char

    elif map_char == 59:                  # save file (stole F2 keycode)
        storage.remount("/", False)
        with open(filename, "a") as file:
            file.write(f"{word_buf},{time_buf}\n")
        word_buf = ''
        key_buf = ''

    elif map_char == 60:                # clear no timer (stole F3 keycode)
        last_detected_time = None       # Capture the current time
        word_buf = ''
        key_buf = ''
        time_buf = ''

    elif map_char == 61:                # USB mode(stole F4 keycode)
        kb = Keyboard(usb_hid.devices)
        last_detected_time = None
        usbmode = True
        word_buf = ''
        key_buf = ''
        time_buf = ''

    # Timer update
    if last_detected_time is not None and last_detected_time > 0:
        elapsed_time = int(time.monotonic() - last_detected_time)
        time_buf = f"{elapsed_time}" # Update display with elapsed time
        time_label.text = time_buf

    # send to display
    word_buf += key_buf
    word_label.text = str(word_buf)
    mcode_label.text = str(key_buf)
    time_label.text = str(time_buf)

    modifier = Keycode.modifier_bit(key_to_send)

    if modifier:
        if modifier & sticky_modifiers:
            # Was sticky, turn it off
            sticky_modifiers &= ~modifier
            current_modifiers &= ~modifier

            # Tell the os about the modifier key update (stuff for shift+mouse scroll)
#            send_kb_report()

            print("Unsticked modifier", modifier)
            return

        # If double tap - two taps of the same key within 500ms
        if modifier == last_modifier and time.monotonic_ns() - last_modifier_time < 5e8:
            sticky_modifiers |= modifier
            current_modifiers |= modifier

#            send_kb_report()

            print("Stickied modifier", modifier)
        else:
            # Toggle the modifier bit (in internal state - reference https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/main/adafruit_hid/keyboard.py)
            current_modifiers ^= modifier
#            send_kb_report()

            print("Toggled modifier", modifier, "to", current_modifiers & modifier)

            # Tracking for double tap detection
            last_modifier = modifier
            last_modifier_time = time.monotonic_ns()
    else: 
        if usbmode:
            kb.report_modifier[0] = current_modifiers
            kb.press(key_to_send)
            kb.release(key_to_send)

        current_modifiers = sticky_modifiers # Remove non-sticky modifier keys

        # Tell the os about the released modifier keys
#        send_kb_report()

        # And since this wasn't a modifier, reset the double tap timer
        last_modifier_time = start_time

class Key:
    def __init__(self, cpin):
        self.cpin = cpin

        pin = dio.DigitalInOut(cpin)
        pin.direction = dio.Direction.INPUT
        pin.pull = dio.Pull.UP

        self.pin = pin
        self.lastvalue = pin.value
        self.value = self.lastvalue
        self.lastchange = time.monotonic_ns()

    def update(self):
        self.value = self.pin.value
        if self.value != self.lastvalue:
            tnow = time.monotonic_ns()
            if tnow < self.lastchange + DEBOUNCE_DURATION:
                return False

            self.lastchange = tnow

            self.onstatechange()
            self.lastvalue = self.value

            return True

        return False

    def onstatechange(self):
        print("Change in state detected on pin", self.cpin, "to", "on" if self.value else "off", "(last value was", "on" if self.lastvalue else "off", ")")

        if self.value:
            # Keyup (nonpressed = high)
            # Look for a chord match and send it
            send_chord()
        else:
            # Keydown
            # Allow a chord to be sent
            prime_chord()

for cpin in CONFIG_INPUT_PINS:
    KEYS.append(Key(cpin))

led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT

finished = False


while not finished:
    led.value = KEYS[0].pin.value
    for key in KEYS:
        key.update()
