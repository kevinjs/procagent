# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

from collections import OrderedDict
from PollsterClass import Pollster
import util

class MemInfoPollster(Pollster):
    def __init__(self, name='mem_info'):
        super(MemInfoPollster, self).__init__(name=name)

    def _changeUnit(self, value, force_unit=None):
        unit_list = ('KB', 'MB', 'GB')
        rate_list = (1,
                     1024,
                     1024*1024)

        if force_unit:
            if force_unit in unit_list:
                tmp_value = float(value)/rate_list[unit_list.index(force_unit)]
                return {'volume':round(tmp_value, 2), 'unit':force_unit}
            else:
                return {'volume':round(value, 2), 'unit':'KB'}
        else:
            for unit, rate in zip(unit_list, rate_list):
                tmp_value = float(value)/rate
                if (tmp_value >= 0 and tmp_value < 1024) or (unit_list.index(unit) == len(unit_list)-1):
                    return {'volume':round(tmp_value, 2), 'unit':unit}

    def getSample(self):
        mem_info = OrderedDict()
    
        try:
            if util.is_exist('/proc/meminfo'):
                #close file is unnecessary
                with open('/proc/meminfo') as f:
                    for line in f:
                        tmp = line.split(':')
                        if len(tmp) == 2:
                            vol_unit = tmp[1].strip().split(' ')
                            if len(vol_unit) == 2:
                                tmp_value = self._changeUnit(value=long(vol_unit[0]), force_unit='MB')
                            elif len(vol_unit) == 1:
                                tmp_value = {'volume':long(long(vol_unit[0])), 'unit':''}
                            mem_info[tmp[0].strip()] = tmp_value
        except:
            print "Unexpected error:", sys.exc_info()[1]
        finally:
            return mem_info
      
if __name__=='__main__':
    mem = MemInfoPollster()
    util.print_list(mem.getSample())
