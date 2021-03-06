#!/usr/bin/env python
'''sniffer_ip_header_decode'''

import socket
import os
import sys
import struct
from ctypes import *

WINDOWS = 'nt'
POSIX = 'posix'
s_ICMP = 'ICMP'
s_TCP = 'TCP'
s_UDP = 'UDP'
PROTOCOL_MAP = {1:s_ICMP, 6:s_TCP, 17:s_UDP}

# our IP header
class IP(Structure):
    '''IP Header'''
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32),
    ]
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer=None):
        # map protocol constants to their names
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        # human readable IP addresses
        #print self.src

        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
        # human readable protocol
        try:
            self.protocol = PROTOCOL_MAP[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):
    '''ICMP Packet'''
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort),
    ]
    def __new__(self, socket_buffer=None):
        '''Create a new ICMP'''
        return self.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer=None):
        '''Initialize ICMP'''
        pass

def main():
    '''sniffer'''
    # host ip to listen on
    host = sys.argv[1]

    os_name = os.name.lower()

    protocols = {WINDOWS    : socket.IPPROTO_IP,
                 POSIX    : socket.IPPROTO_ICMP}
    try:
        socket_protocol = protocols[os_name]
    except:
        print "No match for os.name. Add a protocol to [protocols] variable for %s" % os_name

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    print "Created sniffer"

    sniffer.bind((host, 0))
    print "Bound to host %s" % host

    # we want the ip headers included in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    print "Headers enabled"

    # if we are using windows we want to send and IOCTL to set up promiscuous mode
    if os.name == WINDOWS:
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        print "Enabled promiscuous mode"

    try:
        while True:
            # read in a packet
            raw_buffer = sniffer.recvfrom(65565)[0]
            # create an ip header from the first 20 bytes of the buffer
            ip_header = IP(raw_buffer)
            # print out the protocol that was detected and the hosts
            print "Protocol: %s %s -> %s" % (
                ip_header.protocol,
                ip_header.src_address,
                ip_header.dst_address)
            # if it's ICMP we want it'
            if ip_header.protocol == s_ICMP:
                # calculate where our ICMP packet starts
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + sizeof(ICMP)]
                # create our ICMP Structure
                icmp_header = ICMP(buf)
                print 'ICMP -> Type: %d Code: %d' % (
                    icmp_header.type,
                    icmp_header.code
                )
            
    # Handle CTRL-C
    except KeyboardInterrupt:
        print
        print "Cleaning up..."
        if os.name == WINDOWS:
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print "Disabled promiscuous mode"
        print "Done."
main()