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
