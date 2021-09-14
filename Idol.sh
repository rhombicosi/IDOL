#!/bin/bash
NAME="molp_project"
DJANGODIR=./
SOCKFILE=/path/to/your_project_name/run/gunicorn.sock
USER=your_name
GROUP=your_group
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=your_project.settings
DJANGO_WSGI_MODULE=project.wsgi
echo "Starting $NAME as `whoami`"
cd $DJANGODIR
source ../Env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec /Env/bin/activate/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=$SOCKFILE \
  --log-level=debug \
  --log-file=-