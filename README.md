# Web Service and Cloud Based - 2024 February
The project is structured as follows. 

> - wscb
>   - docker-compose.yml
>   - README.md
>   - Authentication_Service
>       - app.py
>       - models.py
>       - mysql_config.py
>       - utils.py
>       - Dockerfile
>       - wait-for-it.sh
>       - requirements.txt
>   - Url_Shorten_Service
>       - app.py
>       - models.py
>       - mysql_config.py
>       - utils.py
>       - Dockerfile
>       - wait-for-it.sh
>       - requirements.txt
>   - mysql
>     - Dockerfile
>     - init_db.sql
>   - test
>     - A bunch of test scripts of Canvas
>   - docs
>     - A bunch of assignment descriptions of Canvas
>     - **Report for each assignment**
>   - deprecate
>     - Codes no longer used


#  Container Virtualization

This part is about to start two Flask applications (Authentication_Service and Url_Shorten_Service) and MySQL database containers using Docker Compose and let the containers to communicate with database and the database data to persist.

## How to Run Demo with Docker Compose

 Navigate to the project directory (that has docker-compose.yml there )and execute the following command:

```dockerfile
docker-compose up -d
```

![image-20240224174930421](/Users/rr/Library/Application Support/typora-user-images/image-20240224174930421.png)

```dockerfile
docker ps
```

![image-20240224175148571](/Users/rr/Library/Application Support/typora-user-images/image-20240224175148571.png)

```
docker logs <url_shorten_container_id>
```

![image-20240224175506806](/Users/rr/Library/Application Support/typora-user-images/image-20240224175506806.png)

By checking the container logs, you can see that the url shorten service has been started on port 5001 (which we specified). 

Inside the green box, it shows that we used the *wait-for-it.sh* script before running the python command to start the flask application. The reason for using this third-party wait script in the startup command of the Flask app is to **wait for the database port to become available and then start flask application**.

> You can get wait-for-it.sh by executing this on command line:
>
> wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh

Similarly you can see authentication service has been started on port 5002 (which we speicified).

![image-20240224180245803](/Users/rr/Library/Application Support/typora-user-images/image-20240224180245803.png)

You can also check logs of MySQL database and see the mysql starts on port 3306. Note that this port can only be accessed within the containers (can only access by URL_shorten_service_container and Authentication_service_container).

![image-20240224180543026](/Users/rr/Library/Application Support/typora-user-images/image-20240224180543026.png)

You can use Postman to test by send request to http://0.0.0.0:5001 (url shorten service) and http://0.0.0.0:5002 (identity authentication service)

<img src="/Users/rr/Library/Application Support/typora-user-images/image-20240224180744021.png" alt="image-20240224180744021" style="zoom: 33%;" />

<img src="/Users/rr/Library/Application Support/typora-user-images/image-20240224180854707.png" alt="image-20240224180854707" style="zoom: 33%;" />

To remove the containers started by docker-compose up, you can use

```dockerfile
docker-compose down
```

![image-20240224181202071](/Users/rr/Library/Application Support/typora-user-images/image-20240224181202071.png)

