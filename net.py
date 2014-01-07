# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

from collections import OrderedDict
import pprint
import util
import sys

'''
cat /proc/net/dev

Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0: 30172565  287376    0    0    0     0          0         0  1735683   10611    0    0    0     0       0          0
    lo:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
'''
def NetStat():
    net_state = OrderedDict()
    title = OrderedDict()
    total_item = 0
    
    try:
        if util.is_exist('/proc/net/dev'):
            with open('/proc/net/dev') as f:
                for line in f:
                    '''
                    Read items
                    '''
                    if line.strip().startswith('Inter'):
                        tmp = line.strip().split('|')
                        for i in range(1, len(tmp)):
                            title[tmp[i].strip()] = []
                    elif line.strip().startswith('face'):
                        tmp = line.strip().split('|')
                        for i in range(1, len(tmp)):
                            title[title.items()[i-1][0]] = tmp[i].strip().split()
                            total_item += len(title.items()[i-1][1])
                    else:
                        tmp = line.strip().split(':')
                        tmp_data = OrderedDict()

                        value = tmp[1].strip().split()
                        if len(value) == total_item:
                            cnt = 0
                            for t_item in title.items():
                                tmp_data[t_item[0]] = {}
                                for it in t_item[1]:
                                    tmp_data[t_item[0]][it] = value[cnt]
                                    cnt += 1
                        else:
                            print 'number of items error'

                        net_state[tmp[0]] = tmp_data
    except:
        print "Unexpected error:", sys.exc_info()[1]
    finally:
        return net_state


if __name__=='__main__':
    util.print_list(NetStat())
