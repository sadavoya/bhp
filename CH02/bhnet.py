#!/usr/bin/env python
''' A simple netcat replacement'''

import sys
import socket
import getopt
import threading
import subprocess


class MyVars:
    ''' Globals
    '''
    def __init__(self, client_handler):
        self.listen = False
        self.command = False
        self.execute = ""
        self.target = ""
        self.upload_destination = ""
        self.port = 0
        self.client_handler = client_handler
    def init_from(self, target):
        '''Initialize to the same state as target'''
        self.listen = target.listen
        self.command = target.command
        self.execute = target.execute
        self.target = target.target
        self.upload_destination = target.upload_destination
        self.port = target.port
        self.client_handler = target.client_handler
    @staticmethod
    def clone(target):
        '''Copy target to a new MyVars object'''
        result = MyVars(target.client_handler)
        result.init_from(target)
        return result


def usage():
    ''' Display how to use the program'''
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen               - listen on [Host]:[Port] for incoming connections"
    print "-e --execute=file_to_run  - execute [file_to_run] upon receiving a connection"
    print "-c --command              - initialize a command shell"
    print ("-u --upload=destination   - upon receiving a connection, " +
           " upload a file and write to [destination]")
    print "Examples:"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

#usage()

def handle_client(myvars, client_socket):
    '''Simple client handler'''
    myvars = MyVars.clone(myvars)

    # check for upload_destination
    if len(myvars.upload_destination):
        #Read in all the bytes and write to the destination
        file_buffer = ""
        # keep reading date until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(myvars.upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            # Acknowledge that we wrote the file successfully
            client_socket.send("Successfully saved file to %s\r\n" % myvars.upload_destination)
        except:
            client_socket.send("Failed to save the file %s\r\n" % myvars.upload_destination)

    # check for command executions
    if len(myvars.execute):
        output = run_command(myvars.execute)
        client_socket.send(output)
    
    # check for command shell
    if myvars.command:
        while True:
            # show a prompt
            client_socket.send("<BHP:#>")
            #receive until we get a line feed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            # run the command...
            response = run_command(cmd_buffer)
            # ...and send back the output
            client_socket.send(response)

            
        
def main():
    '''The main function'''
    myvars = MyVars(handle_client)

    if not len(sys.argv[1:]):
        usage()


    # process the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target",
                                    "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-l", "--listen"):
            myvars.listen = True
        elif opt in ("-e", "--execute"):
            myvars.execute = arg
        elif opt in ("-c", "--commandshell", "--command"):
            myvars.command = True
        elif opt in ("-u", "--upload"):
            myvars.upload_destination = arg
        elif opt in ("-t", "--target"):
            myvars.target = arg
        elif opt in ("-p", "--port"):
            myvars.port = int(arg)
        else:
            assert False, "Unhandled option"
    # are we going to listen or just send data from stdin?
    if not myvars.listen and len(myvars.target) and myvars.port > 0:
        # read in the buffer from the command line
        # this will block, so send CTRL-D if not sending
        # input to stdin
        mybuffer = sys.stdin.read()
        # send data off
        client_sender(myvars, mybuffer)
    # we are goind to listen and potentially
    # upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if myvars.listen:
        server_loop(myvars)

def client_sender(myvars, mybuffer):
    '''Send as client
    '''
    myvars = MyVars.clone(myvars)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # try to connect to our target host
        client.connect((myvars.target, myvars.port))
        if len(mybuffer):
            client.send(mybuffer)

        while True:
            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break

            print response,

            # Wait for more input
            mybuffer = raw_input("")
            mybuffer += "\n"

            # send it off
            client.send(mybuffer)

    except Exception as err:
        print "[*] Exception! Exiting."
        # Tear down the connection
        client.close()
        print "Exception Details:"
        print str(err)


def server_loop(myvars):
    '''Listen as server
    '''
    myvars = MyVars.clone(myvars)
    # If no target defined, listen on all interfaces
    if not len(myvars.target):
        myvars.target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((myvars.target, myvars.port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])

        #spin off a thread to handle the client
        client_thread = threading.Thread(target=myvars.client_handler,
                                         args=(myvars, client_socket,))
        client_thread.start()

def run_command(command):
    '''Execute the specified [command]'''
    #trim the newline
    command = command.rstrip()

    #run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output



main()
