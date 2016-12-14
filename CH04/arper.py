#!/usr/bin/env python
'''mail sniffer'''

import sys
import argparse


def main():
    '''main'''


    # process the command line
    parser = argparse.ArgumentParser(description='BHP ARPer')
    parser.add_argument('gateway', help='The gateway to spoof')
    parser.add_argument('target', help='The target of the attack')
    parser.add_argument('-c', '--count', default=1000)

    print parser.parse_args()

main()