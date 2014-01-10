# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

import os
import json

'''
Check the file.
'''
def is_exist(filename):
    return os.path.exists(filename)

'''
Print list or object.
'''
def print_list(objList):
    jsonDumpsIndentStr = json.dumps(objList, indent=1)
    print jsonDumpsIndentStr 

'''
Append file.
'''
def append_file(content, filename):
    if len(content) != 0:
        output = open(filename, 'a')
        output.write(content)
        output.close()
    else:
        return

'''
Load module and class
'''
def load_class(clsname):
    cls = None
    bse_name = None
    try:
        r = clsname.rfind('.')
        dft_name = '__main__'
        bse_name = clsname
        if r >= 0:
            dft_name = clsname[0:r]
            bse_name = clsname[r+1:]
        mod = __import__(dft_name)
        cls = getattr(mod, bse_name)
    except:
        return None
    finally:
        return bse_name, cls

def load_conf(confname):
    paras = {}
    if is_exist(confname):
        with open(confname) as f:
            for line in f:
                tmp = line.strip().split('=')
                if len(tmp) == 2:
                    paras[tmp[0]] = tmp[1]
    return paras

def update_conf(confname, paras):
    w_str = ''
    if paras:
        for p in paras:
            w_str += '%s=%s\n' %(p, paras[p])
    if w_str:
        try:
            output = open(confname, 'w')
            output.write(w_str)
        except:
            print 'Update conf error!'
        finally:
            if output:
                output.close()
