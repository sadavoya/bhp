#!/usr/bin/env python
'''sniffer_ip_header_decode'''

import socket
import os
import sys
import struct
from ctypes import *

WINDOWS = 'nt'
POSIX = 'posix'
 
# our IP header
class IP(Structure):
    '''Header'''
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
        print self.src

        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

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
    # Handle CTRL-C
    except KeyboardInterrupt:
        print "Cleaning up"
        if os.name == WINDOWS:
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print "Disabled promiscuous mode"
main()