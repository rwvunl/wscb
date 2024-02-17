# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /docker-image

COPY requirements.txt /docker-image

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]