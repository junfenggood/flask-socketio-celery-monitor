# flask-socketio-celery-monitor
use flask-socketio and celery monitor a bacground task

# usage
## start celery process
``` shell
celery worker -A app.celery -P eventlet -l info
```
## start flask
``` shell
python app.py
```
