import re
from flask import jsonify


class AuthValidation:
    """
    Validation of authentication data (login).
    Returns None if everything is OK, otherwise tuple (response, status_code).
    """

    EMAIL_REGEX = r"^[\w\.+-]+@[\w\.-]+\.\w+$"  # dozvoljen i "+" (npr. ime+igrac@gmail.com)
    MAX_EMAIL_LENGTH = 120
    MAX_PASSWORD_LENGTH = 128

    @staticmethod
    def validate_login_data(data: dict):
        """
        Login: only checks if the email and password have been sent and are in the correct form.
        """
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Request body must be JSON"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        if not isinstance(email, str) or not isinstance(password, str):
            return jsonify({"message": "Email and password must be text"}), 400

        email = email.strip()
        if len(email) > AuthValidation.MAX_EMAIL_LENGTH or not re.match(AuthValidation.EMAIL_REGEX, email):
            return jsonify({"message": "Invalid email format"}), 400

        if len(password) > AuthValidation.MAX_PASSWORD_LENGTH:
            return jsonify({"message": "Password is too long"}), 400

        return None