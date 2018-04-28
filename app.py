# -*- utf-8 -*-
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from celery import Celery
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)

app.config['BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_ACCEPT_CONTENT'] = ['json', 'pickle']

socketio = SocketIO(app, async_mode='eventlet',message_queue=app.config['CELERY_RESULT_BACKEND'])

celery = Celery(app.name)
celery.conf.update(app.config)


@celery.task
def background_task(sid):
    socketio.emit('info', {'data': 'Task starting ...', 'time': time.time() * 1000 },room=sid, namespace='/task')
    time.sleep(4)
    socketio.emit('info', {'data': 'Task running!', 'time': time.time() * 1000 }, room=sid, namespace='/task')
    time.sleep(5)
    socketio.emit('info', {'data': 'Task complete!', 'time': time.time()*1000 }, room=sid, namespace='/task')

@socketio.on('connect', namespace='/task')
def connect_host():
    sid = request.sid
    socketio.emit('hostadd', {'sid': sid}, room=sid, namespace='/task')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/task')
def start_background_task():
    sid = request.cookies.get('sid')
    background_task.delay(sid)
    return 'Started'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
