#!/usr/bin/env python
'''web examples'''

import urllib2
import sys
import argparse


def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP Web Examples')

    parser.add_argument('url', help='The URL to get')
    parser.add_argument('-t', '--target', help='The target of the attack')
    parser.add_argument('-c', '--count', default=1000, help='number of packets to observe')
    parser.add_argument('-i', '--interface', default='eth0', help='interface to use')

    result = parser.parse_args()
    #print result
    return result

def ex1(url):
    '''simple read'''
    body = urllib2.urlopen(url)
    print body.read()
def ex2(url):
    headers = {}
    headers['User-Agent'] = 'Googlebot'

    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)

    print response.read()
    response.close()

def main():
    '''main'''
    ns = getargs()
    url = ns.url

    print 'Reading: "%s"' % (url)

    #ex1(url)
    ex2(url)

main()
