# -*- encoding: utf-8 -*-
'''
@File    :   tifmap.py
@Time    :   2021/12/03 12:59:27
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib
import math
import logging
from math import pi
from osgeo import gdal, osr, gdalconst
from tilemap.utils.shape import Point, Polygon
from tilemap.conf.setting import Setting

logger = logging.getLogger(__name__)

gdal.AllRegister()

class TifMap:

    def __init__(self, path):
        self.__path = path
        self.__dataset = gdal.Open(self.__path)

        # self.__dataset.BuildOverviews(overviewlist=[2, 4 ,8, 16, 32, 64, 128, 256])

    @property
    def rastercount(self):
        return self.__dataset.RasterCount
    
    @property
    def ysize(self):
        return self.__dataset.RasterYSize
    
    @property
    def xsize(self):
        return self.__dataset.RasterXSize
    
    @property
    def geo_transform(self):
        """栅格数据六参数
        [0]: 左上角经度
        [1]: 经度方向分辨率
        [2]: 经度方向旋转角度
        [3]: 左上角纬度
        [4]: 纬度方向旋转角度
        [5]: 纬度方向分辨率(负值)
        """
        return self.__dataset.GetGeoTransform()
    
    @property
    def projection(self):
        """投影坐标系"""
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(self.__dataset.GetProjection())
        return prosrs
    
    @property
    def geogcs(self):
        """获取地理坐标系"""        
        geosrs = self.projection.CloneGeogCS()
        geosrs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 纬经度 -> 经纬度
        return geosrs
    
    @property
    def dataset(self):
        return self.__dataset
    
    @dataset.setter
    def dataset(self, value):
        self.__dataset = value

    def is_geographic(self):
        """地理坐标系"""
        return bool(self.projection.IsGeographic())
    
    def is_geocentric(self):
        """地心坐标系"""
        return bool(self.projection.IsGeocentric())
    
    def is_projected(self):
        """投影参考系"""
        return bool(self.projection.IsProjected())
    
    def xy2geo(self, x, y):
        """行列坐标转实际经纬度(根据具体参考系转化为投影坐标系和地理坐标系)

        Args:
            x (int): 列
            y (int): 行

        Returns:
            [tuple]: (经度, 纬度)
        """        
     
        trans = self.geo_transform
        px = trans[0] + x * trans[1] + y * trans[2]
        py = trans[3] + x * trans[4] + y * trans[5]
        return Point(px, py)
    
    def geo2lonlat(self, point: Point):
        """将投影坐标转化为地理坐标(具体的投影坐标系由给定数据确定)

        Args:
            point (Point): 点模型

        Returns:
            [Point]: 点模型
        """        
        # 坐标转化 (投影 -> 地理坐标系)
        ct = osr.CoordinateTransformation(self.projection, 
                                          self.geogcs)
        if not ct:
            raise Exception('无法建立坐标系转换关系')

        coords = ct.TransformPoint(point.x, point.y)
        # [纬度, 经度]
        # TODO: 经纬度数据顺序问题: https://www.osgeo.cn/gdal/tutorials/osr_api_tut.html
        return Point(*coords)
    
    def get_region(self):
        """获取区域(顺时针)

        Returns:
            [Polygon]: 区域模型
        """        
        points = ((0, 0), 
                  (self.xsize, 0), 
                  (self.xsize, self.ysize), 
                  (0, self.ysize))

        geo_points = (self.xy2geo(*p) for p in points)
        
        return Polygon(*geo_points)
    
    def get_geosrs_region(self):
        """获取地图经纬度区域(顺时针)

        Returns:
            [Polygon]: 区域模型
        """        
        geosrs_points = [self.geo2lonlat(p) for p in self.get_region().points]

        return Polygon(*geosrs_points)
    
    def reprojection_from_epsg(self, epsg: int, file: str):
        """重投影"""
        
        def callback(progress: float, b, data):
            """CreateCopy 回调函数
            progress: 进度
            b: don't know
            data: CreateCopy callback_data 参数
            """
            logger.debug(f"Create file: {data.get('path')} progress: {progress*100}% ...")

        target = osr.SpatialReference()
        target.SetProjCS('WGS 84 / Pseudo-Mercator') # 设置投影系统名称
        target.SetWellKnownGeogCS('WGS84') # 设置地理坐标系统
        target.ImportFromEPSG(epsg) # 定义投影坐标系
        
        """重采样方法
        GRA_NearestNeighbour 选取最邻近的像元
        GRA_Bilinear         邻近4个像元加权平均
        GRA_Cubic            邻近的16个像元平均
        GRA_CubicSpline      16个像元的三次B样条
        GRA_Lanczos          36个像元Lanczos窗口
        GRA_Average          求均值
        GRA_Mode             出现频率最多的像元值
        """
        webMercatorDs  = gdal.AutoCreateWarpedVRT(self.dataset, 
                                                  None, 
                                                  target.ExportToWkt(), 
                                                  gdalconst.GRA_Bilinear)
        dataset = gdal.GetDriverByName("GTiff").CreateCopy(
                file, webMercatorDs, options=["TILED=YES", "COMPRESS={0}".format('LZW')],
                callback=callback, callback_data={"path": file}
            )
        return dataset
    

def wgs84togcj02(lon, lat, semi_major=Setting.SEMI_MAJOR, ee=Setting.EE):
    """wgs84 地理坐标转 火星坐标
    # TODO:整理
    """
    def is_china(lon, lat):
        """判断中国境内"""
        return (lon > 73.66 and lon < 135.05 and lat > 3.86 and lat < 53.55)

    def transformlonlat(lon, lat):

        lon = lon-105.0
        lat = lat-35.0

        ret_lng = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
        ret_lng += (20.0 * math.sin(6.0 * lon * pi) + 20.0 *  math.sin(2.0 * lon * pi)) * 2.0 / 3.0
        ret_lng += (20.0 * math.sin(lon * pi) + 40.0 * math.sin(lon / 3.0 * pi)) * 2.0 / 3.0
        ret_lng += (150.0 * math.sin(lon / 12.0 * pi) + 300.0 * math.sin(lon / 30.0 * pi)) * 2.0 / 3.0

        ret_lat = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
        ret_lat += (20.0 * math.sin(6.0 * lon * pi) + 20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
        ret_lat += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret_lat += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0

        return ret_lng, ret_lat

    if not is_china(lon, lat):
        return lon, lat
    
    dlng, dlat = transformlonlat(lon, lat)

    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((semi_major * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (semi_major / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lon + dlng

    return mglng, mglat
  
def point_wgs84togcj02(point: Point, semi_major=Setting.SEMI_MAJOR, ee=Setting.EE):

    lon, lat = wgs84togcj02(point.x, point.y, semi_major, ee)

    return Point(lon, lat)

def polygon_wgs84togcj02(polygon: Polygon, semi_major=Setting.SEMI_MAJOR, ee=Setting.EE):

    points = [point_wgs84togcj02(p, semi_major, ee) for p in polygon.points]

    return Polygon(*points)