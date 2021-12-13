# -*- encoding: utf-8 -*-
'''
@File    :   tiler.py
@Time    :   2021/12/13 17:08:29
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib
import argparse
import logging
import logging.config
import os

from tilemap.map.tifmap import TifMap
from tilemap.tiler.tiler import get_service_cls
from tilemap.conf.setting import TileServiceDefine
from tilemap.conf.log import get_log_config

logger = logging.getLogger(__name__)

def init_args():
    """
    initialization args
    """

    parser = argparse.ArgumentParser(description='Tile cutout service')

    parser.add_argument('-i', '--input', type=str, required=False, help='path of the tif')
    parser.add_argument('-o', '--output', default='./map', type=str, required=False, help='output path')
    parser.add_argument('-t', '--type', default=TileServiceDefine.amap, type=int, required=False, help="tile service type")
    parser.add_argument('-min', '--minlevel', default=0, type=int, required=False, help="Slice minimum level")
    parser.add_argument('-max', '--maxlevel', default=21, type=int, required=False, help="Slice maximum level")
    parser.add_argument('-e', '--loglevel', default='INFO',  type=str, required=False, help="Log level")
    parser.add_argument('-l', '--logfile', default='./tile.log',  type=str, required=False, help="Log file path")

    return parser.parse_args()


def args_filter(args):

    input = args.input
    output = args.output
    type = args.type
    minlevel = args.minlevel
    maxlevel = args.maxlevel
    loglevel = args.loglevel
    logfile = args.logfile

    if not os.path.isabs(input):
        input = os.path.abspath(input)
    
    if not os.path.isabs(output):
        output = os.path.abspath(output)
    
    if not os.path.isabs(logfile):
        logfile = os.path.abspath(logfile)
    

    return {
        'input': input,
        'output': output,
        'type': type,
        'minlevel': minlevel,
        'maxlevel': maxlevel,
        'loglevel': loglevel,
        'logfile': logfile
    }


def execute():

    args = init_args()
    args = args_filter(args)
    
    # 配置log
    logconfig = get_log_config(level=args.get('loglevel'), 
                               logfile=args.get('logfile'))
    logging.config.dictConfig(logconfig)

    service_cls = get_service_cls(args.get('type'))

    map = TifMap(args.get('input'))
    # TODO: 判断地理坐标系与投影坐标系

    service_cls(
        map, 
        map_path=args.get('output'), 
        minlevel=args.get('minlevel'), 
        maxlevel=args.get('maxlevel')
    ).run()
