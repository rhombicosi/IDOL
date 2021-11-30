
[![License](https://img.shields.io/github/license/rhombicosi/molp_project)](LICENSE)
![Code size](https://img.shields.io/github/languages/code-size/rhombicosi/IDOL)
[![DOI](https://zenodo.org/badge/393465636.svg)](https://zenodo.org/badge/latestdoi/393465636)
## **IDOL web service description**
Web Service IDOL is a tool for generating Chebyshev scalarization to solve multiobjective linear optimization problems.

As of now IDOL accepts exclusively Gurobi multiobjective .lp format (see Gurobi lp format [documentation](https://www.gurobi.com/documentation/9.0/refman/lp_format.html#format:LP)) and returns scalarized problem as an .lp file.

User is able to control Chebyshev scalarization output by changing weights and reference parameters.
IDOL accepts weights and reference points in form of a .txt files. Parameter values should be provided as a space separated array inside txt file.
File may contain several sets of parameters that are separated by a new line.

Chebyshev scalarization is generated for all sets of parameters and provided for download as a zip file on the main Problem page.

## **Development stack**

* Python 3.8
* Django 3.1
* Redis 3.5
* Celery 5.1
* PostgreSQL 12

The project uses Amazon S3 cloud to store files.

As a modelling and optimization tool IDOL uses open-source Python MIP and [CBC solver](https://github.com/coin-or/Cbc).

## **Running project on Ubuntu 20.04**

### **PostgreSQL-12 setup**

-  Install PostgreSQL
```
    sudo apt install postgresql postgresql-contrib
```
-  Create database and database user
```
    sudo -u postgres psql
    CREATE DATABASE <database_name>;
    CREATE USER <user_name> WITH PASSWORD '<password>';
    GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <user_name>;
    \q
```
-  Start postgresql service
```
    sudo service postgresql start
```

### **Redis**

- Install Redis the latest version
```
    sudo apt install redis
```
- Start Redis server
```
    sudo redis-server
```

### **Amazon S3 storage**

Follow the [guide](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/) in order to create S3 Bucket for storing project files.

### **.env file**

Web service environment-specific paramters, e.g. database name, user and password, should be stored in .env file. 

Create .env file in the root of the project directory according to the template .env_example.

### **Start IDOL web service**

-  Install Python 3.8.10 if not installed
-  Install python3.8-venv
-  Create and activate virtual environment 
```
    python3 -m venv /path/to/new/virtual/environment
    . environment/bin/activate
```
-  Install psycopg2 dependencies
```
    sudo apt install python3-dev libpq-dev
```
-  Install dependencies:
```
    pip install -r requirements.txt
```
-  Perform database migrations
```
    python3 manage.py makemigrations
    python3 manage.py migrate
```
-  Start development server
```
    python3 manage.py runserver
```
    
Application is available at http://127.0.0.1:8000/

### **Celery**

- Activate virtual environment if it is not activated
- Go to the project directory
```
    cd /path/to/project/molp_project
```    
- Start a new Celery worker
```
    celery -A molp_project worker --loglevel=info
```

Now application is ready to accept scalarization tasks.

- Start Celery beat
```
    celery -A molp_project beat -l INFO
```

Now application is ready to run scheduled tasks.

### **Running unit tests**

- Activate virtual environment if it is not activated
- Inside the project directory run tests with the command
```
    python3 manage.py test molp_app
```






