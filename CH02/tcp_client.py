'''Some simple clients'''
import socket

def tcp_client_test(target_host, target_port, text):
    '''A simple tcp client
    '''
    # create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect the client
    client.connect((target_host, target_port))
    # send some text
    client.send(text)
    # display response
    response = client.recv(4096)
    print response

def udp_client_test(target_host, target_port):
    ''' UDP client
    '''
    # create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # send some text
    client.sendto("AAABBBCCC", (target_host, target_port))
    # display response
    data, addr = client.recvfrom(4096)
    print data


#client_test(target_host = "www.google.com", target_port = 80, text="GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")
#udp_client_test(target_host="127.0.0.1", target_port=80)
tcp_client_test("0.0.0.0", 9999, "ABCDEF")
