# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import os
import time
from collections import OrderedDict
from PollsterClass import Pollster
import util

class DiskUsagePollster(Pollster):
    def __init__(self, name='disk_stat'):
        super(DiskUsagePollster, self).__init__(name=name)

    def _changeUnit(self, value, force_unit=None):
        unit_list = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
        rate_list = (1,
                     1024,
                     1024*1024,
                     1024*1024*1024,
                     1024*1024*1024*1024,
                     1024*1024*1024*1024*1024,)

        if force_unit:
            if force_unit in unit_list:
                tmp_value = float(value)/rate_list[unit_list.index(force_unit)]
                return {'volume':round(tmp_value, 2), 'unit':force_unit}
            else:
                return {'volume':round(value, 2), 'unit':'B'}
        else:
            for unit, rate in zip(unit_list, rate_list):
                tmp_value = float(value)/rate
                if tmp_value >= 1 and tmp_value < 1024:
                    return {'volume':round(tmp_value, 2), 'unit':unit}

    def _read_diskstats(self, dev):
        if dev:
            f = open("/proc/diskstats", "r")
            dev_data = {}
            for line in f:
                tmp = line.strip().split()
                if dev.has_key(tmp[2]):
                    # Kernel > 2.6
                    dev_data[tmp[2]] = {}
                    dev_data[tmp[2]]['f1'] = float(tmp[3])    # of reads completed
#                    dev_data[tmp[2]]['f2'] = float(tmp[4])    # of reads merged
                    dev_data[tmp[2]]['f3'] = float(tmp[5])    # of sectors read
#                    dev_data[tmp[2]]['f4'] = float(tmp[6])    # of milliseconds spent reading
                    dev_data[tmp[2]]['f5'] = float(tmp[7])    # of writes completed
#                    dev_data[tmp[2]]['f6'] = float(tmp[8])    # of writes merged
                    dev_data[tmp[2]]['f7'] = float(tmp[9])    # of sectors written
#                    dev_data[tmp[2]]['f8'] = float(tmp[10])   # of milliseconds spent writing
#                    dev_data[tmp[2]]['f9'] = float(tmp[11])   # of I/Os currently in progress
#                    dev_data[tmp[2]]['f10'] = float(tmp[12])  # of milliseconds spent doing I/Os
#                    dev_data[tmp[2]]['f11'] = float(tmp[13])  # weight of of milliseconds spent doing I/Os
            return dev_data
        else:
            return {}

    def _getDiskIO(self, dev_list):
        if dev_list:
            dev_data = {}
            for item in dev_list:
                dev_short = item['dev'][item['dev'].rfind('/')+1:]
                dev_data[dev_short] = {}

            intvl = 1
            disk_stats_1 = self._read_diskstats(dev_data)
            time.sleep(intvl)
            disk_stats_2 = self._read_diskstats(dev_data)

            disk_io = {}
            for disk in disk_stats_2:
                disk_io[disk] = {}
                
#                disk_io[disk]['rrqm/s'] = disk_stats_2[disk]['f2'] - disk_stats_1[disk]['f2']
#                disk_io[disk]['wrqm/s'] = disk_stats_2[disk]['f6'] - disk_stats_1[disk]['f6']
                disk_io[disk]['r/s'] = {'volume':disk_stats_2[disk]['f1'] - disk_stats_1[disk]['f1'], 'unit':''}
                disk_io[disk]['w/s'] = {'volume':disk_stats_2[disk]['f5'] - disk_stats_1[disk]['f5'], 'unit':''}
#                disk_io[disk]['rsec/s'] = disk_stats_2[disk]['f3'] - disk_stats_1[disk]['f3']
#                disk_io[disk]['wsec/s'] = disk_stats_2[disk]['f7'] - disk_stats_1[disk]['f7']
                rsec_s = disk_stats_2[disk]['f3'] - disk_stats_1[disk]['f3']
                wsec_s = disk_stats_2[disk]['f7'] - disk_stats_1[disk]['f7']
                disk_io[disk]['rkB/s'] = {'volume':rsec_s * 0.5, 'unit':'KB/s'}
                disk_io[disk]['wkB/s'] = {'volume':wsec_s * 0.5, 'unit':'KB/s'}
