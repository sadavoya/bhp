#!/usr/bin/env python
'''web app mapper'''

# standard imports
import argparse
import os
import sys
import threading

# other imports
import Queue
import urllib2

def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP Web Examples')

    parser.add_argument('url', nargs='?', default='http://www.blackhatpython.com', help='the target url')
    parser.add_argument('-tc', '--thread_count', default=10, help='number of threads to use')
    parser.add_argument('-d', '--output_directory', default='./web_app_mapper_results',
                        help='the folder to store results in')
    parser.add_argument('-f', '--filters', nargs='*', default=['.jpg', '.gif', '.png', '.css'],
                        help='the filters to use')

    result = parser.parse_args()
    #print result
    return result

def build_path_queue(directory, filters):
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

def test_remote(web_paths, target):
    '''check the queue to see if the path exists on the remote site'''
    return
    while not web_paths.empty():
        path = web_paths.get()
        url = '%s%s' % (target, path)

        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            print '[%d]  => %s' % (response.code, path)
            response.close()
        except urllib2.HTTPError as err:
            # print 'Failed %s' % error.code
            pass
def build_threads(thread_count, queue, url):
    '''spawn the threads'''
    for i in range(thread_count):
        print 'Spawning Thread: %d' % i
        t = threading.Thread(target=test_remote, args=(queue, url))
        t.start()

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
    build_threads(threads, queue, target)

        
main()