# -*- encoding: utf-8 -*-
'''
@File    :   setting.py
@Time    :   2021/12/03 11:58:35
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Setting(object):
    pass

class TileNameFormat:

    xyz = 1
    zxy = 2

    @classmethod
    def name_format(cls, x, y, z, type):
        if type == cls.xyz:
            return f'{x}/{y}', str(z)
        elif type == cls.zxy:
            return f'{z}/{x}', str(y)
        else:
            raise Exception("没有此命名格式")