from flask import Blueprint, jsonify, request
from app.Services.AuthService import AuthService, AuthResult
from app.Domain.models.User import User
from app.WebAPI.validation.AuthValidation import AuthValidation

auth_bp = Blueprint("auth", __name__)
authService = AuthService()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    error = AuthValidation.validate_login_data(data)
    if error:
        return error

    email = data["email"].strip()
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    result, token = authService.login(user, password)

    if result == AuthResult.BLOCKED:
        return jsonify({"message": "Account is temporarily blocked"}), 403

    if result == AuthResult.INVALID_CREDENTIALS:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify(access_token=token), 200
