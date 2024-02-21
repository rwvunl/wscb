# Assignment 1: RESTFUL service
This project implements a URL shortening service using the Flask web framework in Python.
## Run the project
Navigate to the project directory  and execute the following command
```python
python -m flask --app app run
```
Flask will look for a module named `app` and run it as a Flask application. If everything is set up correctly, you should see the Flask development server start, and you can access your Flask application at the specified URL (usually `http://0.0.0.0:5000/` by default).
## Use Postman to test services
> Specifications for endpoints are provided in assignment report.
# Assignment 2: RESTful microservices architectures
## Two ways to run the project
### 1. Run python app.py on the command line
> Exactly the same as assignment 1
### 2. Run an image as a container 
- To build the image, navigate to the project directory and execute the following command
```dockerfile
docker build -t wscb-a2-image . 
```
- Note that we have pushed the image on docker hub, so you can also directly execute the following command
```dockerfile
docker pull ivywr/p4-wscb:wscb-a2-imagev5
```
- Then run an image as a container
```dockerfile
docker run -d -p <your_custom_port_number>:5001 <IMAGE ID>
```
## Use Postman to test services
> Specifications for endpoints are provided in assignment report.

Shorten url service: http://0.0.0.0:<your_custom_port_number>/

Authentication service: http://0.0.0.0:<your_custom_port_number>/users/