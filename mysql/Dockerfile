# 使用官方 MySQL 镜像作为基础镜像
FROM mysql:8.0.26

ENV MYSQL_DATABASE=wscb_db \
    MYSQL_ROOT_PASSWORD=12345678

# 将初始化脚本添加到容器内的特定目录下
COPY init_db.sql /docker-entrypoint-initdb.d/


EXPOSE 3306