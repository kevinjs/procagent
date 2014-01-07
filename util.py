import os
import json

def is_exist(filename):
    return os.path.exists(filename)

def print_list(objList):
    jsonDumpsIndentStr = json.dumps(objList, indent=1)
    print jsonDumpsIndentStr 

def appendFile(content, filename):
    if len(content) != 0:
        output = open(filename, 'a')
        output.write(content)
        output.close()
    else:
        return

