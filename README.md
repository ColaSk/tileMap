# 瓦片切图

## 安装库
```
sudo apt install libpq-dev
sudo apt install gdal-bin=3.0.4+dfsg-1build3
sudo apt install libgdal-dev=3.0.4+dfsg-1build3

gdalinfo --version

# 设置setuptools: 对use_2to3 的支持58已经删除
pip install setuptools<58.0.0

# 此处版本号与gdalinfo --version一致
pip install gdal==3.0.4

```

## WKT解析
- WKT 空间参考系的统一表示方法

## 坐标系

### 地理坐标系
- 经度纬度
  
- 原始坐标系(地心坐标系)
  - WGS84\CGCS2000
- 加密坐标系
  - GCJ02(火星坐标系)\BD09

### 投影坐标系
- Pseudo-Mercator\UTM\BD09MC