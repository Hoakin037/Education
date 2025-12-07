from api.model import UserInDB

fake_users_db = {}

def get_user(username: str):
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

def add_user(username: str, data: dict):
    fake_users_db[username] = dict