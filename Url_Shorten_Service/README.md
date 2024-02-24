# URL Shorten Service
This project implements a URL shortening service using the Flask web framework in Python.
## Run the project
Navigate to the project directory  and execute the following command
```python
python -m flask --app app run
```
## Docker Image
- To build the image, navigate to the project directory and execute the following command
```dockerfile
docker build -f Dockerfile -t url_shorten_image . 
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