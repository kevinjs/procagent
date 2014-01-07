# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import util
import os

def LoadStat():
    load_stat = {}
    load_info = None
    f = None
    
    try:
        if util.is_exist('/proc/loadavg'):
            f = open('/proc/loadavg')
            load_info = f.read().split()
            if load_info and len(load_info) == 5:
                # Example:
                # cat /proc/loadavg
                # 0.00 0.02 0.05 1/226 3941
                # 0.00 - load avg 1 min
                # 0.02 - load avg 5 min
                # 0.05 - load avg 15 min
                # 1/226 - num of running proc/proc total
                # 3941 - last pid
                load_stat['load_1_min'] = load_info[0]
                load_stat['load_5_min'] = load_info[1]
                load_stat['load_15_min'] = load_info[2]
                load_stat['nr_thread'] = load_info[3]
                load_stat['last_pid'] = load_info[4]
    except:
        print "Unexpected error:", sys.exc_info()[1] 
    finally:
        if f:
            f.close()
        return load_stat

if __name__=='__main__':
    util.print_list(LoadStat())
