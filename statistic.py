#!/usr/env python
import sys
import time
import string
import datetime
import pymongo
import getopt
import pytz
from functools import wraps
from pollster import util

COUNTER_NAME_FILTER = {'instance.cpu.usage':{'avg':'counter_volume', 'peak':'counter_volume'},
                       'instance.mem.usage':{'avg':'counter_volume', 'peak':'counter_volume'},
                       'instance.net.in.bytes':{'cum':'bytes_in_sum', 'avg':'counter_volume', 'peak':'counter_volume'},
                       'instance.net.out.bytes':{'cum':'bytes_out_sum', 'avg':'counter_volume', 'peak':'counter_volume'},}

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TZ = pytz.timezone('Asia/Taipei')

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print 'cost:%s sec' %(round(end-start, 4))
        return result
    return wrapper

@timeit
def run_statistic(st, et, conn):
    db = conn['ceilometer']
    col = db['meter']

    data_dict = {}
    for k, v in COUNTER_NAME_FILTER.items():
        query = {'counter_name':k, 'timestamp':{'$gte':st, '$lte':et}}
        cursor = col.find(query).sort('timestamp', pymongo.DESCENDING)

        instance_dict = {}
        for item in cursor:
            if not instance_dict.has_key(item['resource_id']):
                # when meet a new instance
                tmp = {}
                for v_k, v_v in v.items():
                    if v_k == 'avg':
                        tmp['avg'] = item[v_v]
                    elif v_k == 'peak':
                        tmp['peak'] = item[v_v]
                        #tmp['peak_time'] = item['timestamp'].strftime(TIME_FORMAT)
                        tmp['peak_time'] = item['timestamp'].replace(tzinfo=pytz.utc).astimezone(TZ).strftime(TIME_FORMAT)
                    elif v_k == 'cum':
                        tmp['cum'] = item['resource_metadata'][v_v]
                        tmp['cum_last'] = item['resource_metadata'][v_v]
                tmp['cnt'] = 1
                instance_dict[item['resource_id']] = tmp
            else:
                for v_k, v_v in v.items():
                    if v_k == 'avg':
                        instance_dict[item['resource_id']]['avg'] += item[v_v]
                    elif v_k == 'peak' and instance_dict[item['resource_id']]['peak'] < item[v_v]:
                        instance_dict[item['resource_id']]['peak'] = item[v_v]
                        #instance_dict[item['resource_id']]['peak_time'] = item['timestamp'].strftime(TIME_FORMAT)
                        instance_dict[item['resource_id']]['peak_time'] = item['timestamp'].replace(tzinfo=pytz.utc).astimezone(TZ).strftime(TIME_FORMAT)
                    elif v_k == 'cum':
                        if instance_dict[item['resource_id']]['cum_last'] > item['resource_metadata'][v_v]:
                            # reboot or clean cumulative value
                            instance_dict[item['resource_id']]['cum'] += item['resource_metadata'][v_v]
                        else:
                            instance_dict[item['resource_id']]['cum'] += item['resource_metadata'][v_v] - instance_dict[item['resource_id']]['cum_last']
                        instance_dict[item['resource_id']]['cum_last'] = item['resource_metadata'][v_v]
                instance_dict[item['resource_id']]['cnt'] += 1
        for ins_k, ins_v in instance_dict.items():
            if ins_v.has_key('avg'):
                ins_v['avg'] = float(ins_v['avg']) / ins_v['cnt']
        data_dict[k] = instance_dict
    return data_dict

if __name__=='__main__':
    conn_mongo = None
    host = None
    port = None
    st = None
    et = None

    opts, args = getopt.getopt(sys.argv[1:], "a:s:e:h")
    for op, value in opts:
        if op == "-a":
            host = value[0:value.rindex(':')]
            port = string.atoi(value[value.rindex(':')+1:len(value)])
        elif op == "-s":
            st = datetime.datetime.strptime(value, TIME_FORMAT)
            st = st.replace(tzinfo=TZ).astimezone(pytz.utc)
            st = TZ.normalize(st)
        elif op == "-e":
            et = datetime.datetime.strptime(value, TIME_FORMAT)
            et = et.replace(tzinfo=TZ).astimezone(pytz.utc)
            et = TZ.normalize(et)
        elif op == "-h":
            print 'python statistic.py -a 127.0.0.1:27017 -s "start_time" -e "end_time"'
 
    if host and port and st:
        if not et:
            et = datetime.datetime.now()
            et = et.replace(tzinfo=TZ).astimezone(pytz.utc)
            et = TZ.normalize(et)
        conn_mongo = pymongo.Connection(host, port)
        util.print_list(run_statistic(st=st, et=et, conn=conn_mongo))
        conn_mongo.close()
