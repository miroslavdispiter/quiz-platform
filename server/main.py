from app import create_app
from app.Extensions.socketio_ext import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="localhost", debug=True, port=5000, allow_unsafe_werkzeug=True)