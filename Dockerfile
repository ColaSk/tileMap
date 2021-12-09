FROM ubuntu:20.04

# 当遇到Configuring tzdata 交互时会卡住，因此设置为非交互式
ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 TZ=Asia/Shanghai

VOLUME ["/docker_codes"]
WORKDIR /docker_codes

COPY ./mirrors /mirrors

RUN apt update && apt upgrade -y && \
    apt install python3-pip -y &&\
    apt-get install g++ -y &&\
    apt install -y libpq-dev&&\
    apt install -y gdal-bin=3.0.4+dfsg-1build3 &&\
    apt install -y libgdal-dev=3.0.4+dfsg-1build3

RUN pip3 install -r /mirrors/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir