import json
from pathlib import Path


USERS_FILE = Path("data/users_data.json")


def load_users():
    if not USERS_FILE.exists():
        return []

    try:
        with USERS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def validate_credentials(email, password):
    normalized_email = email.strip().lower()

    for user in load_users():
        if user.get("email") == normalized_email and user.get("password") == password:
            return user

    return None


def get_user_by_email(email):
    normalized_email = email.strip().lower()

    for user in load_users():
        if user.get("email") == normalized_email:
            return user

    return None