#                disk_io[disk]['avgrq-sz'] = round((disk_io[disk]['rsec/s'] + disk_io[disk]['wsec/s'])/(disk_io[disk]['r/s'] + disk_io[disk]['w/s']), 2)
#                disk_io[disk]['avgqu-sz'] = round(disk_stats_2[disk]['f11'] - disk_stats_1[disk]['f11'], 2)
#                disk_io[disk]['await'] = round(((disk_stats_2[disk]['f4'] - disk_stats_1[disk]['f4'])+(disk_stats_2[disk]['f8'] - disk_stats_1[disk]['f8']))/(disk_io[disk]['r/s']+disk_io[disk]['w/s']), 2)
#                disk_io[disk]['r_await'] = round((disk_stats_2[disk]['f4'] - disk_stats_1[disk]['f4'])/disk_io[disk]['r/s'], 2)
#                disk_io[disk]['w_await'] = round((disk_stats_2[disk]['f8'] - disk_stats_1[disk]['f8'])/disk_io[disk]['w/s'], 2)
                #disk_io[disk]['util'] = 
                #http://hi.baidu.com/casualfish/item/0126b4b7dbde13e94fc7fdb0
            return disk_io
        else:
            return {} 

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
        
        # Add nfs4 and glusterfs
        if 'nfs4' not in phydevs:
            phydevs.append('nfs4')
        if 'fuse.glusterfs' not in phydevs:
            phydevs.append('fuse.glusterfs')

        retlist = []
        f = open('/etc/mtab', "r")
        for line in f:
            #if not all and line.startswith('none'):
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
        hd['available'] = disk.f_bsize * disk.f_bavail
        # Total number of free blocks
        hd['free'] = disk.f_bsize * disk.f_bfree
        # Total number of blocks in filesystem
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = float(hd['capacity'] - hd['free'])/hd['capacity']
        return hd

    def getSample(self):
        disk_list = self._getDiskPartitions()
        # disk io
        disk_io = self._getDiskIO(disk_list)

        total_available = 0
        total_capacity = 0
        total_free = 0

        disk_usage = {}
        for item in disk_list:
            usg = self._getDiskUsage(item['mnt'])

            dev_short = item['dev'][item['dev'].rfind('/')+1:]
            disk_usage[dev_short] = {}
            disk_usage[dev_short]['mnt'] = item['mnt']
            disk_usage[dev_short]['fstype'] = item['fstype']
            disk_usage[dev_short]['dev'] = item['dev']
            disk_usage[dev_short]['available'] = self._changeUnit(value=usg['available'], force_unit='GB')
            total_available += disk_usage[dev_short]['available']['volume']

            disk_usage[dev_short]['used'] = round(usg['used'], 4)
            disk_usage[dev_short]['capacity'] = self._changeUnit(value=usg['capacity'], force_unit='GB')
            total_capacity += disk_usage[dev_short]['capacity']['volume']

            disk_usage[dev_short]['free'] = self._changeUnit(value=usg['free'], force_unit='GB')
            total_free += disk_usage[dev_short]['free']['volume']

            if disk_io.has_key(dev_short):
                disk_usage[dev_short]['io_stat'] = disk_io[dev_short]

        disk_usage['total_available'] = total_available
        disk_usage['total_capacity'] = total_capacity
        disk_usage['total_free'] = total_free

        return disk_usage

    def test(self):
        disk_list = self._getDiskPartitions()
        return self._getDiskIO(disk_list)

if __name__=='__main__':
    disk = DiskUsagePollster()
    util.print_list(disk.getSample())
