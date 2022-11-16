import socketio

if __name__ == '__main__':
    # create a Socket.IO server
    sio = socketio.Server(async_mode='eventlet')

    app = socketio.WSGIApp(sio)
    import eventlet

    @sio.event
    def connect(sid, environ, auth):
        print('connect ', sid)
        print('auth ', auth)

    @sio.on('register_skill')
    def register_skill(sid, data):
        print('register_skill ', data)
        sio.emit('task', {'task_id': 1, 'data': 'Hello World!'})

    @sio.on('results')
    def results(sid, data):
        print('new results ', data)

    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 4852)), app)

