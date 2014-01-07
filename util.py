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
def appendFile(content, filename):
    if len(content) != 0:
        output = open(filename, 'a')
        output.write(content)
        output.close()
    else:
        return

