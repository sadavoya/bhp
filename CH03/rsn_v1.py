#!/usr/bin/env python
'''sniffer'''

import socket
import os
WINDOWS = 'nt'
POSIX = 'posix'

def main():
    '''sniffer'''
    # host ip to listen on
    host = "192.168.124.128"

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
        port = 65565
        # read in a single packet
        print "Waiting for data on port %d..." % port
        print sniffer.recvfrom(port)
    except:
        pass
    finally:
        print "Cleaning up"
        if os.name == WINDOWS:
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print "Disabled promiscuous mode"
main()
