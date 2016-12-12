'''TCP Server test
'''


import socket
import threading


def tcp_server_test(handler, bind_ip, bind_port):
    ''' TCP Server
    '''
    # create socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)

    while True:
        client, addr = server.accept()
        print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])
        client_handler = threading.Thread(target=handler, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    ''' A simple client handler
    '''
    request = client_socket.recv(1024)
    print "[*] Received: %s" % request
    client_socket.send("ACK!")
    client_socket.close()

tcp_server_test(handle_client, "0.0.0.0", 9999)
