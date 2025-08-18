from flask import session, jsonify
from .models import User

def get_user(email: str):
    return User.query.filter_by(email=email).first()

def get_user_by_id(id: int):
    return User.query.filter_by(id=id).first()

def is_auth():
    if "user_id" in session:
        if get_user_by_id(session["user_id"]):
            return True
    return False

def get_forbidden_msg():
    return "Not Authorized.", 403