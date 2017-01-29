import win32gui
import win32ui
import win32con
import win32api

bitmapfile = 'c:\\WINDOWS\\Temp\\screenshot.bmp'

def run_f_for_all_xs(func, targets):
    '''map func on targets'''
    results = []
    for target in targets:
        try:
            pargs = iter(target)
        except:
            pargs = iter((target,))
        results.append(func(*pargs))
    return tuple(results)

def try_close_handle(action, name):
    '''try to perform the specified action'''
    try:
        action()
    except Exception as err:
        print 'Exception closing %s: %s' % (name, str(err))

def main():
    '''main function'''
    #grab a handle to the desktop
    hdesktop = win32gui.GetDesktopWindow()
    #determine the size of all monitors in pixels
    # pylint: disable=unbalanced-tuple-unpacking
    (width, height, left, top) = run_f_for_all_xs(win32api.GetSystemMetrics, [
        (win32con.SM_CXVIRTUALSCREEN),
        (win32con.SM_CYVIRTUALSCREEN),
        (win32con.SM_XVIRTUALSCREEN),
        (win32con.SM_YVIRTUALSCREEN)
    ])
    # width, height, left, top = (
    #     win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),
    #     win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN),
    #     win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN),
    #     win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    # )
    # create a device context
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    try:
        # create a memory based device context
        mem_dc = img_dc.CreateCompatibleDC()
        # create a bitmap object
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        # copy the screen into memory device context
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
        # save the bitmap to a file
        screenshot.SaveBitmapFile(mem_dc, bitmapfile)
    except Exception as err:
        print "Exception: %s" % str(err)
    finally:
        # free our objects
        run_f_for_all_xs(try_close_handle, [
            (lambda: mem_dc.DeleteDC(), 'mem_dc.DeleteDC()'),
            (lambda: win32gui.DeleteObject(screenshot.GetHandle()),
             'win32gui.DeleteObject(screenshot.GetHandle())')
        ])
main()
