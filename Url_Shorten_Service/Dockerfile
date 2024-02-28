# syntax=docker/dockerfile:1

FROM python:3.9-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN apk add gcc
RUN apk add --no-cache libressl-dev musl-dev libffi-dev
RUN pip install --no-cache-dir cryptography
RUN apk del libressl-dev \
        musl-dev \
        libffi-dev


RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY . /app

EXPOSE 5001

COPY wait-for-it.sh /wait-for-it.sh

RUN apk add --no-cache bash

RUN chmod +x /wait-for-it.sh

CMD ["/wait-for-it.sh", "mysql-db:3306", "--", "python3", "-m" , "flask","--app" ,"app","run", "--host=0.0.0.0","--port=5001"]