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

# kb = Keyboard(usb_hid.devices)
usbmode = False
CAN_CHORD = True

filename = "/notes.txt"
word_buf = ''
key_buf = ''
time_buf = ''
map_char = ''
last_detected_time = None
usbmode = False

# Display setup
display = board.DISPLAY
main_group = displayio.Group()
display.root_group = main_group

# String label
word_label = label.Label(font=terminalio.FONT)
word_label.text = word_buf
word_label.scale = 3
word_label.anchor_point = (1, 0)
word_label.anchored_position = (display.width, 0)

# Last key label
mcode_label = label.Label(font=terminalio.FONT)
mcode_label.text = key_buf
mcode_label.scale = 3
mcode_label.anchor_point = (1, 1)
mcode_label.anchored_position = (display.width, display.height)

# Timer label
time_label = label.Label(font=terminalio.FONT)
time_label.text = time_buf
time_label.scale = 3
time_label.anchor_point = (0, 1)
time_label.anchored_position = (0, display.height)

# Add labels to display
main_group.append(word_label)
main_group.append(time_label)

DEBOUNCE_DURATION = 30_000_000

CONFIG_INPUT_PINS = [
    mc.pin.GPIO17,  # Pinky
    mc.pin.GPIO16,  # Ring
    mc.pin.GPIO15,  # Middle
    mc.pin.GPIO14,  # Index
    mc.pin.GPIO5,   # Left thumb
    mc.pin.GPIO6,   # Middle thumb
    mc.pin.GPIO9,   # Right thumb
]

KEYS = []

# For scrolling notes.txt
line_index = 0
notes = []

def load_notes():
    try:
        with open(filename, "r") as file:
            return file.readlines()
    except OSError:
        return ["No notes available."]

notes = load_notes()

def wrap_text(text, max_chars_per_line):
    wrapped = []
    while len(text) > 0:
        wrapped.append(text[:max_chars_per_line])
        text = text[max_chars_per_line:]
    return wrapped

def update_display_scroll():
    global word_buf
    global line_index
    global word_label

    max_chars_per_line = 13  # Adjust if needed

    if line_index >= len(notes):
        line_index = 0
    elif line_index < 0:
        line_index = len(notes) - 1

    line_text = f"{line_index + 1}: {notes[line_index].strip()}"

    wrapped_lines = wrap_text(line_text, max_chars_per_line)

    word_buf = "\n".join(wrapped_lines[:3])

    word_label.scale = 3
    word_label.text = word_buf

hid_keycode_to_char = {
    4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g',
    11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n',
    18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't',
    24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z',
    30: '1', 31: '2', 32: '3', 33: '4', 34: '5',
    35: '6', 36: '7', 37: '8', 38: '9', 39: '0',
    40: '\n', 41: 'esc', 42: 'backspace', 43: 'tab', 44: ' ',
    45: '-', 46: '=', 47: '[', 48: ']', 49: '\\',
    51: ';', 52: "'", 53: '`', 54: ',', 55: '.', 56: '/',
    58: 'F1', 59: 'F2', 60: 'F3', 61: 'F4', 62: 'F5', 63: 'F6',
    64: 'F7', 65: 'F8', 66: 'F9', 67: 'F10', 68: 'F11', 69: 'F12',
    70: 'print_screen', 71: 'scroll_lock', 72: 'pause', 73: 'insert',
    74: 'home', 75: 'page_up', 76: 'delete', 77: 'end', 78: 'page_down',
    79: 'right_arrow', 80: 'left_arrow', 81: 'down_arrow', 82: 'up_arrow',
}

def get_char_from_hid_keycode(keycode):
    return hid_keycode_to_char.get(keycode, "Unknown")

# (CHORD_TABLE omitted for brevity—include your full mapping)
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
    (True, False, True, True, False, False, True): Keycode.RIGHT_ARROW,
    (True, True, False, True, False, False, True): Keycode.LEFT_ARROW,
    (True, False, False, True, False, False, True): Keycode.UP_ARROW,
    (True, True, True, True, False, False, True): Keycode.DOWN_ARROW,
    (True, True, True, False, False, False, True): Keycode.ESCAPE,
    (True, False, True, True, False, False, False): Keycode.HOME,
    (True, True, False, True, False, False, False): Keycode.END,
    (True, True, False, True, False, True, False): Keycode.WINDOWS,
    (True, False, True, True, False, True, False): Keycode.DELETE,
    (True, False, True, True, False, False, True): Keycode.F1,
    (True, False, True, True, False, True, False): Keycode.F2,
    (True, False, True, True, True, False, False): Keycode.F3,
    (True, True, False, True, False, True, False): Keycode.F4,
    (True, False, True, True, False, False, False): Keycode.BACKSPACE,
    (True, True, False, True, False, False, False): Keycode.SPACE,
}


current_modifiers = 0
sticky_modifiers = 0
last_modifier = 0
start_time = time.monotonic_ns()
last_modifier_time = time.monotonic_ns()

def prime_chord():
    global CAN_CHORD
    CAN_CHORD = True

def send_chord():
    global CAN_CHORD
    global last_modifier, last_modifier_time
    global current_modifiers, sticky_modifiers
    global word_buf, key_buf, map_char
    global last_detected_time, time_buf
    global usbmode
    global line_index

    if not CAN_CHORD:
        return

    current_key_comb = tuple(not key.lastvalue for key in KEYS)

    try:
        key_to_send = CHORD_TABLE[current_key_comb]
        map_char = key_to_send
    except KeyError:
        return

    CAN_CHORD = False

    # Handle scrolling first
    if map_char == Keycode.UP_ARROW:
        line_index -= 1
        update_display_scroll()
        return
    elif map_char == Keycode.DOWN_ARROW:
        line_index += 1
        update_display_scroll()
        return

    # Default processing
    if map_char < 57:
        key_buf = get_char_from_hid_keycode(map_char)

    # ---- Key actions ----
    if map_char == Keycode.BACKSPACE:  # 42
        if len(word_buf) > 0:
            word_buf = word_buf[:-1]
        key_buf = ''

    elif map_char == 58:  # start timer
        last_detected_time = time.monotonic()
        key_buf = ''

    elif map_char == 59:  # save file
        storage.remount("/", False)
        with open(filename, "a") as file:
            file.write(f"{word_buf},{time_buf}\n")
        word_buf = ''
        key_buf = ''

    elif map_char == 60:  # clear
        last_detected_time = None
        word_buf = ''
        key_buf = ''
        time_buf = ''

    elif map_char == 61:  # USB mode
        kb = Keyboard(usb_hid.devices)
        last_detected_time = None
        usbmode = True
        word_buf = ''
        key_buf = ''
        time_buf = ''

    else:
        # printable / everything else
        key_buf = get_char_from_hid_keycode(map_char)
        word_buf += key_buf

    if last_detected_time is not None and last_detected_time > 0:
        elapsed_time = int(time.monotonic() - last_detected_time)
        time_buf = f"{elapsed_time}"
        time_label.text = time_buf

    word_label.scale = 3
    word_label.text = str(word_buf)
    time_label.text = str(time_buf)

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
        if self.value:
            send_chord()
        else:
            prime_chord()

for cpin in CONFIG_INPUT_PINS:
    KEYS.append(Key(cpin))

led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT

while True:
    led.value = KEYS[0].pin.value
    for key in KEYS:
        key.update()
