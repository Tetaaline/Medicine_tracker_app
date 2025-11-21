#!/usr/bin/python3
import hashlib
from datetime import datetime
from pathlib import Path

#This is to help define base directory and the path where all users data will be saved
BASE_DIR = Path(__file__).resolve().parents[1]
USERS_FILE = BASE_DIR / "users.txt"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class FileRepoBase:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    def ensure_parent(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

#The function that will help to save a new user in the created user.txt
class UserRepository(FileRepoBase):
    def save_user(self, username, password, name, email, role, org=""):
        self.ensure_parent()
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write("{}:{}:{}:{}:{}:{}:{}\n".format(
                username,
                _hash(password),
                name,
                email,
                role,
                org,
                datetime.now()
    ))

#The function that will select user's information by using username or email
    def get_user(self, username_or_email):
        if not self.file_path.exists():
            return None
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) >= 6:
                    u, pwd_hash, name, email, role, org = parts[:6]
                    if u == username_or_email or email == username_or_email:
                        return {"username": u, "password_hash": pwd_hash, "name": name, "email": email, "role": role, "org": org}
        return None
#This will check the username already exists
    def user_exists(self, username_or_email):
        return self.get_user(username_or_email) is not None

#This function will help to verify a user by use of hashed passwords 
    def authenticate(self, username_or_email, password):
        u = self.get_user(username_or_email)
        if not u:
            return None
        if u["password_hash"] == _hash(password):
            return u
        return None

#The function which displays list of doctors from file
    def list_doctors(self):
        results = []
        if not self.file_path.exists():
            return results
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) >= 6:
                    u, _, name, email, role, org = parts[:6]
                    if role == "doctor":
                        results.append({"username": u, "name": name, "org": org})
        return results


#This will create one shared UserRepository that the functions below will use
_repo = UserRepository(USERS_FILE)

#This will cover functions so that other files may use it easily
def save_user(username, password, name, email, role, org=""):
    return _repo.save_user(username, password, name, email, role, org)

def get_user(username_or_email):
    return _repo.get_user(username_or_email)


def user_exists(username_or_email):
    return _repo.user_exists(username_or_email)


def authenticate(username_or_email, password):
    return _repo.authenticate(username_or_email, password)


def list_doctors():
    return _repo.list_doctors()
