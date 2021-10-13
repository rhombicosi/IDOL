
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

## **Running project**

It is possible to run the Idol on Windows and Ubuntu operating systems.

1.  Install Python 3.8.10
1.  Create and activate virtual environment 
    1.  python -m venv /path/to/new/virtual/environment
    1.  environment\Scripts\activate.bat
1.  Install pip
1.  Install dependencies:
    1.  pip install -r requirements.txt
1.  Get inside the project directory "molp_project" and perform database migrations
    1.  python manage.py makemigrations
    1.  python manage.py migrate
1.  Start development server
    1.  python manage.py runserver
    
Application is available at http://127.0.0.1:8000/

## **Redis and Celery setup**
Redis and Celery are available only on Linux therefore Windows setup requires WSL2 and Ubuntu to be preinstalled.

### **Redis**

1. Install Redis the latest version
    1. wget http://download.redis.io/releases/redis-5.0.8.tar.gz
    1. tar xzf redis-6.2.4.tar.gz
    1. cd redis-6.2.4
    1. make
    
1. Create a configuration file (optional)
   1. The config file example 6379.conf can be found in the project root directory
    
1. Start the Redis server
    1. src/redis-server /path/to/conf/6379.conf

### **Celery**

1. Go to the project directory
    1. cd /mnt/c/Users/username/path/to/project/molp_project
    
1. Start a new Celery worker with this command
    1. celery -A molp_project worker --loglevel=info

Now application is ready to accept scalarization tasks.