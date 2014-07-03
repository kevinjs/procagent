# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

from collections import OrderedDict
import pprint
import util
import time
from PollsterClass import Pollster


class UptimePollster(Pollster):
    def __init__(self, name='uptime_info'):
        super(UptimePollster, self).__init__(name=name)

    def getSample(self):
        cpu_info = OrderedDict()
        proc_info = OrderedDict()
	uptime_info = {}

        nprocs = 0

        try:
            # Get cpu number
            if util.is_exist('/proc/cpuinfo'):
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if not line.strip():
                            nprocs += 1
            # Get uptime and idletime
	    if util.is_exist('/proc/uptime'):
		with open('/proc/uptime') as f:
	            for line in f:
	                if line.strip():
			    if len(line.split(' ')) == 2:
				uptime_info['uptime'] = {'volume':float(line.split(' ')[0].strip()),'unit':'s'}
				uptime_info['idletime'] = {'volume':float(line.split(' ')[1].strip()),'unit':'s'}
				uptime_info['cpu_num'] = {'volume':nprocs,'unit':''}
	    # Compute idle rate
	    uptime_info['idle_rate'] = {'volume':(uptime_info['idletime']['volume'] * 100) / (uptime_info['cpu_num']['volume'] * uptime_info['uptime']['volume']),'unit':'%'}
        except:
            print "Unexpected error:", sys.exc_info()[1]
        finally:    
            return uptime_info

if __name__=='__main__':
    print UptimePollster().getSample()
