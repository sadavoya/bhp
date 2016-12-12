#!/usr/bin/env python
'''SSH'''

import threading
import paramiko
import subprocess

def ssh_command(ip_addr, user, passwd, command):
    '''SSH'''
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/root/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_addr, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return

ssh_command('127.0.0.1', 'root', 'toor', 'id')
