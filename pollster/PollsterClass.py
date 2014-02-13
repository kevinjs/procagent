# -*- encoding: utf-8 -*
# Copyright © 2013 Computer Network Information Center, Chinese Academy of Sciences
#
# Author: Jing Shao <jingshao@cnic.cn>

'''
The base class of pollster
'''
class Pollster(object):
    def __init__(self, name):
        self.name = name

    def getSample(self):
        pass
