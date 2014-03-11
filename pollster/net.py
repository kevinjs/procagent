# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

from collections import OrderedDict
from PollsterClass import Pollster
import pprint
import util
import sys
import time

'''
cat /proc/net/dev

Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0: 30172565  287376    0    0    0     0          0         0  1735683   10611    0    0    0     0       0          0
    lo:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
'''
class NetStatPollster(Pollster):
    def __init__(self, name='net_stat'):
        super(NetStatPollster, self).__init__(name=name)

    def _get_data(self):
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

                total_data = {'net_bytes_in':0,
                              'net_bytes_out':0,
                              'net_pkts_in':0,
                              'net_pkts_out':0}
                for key, value in net_state.items():
                    if key.startswith('eth'):
                        total_data['net_bytes_in'] += int(value['Receive']['bytes'])
                        total_data['net_bytes_out'] += int(value['Transmit']['bytes'])
                        total_data['net_pkts_in'] += int(value['Receive']['packets'])
                        total_data['net_pkts_out'] += int(value['Transmit']['packets'])
        except:
            print "Unexpected error:", sys.exc_info()[1]
        finally:
            return net_state, total_data

    def getSample(self):
        intvl = .5

        net_state_1, total_data_1 = self._get_data()
        time.sleep(intvl)
        net_state_2, total_data_2 = self._get_data()

        flow_data={}
        flow_data['net_bytes_in'] = {'volume':int((total_data_2['net_bytes_in'] - total_data_1['net_bytes_in'])/intvl), 'unit':'B/s'}
        flow_data['net_bytes_out'] = {'volume':int((total_data_2['net_bytes_out'] - total_data_1['net_bytes_out'])/intvl), 'unit':'B/s'}
        flow_data['net_pkts_in'] = {'volume':int((total_data_2['net_pkts_in'] - total_data_1['net_pkts_in'])/intvl), 'unit':'p/s'}
        flow_data['net_pkts_out'] = {'volume':int((total_data_2['net_pkts_out'] - total_data_1['net_pkts_out'])/intvl), 'unit':'p/s'}
        flow_data['net_bytes_in_sum'] = {'volume':int(total_data_2['net_bytes_in']), 'unit':'B'}
        flow_data['net_bytes_out_sum'] = {'volume':int(total_data_2['net_bytes_out']), 'unit':'B'}

        return flow_data

    def test(self):
        net_state, total_data = self._get_data()

        util.print_list(net_state)
        util.print_list(total_data)

if __name__=='__main__':
    net_stat = NetStatPollster()
    net_stat.test()
