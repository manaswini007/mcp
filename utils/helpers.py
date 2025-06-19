
from .db_utils import db
from .constant import USERS_COLLECTION

def get_user_by_username(username: str):
    """Helper to get a user by username"""
    return db[USERS_COLLECTION].find_one({"username": username})

def validate_user_credentials(username: str, password: str):
    """Helper to check username & password"""
    return db[USERS_COLLECTION].find_one({"username": username, "password": password})
