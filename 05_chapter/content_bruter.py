#!/usr/bin/env python
'''web app mapper'''

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
    parser.add_argument('-tc', '--thread_count', default=50, help='number of threads to use')
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
    for i in range(thread_count):
        print 'Spawning Thread: %d' % i
        t = threading.Thread(target=target, args=args)
        t.start()

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

def main():
    '''main'''
    ns = getargs()
    print ns

    threads = ns.thread_count
    target = ns.url
    directory = ns.output_directory
    filters = ns.filters

    # get the Queue
    queue = build_path_queue(directory, filters)

    # construct and start the threads
    build_threads(threads, (queue, target))

        
main()