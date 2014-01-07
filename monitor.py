# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import sys, time, datetime
import json

from DaemonClass import Daemon
import cpu
import mem
import load
import net
import util

class TestMonitor(Daemon):
    def __init__(self,
               pidfile='/tmp/test-monitor.pid',
               stdin='/dev/null',
               stdout='/dev/null',
               stderr='/dev/null',
               intvl=10,
               logfile='/tmp/monitor.log'):
        Daemon.__init__(self, pidfile=pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
        self._intvl = intvl
        self.logfile = logfile

    def poll():
        cpu_info = cpu.CPUInfo()
        cpu_usage = cpu.CPUUsage()
        mem_info = mem.MemInfo()
        net_info = net.NetStat()
        load_info = load.LoadStat()

        poll_info = {}
        poll_info['cpu_usage'] = cpu_usage
        poll_info['cpu_num'] = len(cpu_info)
        poll_info['mem_free'] = mem_info['MemFree']
        poll_info['mem_total'] = mem_info['MemTotal']
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
        while True:
            chk_time = datetime.datetime.now()
            poll_info = self.poll()
            write_str = chk_time.strftime("%Y-%m-%dT%H:%M:%S") + '-----------\n'
            for item in poll_info:
                write_str += '%s: %s\n' % (item, poll_info[item])
            util.appendFile(write_str, self.logfile)
            time.sleep(self._intvl)
            
if __name__ == "__main__":
    daemon = TestMonitor(pidfile='/tmp/test-m.pid', 
                           intvl=10, 
                           logfile='/tmp/moni.log')
   
    import pdb;pdb.set_trace() 
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
    else:
        print 'USAGE: %s start/stop/restart' % sys.argv[0]
        sys.exit(2)
 
