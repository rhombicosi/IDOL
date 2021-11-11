
[![License](https://img.shields.io/github/license/rhombicosi/molp_project)](LICENSE)
![Code size](https://img.shields.io/github/languages/code-size/rhombicosi/Idol)
## **Web Service Idol description**
Web Service Idol is a tool for generating Chebyshev scalarization to solve multiobjective linear optimization problems.

As of now Idol accepts exclusively Gurobi multiobjective .lp format (see Gurobi lp format [documentation](https://www.gurobi.com/documentation/9.0/refman/lp_format.html#format:LP) )and returns scalarized problem as an .lp file.

User is able to control Chebyshev scalarization output by changing weights and reference parameters.
Idol accepts weights and reference points in form of a .txt files. Parameter values should be provided as a space separated array inside txt file.
File may contain several sets of parameters that are separated by a new line.

Chebyshev scalarization is generated for all sets of parameters and provided for download as a zip file on the main Problem page.

## **Development stack**

* Python 3.8
* Django 3.1
* Redis 3.5
* Celery 5.1
* PostgreSQL 12

The project uses Amazon S3 cloud to store files.

As a modelling and optimization tool Idol uses open-source Python MIP and [CBC solver](https://github.com/coin-or/Cbc).

## **Running project on Ubuntu 20.04**

### **Start Idol web service**

1.  Install Python 3.8.10 if not installed
1.  Install python3.8-venv
1.  Create and activate virtual environment 
    1.  python -m venv /path/to/new/virtual/environment
    1.  environment\Scripts\activate.bat (Windows) or . environment/bin/activate (Ubuntu)
1.  Install psycopg2 dependencies 
    1. sudo apt install python3-dev libpq-dev
1.  Install dependencies:
    1.  pip install -r requirements.txt
1.  Get inside the project directory "molp_project" and perform database migrations
    1.  python manage.py makemigrations
    1.  python manage.py migrate
1.  Start development server
    1.  python manage.py runserver
    
Application is available at http://127.0.0.1:8000/

### **PostgreSQL-12 setup**

1.  Install PostgreSQL
    1. sudo apt install postgresql postgresql-contrib
1.  Create database and databse user
    1.  sudo -u postgres psql
    1.  CREATE DATABASE \<database_name>;
    1.  CREATE USER \<user_name> WITH PASSWORD '\<password>';
    1.  GRANT ALL PRIVILEGES ON DATABASE \<database_name> TO \<user_name>;
    1.  \q
1.  Start service
    1.  sudo service postgresql start

### **Redis**

1. Install Redis the latest version
    1. sudo apt install redis
1. Start Redis server
    1. sudo redis-server

### **Celery**

1. Activate virtual environment
1. Go to the project directory
    1. cd /path/to/project/molp_project
    
1.  Start a new Celery worker with this command
    1.  celery -A molp_project worker --loglevel=info

Now application is ready to accept scalarization tasks.

1. Start Celery beat
    1.   celery -A molp_project beat -l INFO 

Now application is ready to run scheduled tasks.

### **Amazon S3**

Follow the [guide](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/) in order to create S3 Bucket for storing django files.

### **.env file**

Web service environment-specific paramters should be stored in .env file. 

Create .env file in the root of the project directory. .env file template is in file .env_example.


