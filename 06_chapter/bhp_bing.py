#!/usr/bin/env python
'''bhp bing'''

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.net import URL
from java.util import List, ArrayList

import socket
import urllib
import urllib2
import json
import re
import base64
import threading


class BurpExtender(IBurpExtender, IContextMenuFactory):
    '''Custom code to bing search on burp data'''
    def get_my_key(self):
        '''Gets a bing key'''
        return '79d54ab82d0746e6bb74e31560f34a69'

    def registerExtenderCallbacks(self, callbacks):
        '''register with burp'''
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # set up our extension
        callbacks.setExtensionName('BHP Bing')
        callbacks.registerContextMenuFactory(self)

        return
    def createMenuItems(self, context_menu):
        '''create context menu'''
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem('Send to Bing', actionPerformed=self.bing_menu))
        return menu_list
    def bing_menu(self, event):
        '''bing the selected data'''
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        print '%d requests highlighted' % len(http_traffic)

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
        self.do_bing_query(bing_query_string)
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.do_bing_query(bing_query_string)
    def do_bing_query(self, bing_query_string):
        '''start a bing_query thread'''
        thread = threading.Thread(target=bing_runner, args=(self, bing_query_string))
        thread.start()
    def bing_query(self, bing_query_string):
        '''query bing'''
        print 'Performing Bing search: %s' % bing_query_string

        # encode our query
        quoted_query = urllib.quote(bing_query_string)
        my_key = base64.b64encode(':%s' % self.get_my_key())

        host = 'api.datamarket.azure.com'
        host = 'api.cognitive.microsoft.com'
        base_url = 'https://%s/Bing/Search/Web' % host
        base_url = 'https://%s/bing/v5.0/search?q='
        agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        http_request = 'GET %s?$format=json&$top=20&Query=%s' % (base_url, quoted_query)
        http_request += ' HTTP/1.1\r\n'
        http_request += 'Host: %s\r\n' % host
        http_request += 'Connection: close\r\n'
        http_request += 'Authorization: Basic %s\r\n' % my_key
        http_request += 'User-Agent: %s' % agent

        print 'Making http_request...',
        json_body = self._callbacks.makeHttpRequest(host, 443, True, http_request).tostring()
        json_body = json_body.split('\r\n\r\n', 1)[1]
        print 'done.'

        try:
            r = json.loads(json_body)
            print str(r)
            if len(r['d']['results']):
                for site in r['d']['results']:
                    print '*' * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print '*' * 100
                    j_url = URL(site['Url'])

                    if not self._callbacks.isInScope(j_url):
                        print 'Adding to Burp Scope'
                        self._callbacks.includeInScope(j_url)
        except Exception as err:
            print str(err)
            #print 'No results from Bing'
        return

def bing_runner(burp_ext, bing_query_string):
    '''run bing_query'''
    burp_ext.bing_query(bing_query_string)
