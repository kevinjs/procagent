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

    def getSample(self):
        mem_info = OrderedDict()
    
        try:
            if util.is_exist('/proc/meminfo'):
                #close file is unnecessary
                with open('/proc/meminfo') as f:
                    for line in f:
                        tmp = line.split(':')
                        if len(tmp) == 2:
                            mem_info[tmp[0].strip()] = tmp[1].strip()
        except:
            print "Unexpected error:", sys.exc_info()[1]
        finally:
            return mem_info
      
if __name__=='__main__':
    mem = MemInfoPollster()
    print mem.getSample() 
