import re
from datetime import datetime, date
from flask import jsonify

from app.Domain.enums.role import Role


class UserValidation:

    EMAIL_REGEX = r"^[\w\.+-]+@[\w\.-]+\.\w+$"  # dozvoljen i "+" (npr. ime+igrac@gmail.com)
    PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d).{6,}$"  # MIN 6 CHARACTERS, AT LEAST ONE LETTER AND NUMBER
    NAME_REGEX = r"^[A-Za-zČĆŽŠĐčćžšđ\s-]{2,50}$"
    GENDERS = ["male", "female", "other"]
    MIN_AGE = 12

    @staticmethod
    def _validate_date_of_birth(dob):
        """
        DATE OF BIRTH - zajednicka provera za registraciju i izmenu profila
        """
        try:
            if isinstance(dob, str):
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            elif not isinstance(dob, date):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid date_of_birth format, expected YYYY-MM-DD"}), 400

        today = date.today()
        if dob > today:
            return jsonify({"error": "Date of birth cannot be in the future"}), 400

        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < UserValidation.MIN_AGE:
            return jsonify({"error": f"User must be at least {UserValidation.MIN_AGE} years old"}), 400

        return None

    @staticmethod
    def validate_registration_data(data: dict):
        """
        USER REGISTRATION
        """
        required_fields = [
            "first_name", "last_name", "email", "password",
            "date_of_birth", "gender"
        ]

        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        # EMAIL
        email = data.get("email")
        if not re.match(UserValidation.EMAIL_REGEX, email):
            return jsonify({"error": "Invalid email format"}), 400

        # PASSWORD
        password = data.get("password")
        if not re.match(UserValidation.PASSWORD_REGEX, password):
            return jsonify({
                "error": "Password must have at least 6 characters and contain letters and digits"
            }), 400

        # NAME AND LAST NAME
        for field in ("first_name", "last_name"):
            if not re.match(UserValidation.NAME_REGEX, data.get(field)):
                return jsonify({"error": f"Invalid {field.replace('_', ' ')} format"}), 400

        # DATE OF BIRTH
        error = UserValidation._validate_date_of_birth(data.get("date_of_birth"))
        if error:
            return error

        # GENDER
        gender = data.get("gender").lower()
        if gender not in UserValidation.GENDERS:
            return jsonify({"error": f"Gender must be one of {UserValidation.GENDERS}"}), 400

        return None

    @staticmethod
    def validate_profile_update_data(data: dict):
        """
        UPDATE PROFILE
        """
        allowed = ("first_name", "last_name", "email", "password", "date_of_birth", "gender", "profile_image")
        if not any(f in data for f in allowed):
            return jsonify({"error": "No updatable fields provided"}), 400

        # EMAIL
        if "email" in data and data["email"] and not re.match(UserValidation.EMAIL_REGEX, data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # PASSWORD
        if "password" in data and data["password"]:
            if not re.match(UserValidation.PASSWORD_REGEX, data["password"]):
                return jsonify({"error": "Password must have at least 6 characters and contain letters and digits"}), 400

        # NAME AND LAST NAME
        for f in ["first_name", "last_name"]:
            if f in data and data[f] and not re.match(UserValidation.NAME_REGEX, data[f]):
                return jsonify({"error": f"Invalid {f.replace('_',' ')} format"}), 400

        # DATE OF BIRTH
        if "date_of_birth" in data and data["date_of_birth"]:
            error = UserValidation._validate_date_of_birth(data["date_of_birth"])
            if error:
                return error

        # GENDER
        if "gender" in data and data["gender"]:
            gender = data["gender"].lower()
            if gender not in UserValidation.GENDERS:
                return jsonify({"error": f"Gender must be one of {UserValidation.GENDERS}"}), 400

        return None

    @staticmethod
    def validate_role_change(data: dict):
        """
        CHANGE ROLE -> MODERATOR
        """
        new_role = data.get("role")
        if not new_role:
            return jsonify({"error": "Role is required"}), 400

        try:
            Role(new_role)
        except ValueError:
            return jsonify({"error": f"Invalid role. Allowed roles: {[r.value for r in Role]}"}), 400

        return None