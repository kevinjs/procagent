# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

from collections import OrderedDict
import pprint
import util
import time
from PollsterClass import Pollster

class CPUInfoPollster(Pollster):
    def __init__(self, name='cpu_info'):
        super(CPUInfoPollster, self).__init__(name=name)

    def getSample(self):
        cpu_info = OrderedDict()
        proc_info = OrderedDict()

        nprocs = 0

        try:    
            if util.is_exist('/proc/cpuinfo'):
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if not line.strip():
                            cpu_info['proc%s' % nprocs] = proc_info
                            nprocs += 1
                            proc_info = OrderedDict()
                        else:
                            if len(line.split(':')) == 2:
                                proc_info[line.split(':')[0].strip()] = line.split(':')[1].strip()
                            else:
                                proc_info[line.split(':')[0].strip()] = ''
        except:
            print "Unexpected error:", sys.exc_info()[1]
        finally:    
            return cpu_info

class CPUUsagePollster(Pollster):
    def __init__(self, name='cpu_info'):
        super(CPUUsagePollster, self).__init__(name=name)

    '''
    Read CPU stat from /proc/stat.
    '''
    def _read_proc_stat(self):
        cpu_line = OrderedDict()
        f = None
    
        try:
            if util.is_exist('/proc/stat'):
                f = open('/proc/stat')
                lines = f.readlines()
                for line in lines:
                    if line.startswith('cpu'):
                        tmp = line.strip().split()
                        cpu_line[tmp[0]] = tmp[1:len(tmp)]
        except:
            print "Unexpected error: ", sys.exc_info[1]
        finally:
            if f:
                f.close()
            return cpu_line

    def getSample(self):
        cpu_usage = {}
        cpu_line = self._read_proc_stat()
        total_1 = {}
        idle_1 = {}
        total_2 = {}
        idle_2 = {}
    
        if cpu_line:
            for item in cpu_line:
                total_1[item] = float(cpu_line[item][0]) + float(cpu_line[item][1]) + \
                        float(cpu_line[item][2]) + float(cpu_line[item][3]) + \
                        float(cpu_line[item][4]) + float(cpu_line[item][5]) + float(cpu_line[item][6])
                idle_1[item] = float(cpu_line[item][3])
    
            time.sleep(1)
            
            cpu_line_2 = self._read_proc_stat()
     
            if cpu_line_2:
                for item in cpu_line_2:
                    total_2[item] = float(cpu_line_2[item][0]) + float(cpu_line_2[item][1]) + \
                              float(cpu_line_2[item][2]) + float(cpu_line_2[item][3]) + \
                              float(cpu_line_2[item][4]) + float(cpu_line_2[item][5]) + float(cpu_line_2[item][6])
                    idle_2[item] = float(cpu_line_2[item][3])
    
            if total_1 and total_2:
                for item in total_1:
                    cpu_usage[item] = {'volume':round(100 * (1 - float(idle_2[item] - idle_1[item])/float(total_2[item] - total_1[item])), 2), 'unit':'%'}
        return cpu_usage       

