#!/usr/bin/env python
'''content bruter'''

# standard imports
import argparse
import os
import sys
import threading

# other imports
import Queue
import urllib
import urllib2

def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP Web Examples')

    parser.add_argument('url', nargs='?', default='http://testphp.vulnweb.com', help='the target url')
    parser.add_argument('-tc', '--thread_count', default=5, help='number of threads to use')
    parser.add_argument('-w', '--wordlist', default='all.txt', help='file containing the words to search for')
    parser.add_argument('-a', '--user_agent',
                        default='Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0',
                        help='user agent to use')
    parser.add_argument('-e', '--extensions', nargs='*', default=['.jpg', '.gif', '.png', '.css'],
                        help='the file extensions to look for')

    result = parser.parse_args()
    #print result
    return result

def build_threads(thread_count, target, args):
    '''spawn the threads'''
    threads = []
    for i in range(thread_count):
        print 'Spawning Thread: %d' % i
        threads.append(threading.Thread(target=target, args=args))
    def starter():
        for t in threads:
            t.start()
    return starter

def build_queue(directory, filters):
    '''build the queue of paths'''

    # switch to the directory
    if not os.path.isdir(directory):
        os.makedirs(directory)
    os.chdir(directory)

    result = Queue.Queue()
    for r,d,f in os.walk('.'):
        for files in f:
            remote_path = '%s/%s' % (r, files)
            if remote_path.startswith('.'):
                remote_path = remote_path[1:]
            if os.path.splitext(files)[1] not in filters:
                result.put(remote_path)

    return result

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




def dir_bruter(target_url, user_agent, word_queue, extensions=None):
    '''brute force the target'''
    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []
        # check if we are looking at a file or folder

        sformat = '/%s' # assume we are working with a file...
        if '.' not in attempt:
            # ... nope, it's a folder
            sformat = sformat + '/'
        attempt_list.append(sformat % attempt)

        # if we want to brute force extensions
        if extensions:
            for extension in extensions:
                attempt_list.append('/%s%s' % (attempt, extension))

        # iterate over our list of attempts
        for brute in attempt_list:
            url = '%s%s' % (target_url, urllib.quote(brute))

            try:
                headers = {}
                headers['User-Agent'] = user_agent

                request = urllib2.Request(url, headers=headers)

                response = urllib2.urlopen(request)

                if len(response.read()):
                    print '[%d] => %s' % (response.code, url)
            except urllib2.URLError, err:
                if hasattr(err, 'code') and err.code != 404:
                    print '[!!!] [%d] => %s' % (err.code, url)

    
def main():
    '''main'''
    ns = getargs()
    print ns

    threads = ns.thread_count
    target_url = ns.url
    wordlist_file = ns.wordlist
    user_agent = ns.user_agent

    extensions = ns.extensions

    # get the Queue
    queue = build_wordqueue(wordlist_file)

    # construct and start the threads
    starter = build_threads(threads, dir_bruter, (target_url, user_agent, queue, extensions))
    starter()
        
main()