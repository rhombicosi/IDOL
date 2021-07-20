## **Web Service Idol description**
Web Service Idol is a tool for generating Chebyshev scalarization to solve multiobjective linear optimization problems.

As of now Idol accepts exclusively Gurobi multiobjective .lp format (see Gurobi lp format documentation https://www.gurobi.com/documentation/9.0/refman/lp_format.html#format:LP) and returns scalarized problem as an .lp file.

User is able to control Chebyshev scalarization output by changing weights and reference points parameters.
Idol accepts weights and reference points in form of a .txt files. Parameter values should be provided as a space separated array inside txt file.
File may contain several sets of parameters that are separated by a new line.

Chebyshev scalarization is generated for all sets of parameters and provided for download as a zip file on the main Problem page.

## **Development stack**
Service is written in Python 3.8.10 and based on the Django 3.1 web framework. 

User data is stored in built-in SQLite database. AWS Cloud Storage (S3) S3 cloud as a files storage.

As a modelling and optimization tool Idol uses open-source Python MIP and CBC solver(https://github.com/coin-or/Cbc).

## **Running project**
1.  Create virtual environment using pip or conda
    1.  conda create --name molp_env python=3.7
    1.  conda activate molp_env
1.  When environment is activated install required packages
    1.  conda install django
1.  Get inside the project directory "molp_project" and perform database migrations
    1.  python manage.py makemigrations
    1.  python manage.py migrate
1.  Now project is ready to start using command
    1.  python manage.py runserver
    
Application is available at http://127.0.0.1:8000/
