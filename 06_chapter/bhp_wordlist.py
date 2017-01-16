#!/usr/bin/env python
'''bhp bing'''

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.net import URL
from java.util import List, ArrayList

from datetime import datetime
from HTMLParser import HTMLParser
import re
import threading

class TagStripper(HTMLParser):
    '''strip tags'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []
    def handle_data(self, data):
        '''handle data'''
        self.page_text.append(data)
    def handle_comment(self, data):
        '''handle comment'''
        self.handle_data(data)
    def strip(self, html):
        '''strip'''
        self.feed(html)
        return ' '.join(self.page_text)

class BurpExtender(IBurpExtender, IContextMenuFactory):
    '''extender to build word lists'''
    def registerExtenderCallbacks(self, callbacks):
        '''register with burp'''
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        self.hosts = set()

        # start with something we know is common
        self.wordlist = set(['password'])

        # set up our extension
        callbacks.setExtensionName('BHP Wordlist')
        callbacks.registerContextMenuFactory(self)

        return
    def createMenuItems(self, context_menu):
        '''create context menu'''
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem('Create Wordlist', actionPerformed=self.wordlist_menu))
        return menu_list
    def wordlist_menu(self, event):
        '''build the wordlist'''
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            # print 'host: %s' % host                

            self.hosts.add(host)

            http_response = traffic.getResponse()
            if http_response:
                self.get_words(http_response)
        self.display_wordlist()
        return
    def get_words(self, http_response):
        '''get words from response'''
        #print 'getting words...'
        headers, body = http_response.tostring().split('\r\n\r\n', 1)
        # skip non-text responses
        if headers.lower().find('content-type: text') == -1:
            return

        tag_stripper = TagStripper()
        page_text = tag_stripper.strip(body)

        try:
            words = re.findall("[a-zA-Z]\w{2,}", page_text)
        except Exception as err:
            print "Error: %s" % str(err)
        
        print 'getting [%d] words' % len(words)
        for word in words:
            # filter out long strings
            if len(word) <= 12:
                self.wordlist.add(word.lower())
        return
    def mangle(self, word):
        '''mangle word'''
        year = datetime.now().year
        suffixes = ['', '1', '!', year]
        mangled = []
        for password in (word, word.capitalize()):
            for suffix in suffixes:
                mangled.append('%s%s' % (password, suffix))
        return mangled
    def display_wordlist(self):
        '''display passwords'''
        print '#!comment: BHP Wordlist for site(s) %s' % ', '.join(self.hosts)

        for word in sorted(self.wordlist):
            for password in self.mangle(word):
                print password
        return
