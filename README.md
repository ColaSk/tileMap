[toc]
# 瓦片切图

## 依赖库安装
### ubuntu

- C/C++依赖安装
```shell
# 暂时gdal依赖库为3.0.4, 因此指定版本安装
sudo apt install libpq-dev
sudo apt install gdal-bin=3.0.4+dfsg-1build3   # gdal 包
sudo apt install libgdal-dev=3.0.4+dfsg-1build3 # 开发包
```

- build
 
```shell

python setup.py build
```

- install

```
python setup.py install
```

### dockerfile

> Dockerfile: 基于ubuntu20.04 安装的依赖库
> gdal-Dockerfile: 基于gdal提供的docker镜像制作

## 用法

> tilemap [-h] [-i INPUT] [-o OUTPUT] [-t TYPE] [-min MINLEVEL] [-max MAXLEVEL] [-e LOGLEVEL] [-l LOGFILE]

### 参数

#### -h, --help 

> show this help message and exit

#### -i INPUT, --input INPUT

> path of the tif
> 需要切片的tif文件, 目前仅支持tif
> 支持相对路径与绝对路径

#### -o OUTPUT, --output OUTPUT

> output path
> 瓦片地图的输出路径
> 支持相对路径与绝对路径
> 默认: ./map

####   -t TYPE, --type TYPE  

> tile service type
> 切片服务类型
> 1: 支持高德地图, 通过gcj02 加密后的地图，默认
> 2：支持原生谷歌地图, 即未发生偏移的地图

####   -min MINLEVEL, --minlevel MINLEVEL

> Slice minimum level
> 瓦片图最小等级
> 默认: 0

####   -max MAXLEVEL, --maxlevel MAXLEVEL

> Slice maximum level
> 瓦片图最大等级
> 默认：21

####   -e LOGLEVEL, --loglevel LOGLEVEL

> Log level
> log的等级

####   -l LOGFILE, --logfile LOGFILE

> Log file path
> log输出文件的路径
> 默认：./tile.log

## 存在的问题

### setuptools 版本问题

> setuptools: 对use_2to3 的支持58已经删除, 因此需要保持setuptools<58.0.0

### gdal 版本问题

> python gdal 版本需要与 gdalinfo --version 版本保持一致
> 因此将gdal版本固定为3.0.4, 排除版本问题，就该项目而言，3.0.4可以满足所有要求
