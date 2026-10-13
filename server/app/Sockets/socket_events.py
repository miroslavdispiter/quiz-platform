from flask_socketio import join_room
from flask_jwt_extended import decode_token
from app.Extensions.socketio_ext import socketio


@socketio.on("connect")
def handle_connect(auth):
    """
    The client connects with its JWT: io(URL, { auth: { token } }).
    Every user joins two "rooms":
      - his role ("ADMIN", "MODERATOR", "PLAYER") -> e.g. all admins get new quizzes
      - "user_<id>"                             -> e.g. only the author gets the review result
    Without a valid token the connection is refused.
    """
    token = auth.get("token") if isinstance(auth, dict) else None
    if not token:
        return False

    try:
        claims = decode_token(token)
    except Exception:
        return False

    join_room(claims["role"])
    join_room(f"user_{claims['sub']}")
