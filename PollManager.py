# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import sys, time, datetime
import json, re, socket
from collections import OrderedDict
from DaemonClass import Daemon
from pollster import util

class PollManager(Daemon):
    _intvl = None
    _pollsters = OrderedDict()
    _wr_url = None

    def __init__(self,
               pidfile='/tmp/daemoncls.pid',
               stdin='/dev/null',
               stdout='/dev/null',
               #stdout='/tmp/poll_stdout.out',
               stderr='/dev/null',
               intvl=10,
               wr_url='http://127.0.0.1:8655/'):
        super(PollManager, self).__init__(pidfile=pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
        self._wr_url = wr_url
        
        # Read interval
        tmp_str = util.rd_data('%s%s' %(self._wr_url, 'getintvl'))
        if tmp_str:
            self._intvl = int(tmp_str)
        else:
            self._intvl = intvl

        # Read pollsters
        tmp_str = util.rd_data('%s%s' %(self._wr_url, 'getpollsters'))
        if tmp_str:
            tmp_list = eval(tmp_str)
            if type(tmp_list) == type(''):
                tmp_list = eval(tmp_list)
            for poll in tmp_list:
                p_name, cls = util.load_class(poll)
                if p_name and cls:
                    self._pollsters[p_name] = cls()
        else:
            self._pollsters = OrderedDict()

    def set_intvl(self, intvl):
        '''Set interval of polling'''
        if intvl >= 1:
            self._intvl = intvl
            util.wr_data('%s%s' %(self._wr_url, 'setintvl'), intvl)
            self.restart()

    def set_pollsters(self, pollsters):
        '''Set pollster list'''
        poll_list = eval(pollsters)
        self._pollsters = OrderedDict()
        for poll in poll_list:
            p_name, cls = util.load_class(poll)
            if p_name and cls:
                self._pollsters[p_name] = cls()
        util.wr_data('%s%s' %(self._wr_url, 'setpollsters'), pollsters)
        self.restart()

    def _poll(self):
        '''Execute poll task'''
        poll_data = OrderedDict()
        if self._pollsters:
            for pollster in self._pollsters:
                poll_data[pollster] = {}
                poll_data[pollster]['timestamp'] = time.asctime(time.localtime())
                #poll_data[pollster]['timestamp'] = time.time()
                poll_data[pollster]['data'] = self._pollsters[pollster].getSample()
        return poll_data

    def run(self):
        c = 0
        while True:
            wr_obj = {}
            wr_obj['data'] = self._poll()
            #wr_obj['timestamp'] = time.asctime(time.localtime())
            wr_obj['hostname'] = socket.gethostname()
            wr_obj['ip_address'] = socket.gethostbyname(wr_obj['hostname'])
            wr_obj['timestamp'] = time.asctime(time.localtime())
            util.wr_data('%s%s' %(self._wr_url, 'setdata'), wr_obj)
            time.sleep(self._intvl)
            c += 1

if __name__ == "__main__":
    daemon = PollManager(pidfile='/tmp/polling_task.pid', 
                           intvl=10) 
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'Unknown command'
            sys.exit(2)
    elif len(sys.argv) == 3:
        if 'setintvl' == sys.argv[1]:
            if re.match(r'^-?\d+$', sys.argv[2]) or re.match(r'^-?(\.\d+|\d+(\.\d+)?)', sys.argv[2]):
                daemon.set_intvl(int(sys.argv[2]))
                print 'Set interval: %s' %sys.argv[2]
        elif 'setpoll' == sys.argv[1]:
            poll_list = None
            try:
                poll_list = eval(sys.argv[2])
            except:
                print '%s is not a list.' %sys.argv[2]
            if poll_list:
                daemon.set_pollsters(sys.argv[2])
    else:
        print 'USAGE: %s start/stop/restart' % sys.argv[0]
        sys.exit(2)
 
