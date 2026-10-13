"""
Entry point for the Quiz Service:  python run.py

The app is created only inside main(). On Windows, multiprocessing starts new processes
with "spawn", which re-imports this module in every child process; keeping the startup
code under `if __name__ == "__main__"` stops the grading processes from starting Flask again.
"""

import logging

from app import create_app

logger = logging.getLogger("quiz_service")


def main() -> None:
    app = create_app()

    # TODO: create the ProcessPoolExecutor for asynchronous grading here and attach it to the app.

    logger.info("Quiz Service starting on http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])


if __name__ == "__main__":
    main()
