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
from osgeo import gdal, osr
from tilemap.utils.shape import Point, Polygon

class TifMap:

    def __init__(self, path):
        self.__path = path
        self.__dataset = gdal.Open(self.__path)
    
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
        return geosrs
    
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
        return Point(*coords[-2:-4:-1])
    
    def get_region(self):
        """获取

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
        """获取地图经纬度区域

        Returns:
            [Polygon]: 区域模型
        """        
        geosrs_points = (self.geo2lonlat(p) for p in self.get_region().points)

        return Polygon(*geosrs_points)
        
