# -*- encoding: utf-8 -*-
'''
@File    :   tiler.py
@Time    :   2021/12/03 17:35:16
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''
import math
import logging
import os
from osgeo import gdal
from tilemap.map.tifmap import TifMap, polygon_wgs84togcj02
from tilemap.utils.shape import Point, Polygon, box
from tilemap.utils.utils import resolution, pixel_num
from tilemap.conf.setting import TileNameFormat, TileServiceDefine

# 设定Imagine风格的pyramids
gdal.SetConfigOption('HFA_USE_RRD', 'YES')

logger = logging.getLogger(__name__)

# here put the import lib
class MapTilerService(object):

    def __init__(self, 
                map:TifMap, 
                map_path: str = './map', 
                named_type=TileNameFormat.zxy, 
                minlevel: int = 0, 
                maxlevel: int = 21):

        self.map = map
        self.minlevel = minlevel
        self.maxlevel = maxlevel
        
        if not os.path.isabs(map_path):
            map_path = os.path.abspath(map_path)
        
        self.map_path = map_path
        self.named_type = named_type
    
    @staticmethod
    def lonlat2xytile(point: Point, level: int):
        """经纬度转瓦片编号
        # TODO:整理
        """
        lon = point.x
        lat = point.y
        lat_rad = math.radians(lat)
        xtile = int(((lon + 180.0) / 360.0) * (2.0 ** level))
        ytile = int(((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0) * (2.0 ** level))
        return (xtile, ytile)
    
    @staticmethod
    def xtile2lon(x: int, level: int):
        """瓦片编号转经度
        # TODO:整理
        """
        return (x / math.pow(2.0, level)) * 360.0 - 180
    
    @staticmethod
    def ytile2lat(y: int, level: int):
        """瓦片编号转纬度
        # TODO:整理
        """
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2.0 ** level))))   

    def tile_path(self, x, y, z):
        path, filename = TileNameFormat.name_format(x, y, z, self.named_type)
        path = os.path.join(self.map_path, path)
        os.makedirs(path, exist_ok=True)
        path = os.path.join(path, f'{filename}.png')
        return path

    def xytile2lonlatbounds(self, x, y, level):
        """瓦片编号转经纬度界限"""

        lonmin = self.xtile2lon(x, level)
        lonmax = self.xtile2lon(x+1, level)
        latmin = self.ytile2lat(y+1, level)
        latmax = self.ytile2lat(y, level)

        return (lonmin, latmin, lonmax, latmax)
    
    def tile_cut(self, 
                 level: int, 
                 tile_bounds: tuple,
                 map_bounds: tuple,
                 lon_resolution: float, 
                 lat_resolution: float):
        
        """指定等级下切片
        Args:
            level: (int) 瓦片等级
            tile_bounds: (tuple) 瓦片编号区域
                         ex: (minx, miny, maxx, maxy)
            map_bounds: (tuple) 地图经纬度区域
                        ex: (minlon, minlat, maxlon, maxlat)
            lon_resolution: (float) 经度分辨率
            lat_resolution: (float) 纬度分辨率
        """        

        logger.debug(f'瓦片级别: {level}')
        logger.debug(f'地图bounds: {map_bounds}')

        for x in range(tile_bounds[0], tile_bounds[2]+1):
            for y in range(tile_bounds[1], tile_bounds[3]+1):

                logger.debug(f' x, y : {(x, y)}')

                tile_lonlat_bounds = self.xytile2lonlatbounds(x, y, level)

                logger.debug(f'tile_lonlat_bounds : {tile_lonlat_bounds}')
                
                # 切片与图像的交集
                tilebox = box(*tile_lonlat_bounds)
                imagebox = box(*map_bounds)
                intersect = tilebox.intersection(imagebox)
                inter_bounds = intersect.bounds

                logger.debug(f"交集区域: {intersect}")
                logger.debug(f"交集bounds: {inter_bounds}")

                tile_lon_resolution = resolution(tile_lonlat_bounds[0], tile_lonlat_bounds[2], 256)
                tile_lat_resolution = resolution(tile_lonlat_bounds[1], tile_lonlat_bounds[3], 256)

                xoff = int(pixel_num(inter_bounds[0], map_bounds[0], lon_resolution))
                yoff = int(pixel_num(inter_bounds[3], map_bounds[3], lat_resolution))

                xsize = int(pixel_num(inter_bounds[2], inter_bounds[0], lon_resolution))
                ysize = int(pixel_num(inter_bounds[3], inter_bounds[1], lat_resolution))

                buf_xsize = math.ceil(pixel_num(inter_bounds[2], inter_bounds[0], tile_lon_resolution))
                buf_ysize = math.ceil(pixel_num(inter_bounds[3], inter_bounds[1], tile_lat_resolution))

                img_xoff = int(pixel_num(tile_lonlat_bounds[0], inter_bounds[0], tile_lon_resolution))
                img_yoff = int(pixel_num(tile_lonlat_bounds[3], inter_bounds[3], tile_lat_resolution))

                img_xoff = img_xoff if img_xoff > 0 else 0
                img_yoff = img_yoff if img_yoff > 0 else 0

                logger.debug(f'read 参数: {(xoff, yoff, xsize, ysize, buf_xsize, buf_ysize)}')

                datas = self.readdata(xoff, yoff, xsize, ysize, buf_xsize, buf_ysize)

                path = self.tile_path(x, y, level)
            
                self.savepng(datas, path, img_xoff, img_yoff,buf_xsize, buf_ysize)
  
    def readdata(self, xoff, yoff, xsize, ysize, buf_xsize, buf_ysize):
        """读取每个波段的数据"""
        datas = []
        for i in range(1, self.map.rastercount+1):
            data = self.map.dataset.GetRasterBand(i).ReadRaster(xoff, yoff, xsize, ysize, buf_xsize, buf_ysize)
            datas.append(data)
 
        return datas
    
    def savepng(self, datas, path, xoff, yoff, xsize, ysize):
        """保存为png"""
        
        def callback(progress: float, b, data):
            """CreateCopy 回调函数
            progress: 进度
            b: don't know
            data: CreateCopy callback_data 参数
            """
            logger.debug(f"Create file: {data.get('path')} progress: {progress*100}% ...")
        

        mem_driver = gdal.GetDriverByName("MEM")
        msmds = mem_driver.Create("msmDS", 256, 256, self.map.rastercount)

        for i in range(len(datas)):
            msmds.GetRasterBand(i+1).WriteRaster(xoff, yoff, xsize, ysize, datas[i])

        png_driver = gdal.GetDriverByName("PNG")
        pngds = png_driver.CreateCopy(path, msmds, True, callback=callback, 
                                      callback_data={"path": path})

        return pngds
    
    def map_bounds(self):
        polygon: Polygon = self.map.get_geosrs_region()
        return polygon.bounds
    
    def tile_bounds(self, level):
        map_bounds = self.map_bounds()
        lu_xytile = self.lonlat2xytile(Point(map_bounds[0], map_bounds[3]), level)
        rl_xytile = self.lonlat2xytile(Point(map_bounds[2], map_bounds[1]), level)
        tile_bounds = (lu_xytile[0], lu_xytile[1], rl_xytile[0], rl_xytile[1])
        return tile_bounds


    def run(self):
        logger.info('cutting start ...'.center(100, '*'))
        
        # 确保 Pseudo-Mercator 投影
        assert self.map.projection.GetAttrValue('PROJCS') == 'WGS 84 / Pseudo-Mercator'

        logger.debug(f'rastercount: {self.map.rastercount}')

        map_bounds = self.map_bounds()
        polygon = box(*map_bounds)
        
        logger.debug(f"polygon: {polygon}")
        
        lon_resolution  = resolution(map_bounds[0], map_bounds[2], self.map.xsize)
        lat_resolution  = resolution(map_bounds[1], map_bounds[3], self.map.ysize)

        logger.debug(f'经纬度分辨率: {(lon_resolution, lat_resolution)}')

        for z in range(self.minlevel, self.maxlevel+1):

            logger.info(f'cutting level: {z} ...'.center(100, '*'))
            tile_bounds = self.tile_bounds(z)
            self.tile_cut(z, tile_bounds, map_bounds, lon_resolution, lat_resolution)
            logger.info(f'cutting level: {z} end'.center(100, '*'))
        
        logger.info('cutting end ...'.center(100, '*'))

    def test(self):
        self.run()


"""谷歌地图切片服务

任意坐标系tif -> WGS84(Pseudo-Mercator) -> 谷歌地图瓦片

"""
class GoogleMapTilerService(MapTilerService):
    pass


"""高德地图切片服务

任意坐标系tif -> WGS84(Pseudo-Mercator) -> 高德地图瓦片

"""
class AMapTilerService(MapTilerService):

    def map_bounds(self):

        polygon: Polygon = self.map.get_geosrs_region()
        polygon: Polygon = polygon_wgs84togcj02(polygon) # wgs84 转 gcj02

        return polygon.bounds





def get_service_cls(type: int):
    if type == TileServiceDefine.amap:
        return AMapTilerService
    elif type == TileServiceDefine.google:
        return GoogleMapTilerService
    else:
        raise Exception(f"This slice service type cannot exist: {type}")