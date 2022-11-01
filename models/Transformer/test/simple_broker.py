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

    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 4852)), app)

