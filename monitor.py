# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import sys, time, datetime
import json

from DaemonClass import Daemon
from collections import OrderedDict
from cpu import CPUInfoPollster
from cpu import CPUUsagePollster
from mem import MemInfoPollster
from load import LoadStatPollster
from net import NetStatPollster
import util
import re

class TestMonitor(Daemon):
    intvl = 10
    def __init__(self,
               pidfile='/tmp/test-monitor.pid',
               stdin='/dev/stdin',
               stdout='/dev/stdout',
               stderr='/dev/stderr',
               intvl=10,
               logfile='/opt/monitor.log'):
        Daemon.__init__(self, pidfile=pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
        TestMonitor.intvl = intvl
        self._logfile = logfile
    
    '''
    Set poll interval
    '''
    def set_intvl(self, intvl):
        if intvl >= 1:
            TestMonitor.intvl = intvl
    
    '''
    Basic poll task
    '''
    def _poll(self):
        cpu_info = CPUInfoPollster().getSample()
        cpu_usage = CPUUsagePollster().getSample()
        mem_info = MemInfoPollster().getSample()
        net_info = NetStatPollster().getSample()
        load_info = LoadStatPollster().getSample()
    
        poll_info = OrderedDict()
        for cpu_i in cpu_usage:
            poll_info[cpu_i] = cpu_usage[cpu_i]
    
        poll_info['cpu_num'] = len(cpu_info)
        poll_info['mem_free'] = mem_info['MemFree']
        poll_info['mem_total'] = mem_info['MemTotal']
        poll_info['mem_buffer'] = mem_info['Buffers']
        poll_info['mem_cached'] = mem_info['Cached']
        poll_info['mem_swapfree'] = mem_info['SwapFree']
        poll_info['load_1'] = load_info['load_1_min']
        poll_info['load_5'] = load_info['load_5_min']
        poll_info['load_15'] = load_info['load_15_min']
    
        for net_i in net_info:
            poll_info[net_i+'_recv_bytes'] = net_info[net_i]['Receive']['bytes']
            poll_info[net_i+'_trans_bytes'] = net_info[net_i]['Transmit']['bytes']
            poll_info[net_i+'_recv_pkts'] = net_info[net_i]['Receive']['packets']
            poll_info[net_i+'_trans_pkts'] = net_info[net_i]['Transmit']['packets']
        return poll_info

    def run(self):
	c = 0
        while True:
            poll_info = self._poll()
            content = time.asctime(time.localtime()) + '\n'
            for item in poll_info:
                content += '%s: %s\n' %(item, poll_info[item])
            content += '----------------------------\n\n'
            util.appendFile(content, self._logfile)
            time.sleep(TestMonitor.intvl)
            c = c + 1
            
if __name__ == "__main__":
    daemon = TestMonitor(pidfile='/tmp/test-monitor.pid', 
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
                daemon.restart()
    else:
        print 'USAGE: %s start/stop/restart' % sys.argv[0]
        sys.exit(2)
 
