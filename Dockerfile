# tells the Docker builder what syntax to use while parsing the Dockerfile and the location of the Docker syntax file
# syntax=docker/dockerfile:1

# start by pulling the python image
FROM python:3.8-slim-buster

# switch working directory
WORKDIR /docker-image

# copy the requirements file into the image
COPY requirements.txt /docker-image

# install the dependencies and packages in the requirements file
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]