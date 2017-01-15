#!/usr/bin/env python
'''bhp bing'''

from burp import IBurpExtender
from burp import IContextMenuExtenderFactory

from javax.swing import JMenuItem
from java.net import URL
from java.util import List, ArrayList

import socket
import urllib
import urllib2
import json
import re
import base64

BING_API_KEY = get_my_key()
def get_my_key():
    '''Gets a bing key'''
    return '79d54ab82d0746e6bb74e31560f34a69'


class BurpExtender(IBurpExtender, IContextMenuExtenderFactory):
    '''Custom code to bing search on burp data'''
    def registerExtenderCallbacks(self, callbacks):
        '''register with burp'''
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # set up our extension
        callbacks.setExtensionName('BHP Bing')
        callbacks.registerContextMenuFactory(self)

        return
    def createContextMenu(self, context_menu):
        '''create context menu'''
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem('Send to Bing', actionPerformed=self.bing_menu))
        return menu_list
    def bing_menu(self, event):
        '''bing the selected data'''
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        print '%d requests highlighted'

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            print 'User selected host %s' % host
            self.bing_search(host)
        return
    def bing_search(self, host):
        '''bing the host'''
        # check if we have an ip or host name
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        bing_query_string = "'ip:%s'" % ip_address
        self.bing_query(bing_query_string)
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)
    def bing_query(self, bing_query_string):
        '''query bing'''
        pass
