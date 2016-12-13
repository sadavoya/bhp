#!/usr/bin/env python
'''mail sniffer'''

from scapy.all import *


# packet callback
def callback(packet):
    '''Handle the packet'''
    print packet.show()

def main():
    '''main function'''
    sniff(prn=callback, count=1)

main()
