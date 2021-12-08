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
from posixpath import join
import shutil
import numpy
import os
from osgeo import gdal, osr, gdalconst
from tilemap.map.tifmap import TifMap
from tilemap.utils.shape import Point, Polygon, box
from tilemap.utils.utils import resolution, pixel_num
from tilemap.conf.setting import TileNameFormat

# 设定Imagine风格的pyramids
gdal.SetConfigOption('HFA_USE_RRD', 'YES')

logger = logging.getLogger(__name__)



# here put the import lib
class MapTilerService(object):

    def __init__(self, 
                 map:TifMap, 
                map_path: str = './', 
                named_type=TileNameFormat.xyz, 
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

        datas = []
        for i in range(1, self.map.rastercount+1):
            data = self.map.dataset.GetRasterBand(i).ReadRaster(xoff, yoff, xsize, ysize, buf_xsize, buf_ysize)
            # logger.debug(data)
            datas.append(data)
        # datas = numpy.concatenate(datas)
        
        return datas
    
    def savepng(self, datas, path, xoff, yoff, xsize, ysize):

        memDriver = gdal.GetDriverByName("MEM")
        msmDS = memDriver.Create("msmDS", 256, 256, self.map.rastercount)

        for i in range(len(datas)):
            msmDS.GetRasterBand(i+1).WriteRaster(xoff, yoff, xsize, ysize, datas[i])

        pngDriver = gdal.GetDriverByName("PNG")
        pngDs = pngDriver.CreateCopy(path, msmDS)
        return pngDs

    def run(self):
        # 确保 Pseudo-Mercator 投影
        assert self.map.projection.GetAttrValue('PROJCS') == 'WGS 84 / Pseudo-Mercator'

        logger.debug(f'rastercount: {self.map.rastercount}')
        polygon: Polygon = self.map.get_geosrs_region()
        map_bounds = polygon.bounds
        
        logger.debug(f"polygon: {polygon}")
        
        x_pixel_resolution  = resolution(map_bounds[0], map_bounds[2], self.map.xsize)
        y_pixel_resolution  = resolution(map_bounds[1], map_bounds[3], self.map.ysize)

        logger.debug(f'经纬度分辨率: {(x_pixel_resolution, y_pixel_resolution)}')

        for z in range(self.minlevel, self.maxlevel+1):

            # Tile No. in upper right corner
            ur_tile_n = self.lonlat2xytile(polygon.indexpoint(1), z)

            # Tile No. at lower left corner
            ll_tile_n = self.lonlat2xytile(polygon.indexpoint(-1), z)

            tile_bounds = (ll_tile_n[0], ur_tile_n[1], ur_tile_n[0], ll_tile_n[1])

            self.tile_cut(z, tile_bounds, map_bounds, x_pixel_resolution, y_pixel_resolution)

    def test(self):
        self.run()
