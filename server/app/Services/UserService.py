import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime
from app.Database.UserRepository import UserRepository
from app.Domain.enums.role import Role
from app.Domain.models.User import User
from app.Extensions.bcrypt import bcrypt
from app.Domain.DTOs.UserDTO import UserDTO
from app.Domain.DTOs.UserSummaryDTO import UserSummaryDTO
from app.Domain.DTOs.UserListDTO import UserListDTO
from app.Domain.DTOs.UserCreatedDTO import UserCreatedDTO

class UserService:
    def __init__(self):
            self.repo = UserRepository()

    def create_user(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return None, 400

        if self.repo.get_by_email(email):
            return None, 409

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            email=email,
            password_hash=hashed_password,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            country=data.get("country"),
            street=data.get("street"),
            street_number=data.get("number"),
            role=Role.PLAYER,
            created_at=datetime.utcnow()
        )

        self.repo.create(user)
        return UserCreatedDTO.from_model(user), 201

    def delete_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)

        if not user:
            return None, 404

        deleted_dto = UserCreatedDTO.from_model(user)

        self.repo.delete(user_id)
        return deleted_dto, 200

    def update_user_profile(self, user_id: int, data):
        user = self.repo.get_by_id(user_id)

        if not user:
            return None, 404

        fields = ["first_name", "last_name", "email", "gender", "country", "street", "street_number", "profile_image"]
        for f in fields:
            if f in data and data[f]:
                setattr(user, f, data[f])

        if "date_of_birth" in data and data["date_of_birth"]:
            user.date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()

        if "password" in data and data["password"]:
            user.password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        self.repo.update(user)
        return UserDTO.from_model(user), 200

    def change_user_role(self, user_id: int, new_role: Role):
        user = self.repo.get_by_id(user_id)

        if not user:
            return None, 404

        user.role = new_role
        self.repo.update(user)

        return UserDTO.from_model(user), 200

    def get_user_by_id(self, user_id: int):
        user = self.repo.get_by_id(user_id)

        if not user:
            return None, 404

        return UserDTO.from_model(user), 200

    def get_all_users(self):
        users = self.repo.get_all()

        users = self.repo.get_all()
        user_summaries = [UserSummaryDTO.from_model(u) for u in users]
        dto = UserListDTO(count=len(user_summaries), users=user_summaries)
        return dto, 200
        
    def upload_profile_image(self, user_id: int, file):
        user = self.repo.get_by_id(user_id)
        if not user:
            return {"error": f"User {user_id} not found"}, 404

        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            return {"error": "Invalid file extension"}, 400

        filename = secure_filename(f"user_{user_id}.{ext}")
        folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        # LOCALLY FOR NOW
        file.save(filepath)

        user.profile_image = filepath
        self.repo.update(user)

        return {"message": "Profile image uploaded", "image_path": filepath}, 200