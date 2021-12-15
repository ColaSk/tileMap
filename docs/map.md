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
- Pseudo-Mercator(EPSG 3857)\UTM\BD09MC


## 坐标系转化

当前(WGS 84 基准)
x, y -> 自身投影(UTM)
自身投影 -> epsg3857(Pseudo-Mercator)

-> 地理坐标系(WGS 84)

## EPSG

```
EPSG:4326	Geodetic coordinate system(地理坐标系)	WGS 84
EPSG:2437	Projected coordinate system(投影坐标系)	Beijing 1954 / 3-degree Gauss-Kruger CM 120E
```

## 高德地图
- 地理坐标系: GCJ02 准确的说GCJ02不属于坐标系，仅仅是坐标加密算法
- 投影坐标系：Pseudo-Mercator
  
### 问题
- 高德地图加密后如何进行的投影