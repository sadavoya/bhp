'''detect if we are running inside a sandbox'''

import ctypes
import random
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

KEYSTROKES, MOUSE_CLICKS, DOUBLE_CLICKS = 'keystrokes', 'mouse_clicks', 'double_clicks'
KEYSTROKE_MIN, KEYSTROKE_MAX = 10, 25
MOUSE_CLICK_MIN, MOUSE_CLICK_MAX = 5, 25
DOUBLE_CLICK_MAX = 10
DOUBLE_CLICK_THRESHOLD = 0.250 # in seconds
DOUBLE_CLICK_BAILOUT_TIME = DOUBLE_CLICK_MAX * DOUBLE_CLICK_THRESHOLD
MAX_INPUT_THRESHOLD = 30000 # in milliseconds

def init_sensor_dict(names, init=0, target=None):
    '''create or update target with names, all set to init'''
    if target is None:
        target = {}
    for name in names:
        target[name] = init
    return target

class LASTINPUTINFO(ctypes.Structure):
    '''last input info'''
    _fields_ = [('cbSize', ctypes.c_uint),
                ('dwTime', ctypes.c_ulong)
               ]
def get_last_input():
    '''get last input'''
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    # get last input registered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))
    # now determine how long the machine has been running
    run_time = kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime

    print '[*] It has been %d milliseconds since the last input event' % elapsed
    return elapsed

def test_get_last_input():
    '''just a test'''
    for i in range(30):
        get_last_input()
        time.sleep(1)


def get_key_press(sensors):
    '''get key press without pyhook'''
    for i in range(0, 0xff):
        if user32.GetAsyncKeyState(i) == -32767:
            #0x1 is the keycode for a left mouse-click
            if i == 0x1:
                sensors[MOUSE_CLICKS] += 1
                return time.time()
            elif i > 32 and i < 127:
                sensors[KEYSTROKES] += 1
    return None


def detect_sandbox(sensors):
    '''detect a sandbox'''
    max_keystrokes = random.randint(KEYSTROKE_MIN, KEYSTROKE_MAX)
    max_mouse_clicks = random.randint(MOUSE_CLICK_MIN, MOUSE_CLICK_MAX)
    first_double_click = None
    average_mouse_time = 0
    previous_timestamp = None
    detection_complete = False

    last_input = get_last_input()
    # if we hit our threshold, bailout
    if last_input >= MAX_INPUT_THRESHOLD:
        sys.exit(0)
    while not detection_complete:
        key_press_time = get_key_press(sensors)
        if key_press_time is not None and previous_timestamp is not None:
            # calculate the time between double_clicks
            elapsed = key_press_time - previous_timestamp
            #print '[*] time between is %d' % elapsed
            if elapsed <= DOUBLE_CLICK_THRESHOLD:
                sensors[DOUBLE_CLICKS] += 1
                if first_double_click is None:
                    # grab the time stamp of the first double-click
                    first_double_click = time.time()
                else:
                    if sensors[DOUBLE_CLICKS] == DOUBLE_CLICK_MAX:
                        timediff = key_press_time - first_double_click
                        if timediff <= DOUBLE_CLICK_BAILOUT_TIME:
                            sys.exit(0)
            # we are happy there's enough user input
            enough_keystrokes = sensors[KEYSTROKES] >= max_keystrokes
            enough_double_clicks = sensors[DOUBLE_CLICKS] >= DOUBLE_CLICK_MAX
            enough_mouse_clicks = sensors[MOUSE_CLICKS] >= max_mouse_clicks
            if  enough_keystrokes and enough_double_clicks and enough_mouse_clicks:
                return
            previous_timestamp = key_press_time
        elif key_press_time is not None:
            previous_timestamp = key_press_time
def main():
    '''main function'''
    #test_get_last_input()

    sensors = init_sensor_dict([
        KEYSTROKES,
        MOUSE_CLICKS,
        DOUBLE_CLICKS
    ])
    #Sensor = namedtuple(KEYSTROKES, MOUSE_CLICKS, DOUBLE_CLICKS)
    #sensors = Sensor(0, 0, 0) 
    detect_sandbox(sensors)
    print 'We are ok!'

main()
