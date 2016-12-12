#!/usr/bin/env python
'''Simple proxy'''
import sys
import socket
import threading

class ProxyParams(object):
    '''Params'''
    def __init__(self, proxy_handler,
                 local_host="",
                 remote_host="", local_port=0,
                 remote_port=0, receive_first=False):
        self.local_host = local_host
        self.remote_host = remote_host
        self.local_port = local_port
        self.remote_port = remote_port
        self.receive_first = receive_first
        self.proxy_handler = proxy_handler
    def copy_from(self, target):
        '''Copy the contents of target to self'''
        self.local_host = target.local_host
        self.remote_host = target.remote_host
        self.local_port = target.local_port
        self.remote_port = target.remote_port
        self.receive_first = target.receive_first
        self.proxy_handler = target.proxy_handler
    @staticmethod
    def clone(target):
        '''Create a duplicate of target'''
        result = ProxyParams(target.proxy_handler)
        result.copy_from(target)
        return result

def server_loop(parms):
    '''Simple proxy server loop'''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((parms.local_host, parms.local_port))
    except Exception as err:
        print "[!!] Failed to listen on %s:%d" % (parms.local_host, parms.local_port)
        print
        print "[!!] Check for other listening sockets and correct permissions"
        print
        print "Exception Details:"
        print str(err)
        sys.exit(0)

    print "[*] Listening on %s:%d" % (parms.local_host, parms.local_port)
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        print "[==>] Received connection from %s:%d" % (addr[0], addr[1])

        proxy_thread = threading.Thread(target=parms.proxy_handler,
                                        args=(client_socket, parms))
        proxy_thread.start()
#server_loop(ProxyParams("127.0.0.1", local_port=80))

def usage():
    '''Print usage instructions'''
    print "Usage: ./bhproxy.py [locahost] [localport] [remotehost] [remoteport] [receive_first]"
    print "Example: ./bhproxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
    

def main(handler):
    ''' Main proxy method'''
    if len(sys.argv[1:]) != 5:
        usage()
        sys.exit(0)

    # set up parms
    parms = ProxyParams(handler)

    # set up local params
    parms.local_host = sys.argv[1]
    parms.local_port = int(sys.argv[2])

    # set up remote params
    parms.remote_host = sys.argv[3]
    parms.remote_port = int(sys.argv[4])

    # this tells our proxy to connect and recieve data
    # before sending to the remote host
    parms.receive_first = "True" in sys.argv[5]

    # now spin up the listening socket
    server_loop(parms)



def simple_handler(client_socket, parms):
    '''Simple proxy handler'''
    parms = ProxyParams.clone(parms) # ONLY for intellisense. Comment out when finished coding

    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    remote_socket.connect((parms.remote_host, parms.remote_port))
    # receive data from the remote end first if necessary
    if parms.receive_first:
        remote_buffer = receive_from(remote_socket)
        hex_dump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to our local client, send it
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
    # now lets loop and read from local
        # send to remmote, send to local
    # rinse, repeat
    while True:
        #receive from local host
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print "[==>] Recieved %d bytes from localhost." % len(local_buffer)
            hex_dump(local_buffer)

            # send to our request handler
            local_buffer = request_handler(local_buffer)

            # send off the data to our remote host
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote."

            # recieve back the response
            remote_buffer = receive_from(remote_socket)
            if len(remote_buffer):
                print "[<==] Received %d bytes from remote." % len(remote_buffer)
                hex_dump(remote_buffer)

                # send to our response handler
                remote_buffer = response_handler(remote_buffer)

                # send the response to the local socket
                client_socket.send(remote_buffer)

                print "[<==] Sent to localhost."
            # if no more data on either side, close the connections
                if not len(local_buffer) or not len(remote_buffer):
                    client_socket.close()
                    remote_socket.close()

                    print "[*] No more data. Closing connections."
                    break
def hex_dump(src, length=16):
    '''This is a pretty hex dumper taken directly from the comments here:
    http://code.activestate.com/recipes/142812-hex-dumper
    '''
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        block = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in block])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in block])
        result.append(b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))
    result = b'\n'.join(result)
    print result
    return result

def receive_from(connection, timeout=2):
    '''Recieve data from socket'''
    buffer = ""

    # set a 2 second timeout; depending on the target this may need to be adjusted
    connection.settimeout(timeout)
    try:
        # keep reading into the buffer until there is no more data or we reach out timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data

    except:
        pass
    return buffer

def request_handler(buffer):
    '''Perform packet modifications'''
    return buffer
def response_handler(buffer):
    '''Perform packet modifications'''
    return buffer
main(simple_handler)
