from flask import Blueprint, jsonify, request, send_from_directory, current_app
import os
from dataclasses import asdict
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.Services.UserService import UserService
from app.WebAPI.validation.UserValidation import UserValidation
from app.Domain.enums.role import Role
from app.Middleware.role_required import role_required
from app.Extensions.email_sender import EmailSender

user_bp = Blueprint("users", __name__)
user_service = UserService()
email_sender = EmailSender()

# CREATE USER
@user_bp.route("/register", methods=["POST"])
def create_user():
    data = request.get_json()

    error = UserValidation.validate_registration_data(data)
    if error:
        return error

    dto, status = user_service.create_user(data)
    if not dto or status != 201:
        return jsonify({"error": "User already exists or invalid data"}), 400

    token = create_access_token(
        identity=str(dto.id),
        additional_claims={"role": "PLAYER"}
    )

    return jsonify({
        "user": asdict(dto),
        "access_token": token
    }), 201

# DELETE USER
@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required(Role.ADMIN)
def delete_user(user_id):
    dto, status = user_service.delete_user(user_id)

    if not dto:
        return jsonify({"error": f"User with id {user_id} not found"}), status

    return jsonify(asdict(dto)), status

# GET CURRENT USER PROFILE
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        if user_id is None:
            return jsonify({"error": "Invalid token"}), 401
        
        dto, status = user_service.get_user_by_id(int(user_id))
        if dto is None:
            return jsonify({"error": "User not found"}), status
        
        return jsonify(asdict(dto)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE CURRENT USER PROFILE
@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        error = UserValidation.validate_profile_update_data(data)
        if error:
            return error
        
        dto, status = user_service.update_user_profile(user_id, data)
        if dto is None:
            return jsonify({"error": "Update failed"}), status
        return jsonify(asdict(dto)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/profile/image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    try:
        user_id = int(get_jwt_identity())
        if "profileImage" not in request.files:
            return jsonify({"error": "No file", "success": False}), 400
        file = request.files["profileImage"]
        result, status = user_service.upload_profile_image(user_id, file)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# CHANGE ROLE
@user_bp.route("/change_role/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(Role.ADMIN)
def change_user_role(user_id):
    data = request.get_json()

    error = UserValidation.validate_role_change(data)
    if error:
        return error

    new_role_val = data["role"]
    new_role = Role(new_role_val)

    dto, status = user_service.change_user_role(user_id, new_role)

    if not dto:
        return jsonify({"error": f"User with id {user_id} not found"}), status

    # SENDING MAIL
    try:
        user_email = dto.email
        full_name = f"{dto.first_name} {dto.last_name}"
        
        email_sender.send_role_change_email(
            to_email=user_email,
            new_role=new_role_val,
            full_name=full_name
        )
        print(f"Notification email sent to {user_email} for new role: {new_role_val}")
    except Exception as e:
        print(f"Failed to send role change email: {str(e)}")

    return jsonify(asdict(dto)), status

# GET BY ID
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    dto, status = user_service.get_user_by_id(user_id)

    if not dto:
        return jsonify({"error": f"User with id {user_id} not found"}), status

    return jsonify(asdict(dto)), status

# GET ALL USERS
@user_bp.route("/all", methods=["GET"])
@jwt_required()
@role_required(Role.ADMIN)
def get_all_users():
    dto, status = user_service.get_all_users()
    return jsonify(asdict(dto)), status

# UI DISPLAY FETCH
@user_bp.route("/profile-image/<int:user_id>", methods=["GET"])
def get_profile_image(user_id):
    dto, status = user_service.get_user_by_id(user_id)
    if not dto:
        return jsonify({"error": "User not found"}), status

    if not dto.profile_image:
        return jsonify({"error": "User has no profile image"}), 404

    file_path = dto.profile_image
    if not os.path.exists(file_path):
        return jsonify({"error": "Image file not found"}), 404

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        os.path.basename(file_path)
    )
