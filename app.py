# -*- utf-8 -*-
import time
import uuid
from flask import Flask, render_template, request, make_response, jsonify
from flask_socketio import SocketIO
from celery import Celery
import eventlet
from flask_redis import FlaskRedis
eventlet.monkey_patch()

app = Flask(__name__)

app.config['BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_ACCEPT_CONTENT'] = ['json', 'pickle']
app.config['REDIS_URL'] = 'redis://localhost:6379/0'

socketio = SocketIO(app, async_mode='eventlet',message_queue=app.config['CELERY_RESULT_BACKEND'])
redis = FlaskRedis(app)

celery = Celery(app.name)
celery.conf.update(app.config)


@celery.task
def background_task(uid):
    sid = redis.get(uid)
    socketio.emit('info', {'data': 'Task starting ...', 'time': time.time() * 1000 },room=sid, namespace='/task')
    socketio.sleep(4)
    socketio.emit('info', {'data': 'Task running!', 'time': time.time() * 1000 }, room=sid, namespace='/task')
    socketio.sleep(5)
    socketio.emit('info', {'data': 'Task complete!', 'time': time.time()*1000 }, room=sid, namespace='/task')

@socketio.on('connect', namespace='/task')
def connect_host():
    sid = request.sid
    socketio.emit('hostadd', {'sid': sid}, room=sid, namespace='/task')

@app.route('/')
def index():
    if not request.cookies.get('host_uid', None):
        uid = uuid.uuid1().get_hex()
        response = make_response(render_template('index.html'))
        response.set_cookie('host_uid', uid)
        return response
    return render_template('index.html')

@app.route('/task')
def start_background_task():
    uid = request.cookies.get('host_uid')
    background_task.delay(uid)
    return 'Started'

@app.route('/setsid', methods=['POST'])
def set_uid():
    data = request.json
    uid = request.cookies.get('host_uid')
    redis.set(uid, data['sid'])
    redis.expire(uid, 3600 * 12)
    return jsonify({'success': True})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
