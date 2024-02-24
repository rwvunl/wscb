# syntax=docker/dockerfile:1

# 阶段1：使用Python官方镜像作为构建环境
FROM python:3.9-slim AS builder
# 设置工作目录
WORKDIR /app
# 将依赖信息复制到容器中
COPY requirements.txt .
# 安装 Python 依赖项, 使用--no-cache-dir标志来减小镜像大小
RUN pip install --no-cache-dir -r requirements.txt

# 阶段2：运行应用程序
# 使用从builder阶段构建的轻量级基础镜像
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# 将Flask应用的代码复制到容器中
COPY . /app

EXPOSE 5001

CMD ["python3", "-m" , "flask","--app" ,"app","run", "--host=0.0.0.0","--port=5001"]