# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import os
from collections import OrderedDict
from PollsterClass import Pollster
import util

class DiskStatPollster(Pollster):
    def __init__(self, name='disk_stat'):
        super(DiskStatPollster, self).__init__(name=name)

    def _getDiskPartitions(self, all=False):
        """Return all mountd partitions as a nameduple.
        If all == False return phyisical partitions only.
        """
        key_list = ['dev', 'mnt', 'fstype']

        phydevs = []
        f = open("/proc/filesystems", "r")
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())
    
        retlist = []
        f = open('/etc/mtab', "r")
        for line in f:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            
            retlist.append(dict(zip(key_list, fields)))
        return retlist

    def _getDiskUsage(self, path):
        hd = {}
        disk = os.statvfs(path)
        ch_rate = 1024 * 1024 * 1024
        # Free blocks available to non-super user
        hd['available'] = float(disk.f_bsize * disk.f_bavail) / ch_rate
        # Total number of free blocks
        hd['free'] = float(disk.f_bsize * disk.f_bfree) / ch_rate
        # Total number of blocks in filesystem
        hd['capacity'] = float(disk.f_bsize * disk.f_blocks) /ch_rate
        hd['used'] = float(hd['capacity'] - hd['free'])/hd['capacity']
        return hd

    def getSample(self):
        #return self._getDiskUsage('/')
        key_list = ['volume', 'unit']
        disk_list = self._getDiskPartitions()
        for item in disk_list:
            usg = self._getDiskUsage(item['mnt'])
            item['available'] = dict(zip(key_list, [round(usg['available'], 2), 'GB']))
            item['used'] = dict(zip(key_list, [round(usg['used'], 4) * 100, '%']))
            item['capacity'] = dict(zip(key_list, [round(usg['capacity'], 2), 'GB']))
            item['free'] = dict(zip(key_list, [round(usg['free'], 2), 'GB']))
        return disk_list

#{'available': 67, 'used': 0.14102564102564102, 'capacity': 78, 'free': 70}

if __name__=='__main__':
    disk = DiskStatPollster()
    util.print_list(disk.getSample())
