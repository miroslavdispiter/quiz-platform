from app import create_app
from app.config import Config

# The app is created only here, inside "if __name__ == '__main__'".
# On Windows every new process (quiz processing) imports this file again,
# and without this check every process would start the whole Flask server again.
if __name__ == "__main__":
    app = create_app()
    print(f"Quiz Service started on port {Config.PORT}")
    # 127.0.0.1 -> reachable only from this computer (the main server), not from the network
    app.run(host="127.0.0.1", port=Config.PORT, debug=True)
