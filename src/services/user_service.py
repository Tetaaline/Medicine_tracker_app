#!/usr/bin/python3
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
USERS_FILE = BASE_DIR / "users.txt"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class FileRepoBase:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    def ensure_parent(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)


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

    def user_exists(self, username_or_email):
        return self.get_user(username_or_email) is not None

    def authenticate(self, username_or_email, password):
        u = self.get_user(username_or_email)
        if not u:
            return None
        if u["password_hash"] == _hash(password):
            return u
        return None

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


# instantiate and expose module-level API for backward compatibility
_repo = UserRepository(USERS_FILE)


def save_user(username, password, name, email, role, org=""):
    return _repo.save_user(username, password, name, email, role, org)

