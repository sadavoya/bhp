'''detect if we are running inside a sandbox'''

import ctypes
import random
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

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
                sensors['mouse_clicks'] += 1
                return time.time()
            elif i > 32 and i < 127:
                sensors['keystrokes'] += 1
    return None

def main():
    '''main function'''
    #test_get_last_input()

    sensors = init_sensor_dict([
        'keystrokes',
        'mouse_clicks',
        'double_clicks'
    ])
    get_key_press(sensors)
main()
