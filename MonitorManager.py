# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import sys, time, datetime
import json, re
import util
from collections import OrderedDict
from DaemonClass import Daemon

class MonitorManager(Daemon):
    '''
    {'cpu_info':{'cls':CPUInfoPollster(), 'is_active':True},...}
    '''
    _intvl = None
    _pollsters = OrderedDict()
    _logfile = None

    def __init__(self,
               pidfile='/tmp/test-monitor.pid',
               stdin='/dev/stdin',
               stdout='/dev/stdout',
               stderr='/dev/stderr',
               intvl=10,
               logfile='/opt/monitor.log'):
        super(MonitorManager, self).__init__(pidfile=pidfile, stdin=stdin, stdout=stdout, stderr=stderr)

        paras = util.load_conf('conf')

        MonitorManager._logfile = logfile

        if not paras.has_key('intvl'):
            MonitorManager._intvl = intvl
            paras['intvl'] = intvl
        else:
            MonitorManager._intvl = int(paras['intvl'])

        if paras.has_key('pollsters'):
            tmp_list = eval(paras['pollsters'])
            for poll in tmp_list:
                p_name, cls = util.load_class(poll)
                if p_name and cls:
                    MonitorManager._pollsters[p_name] = cls()
        else:
            MonitorManager._pollsters = OrderedDict()

        util.update_conf('conf', paras)

    '''
    Set poll interval
    '''
    def set_intvl(self, intvl):
        paras = util.load_conf('conf')
        if intvl >= 1:
            MonitorManager._intvl = intvl
            paras['intvl'] = intvl
            util.update_conf('conf', paras)
            self.restart()

    def set_pollsters(self, poll_list):
        paras = util.load_conf('conf')
        MonitorManager._pollsters = OrderedDict()
        for poll in poll_list:
            p_name, cls = util.load_class(poll)
            if p_name and cls:
                MonitorManager._pollsters[p_name] = cls()
        if poll_list:
            paras['pollsters']='%s' %poll_list
            util.update_conf('conf', paras)
        self.restart()

    '''
    Execute poll task
    '''
    def _poll(self):
        poll_data = OrderedDict()
        if MonitorManager._pollsters:
            for pollster in MonitorManager._pollsters:
                poll_data[pollster] = {}
                poll_data[pollster]['timestamp'] = time.asctime(time.localtime())
                poll_data[pollster]['data'] = MonitorManager._pollsters[pollster].getSample()
        return poll_data

    def run(self):
        c = 0
        while True:
            poll_info = self._poll()
            content = time.asctime(time.localtime()) + '\n'
            for item in poll_info:
                content += '++++%s: %s\n' %(item, str(poll_info[item]))
            content += '----------------------------\n\n'
            util.append_file(content, MonitorManager._logfile)
            time.sleep(MonitorManager._intvl)
            c = c + 1

if __name__ == "__main__":
    daemon = MonitorManager(pidfile='/tmp/test-monitor.pid', 
                           intvl=10)
   
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
#        elif 'prtpoll' == sys.argv[1]:
#            print 'Running pollsters:'
#            util.print_list(daemon.get_pollsters())
#        elif 'prtintvl' == sys.argv[1]:
#            print 'Global interval: %s' %daemon.get_intvl()
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
                daemon.set_pollsters(poll_list)
    else:
        print 'USAGE: %s start/stop/restart' % sys.argv[0]
        sys.exit(2)
 
