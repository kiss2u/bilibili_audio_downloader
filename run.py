from app import create_app
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

if __name__ == '__main__':
    app = create_app()
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()
