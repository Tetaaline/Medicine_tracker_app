import json
from datetime import datetime
from pathlib import Path
# Paths to the JSON files used as our lightweight “database”
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PAT_FILE = DATA_DIR / "patients.json"
MED_FILE = DATA_DIR / "medicines.json"
SCH_FILE = DATA_DIR / "schedules.json"

# Created JSONBased parent class  and other classes can inherit from this so we don't repeat storage logic everywhere

class JSONStorageBase:
    def __init__(self, file_path: Path, default_structure):
        self.file_path = Path(file_path)
        self.default_structure = default_structure
# def ensure method make sure the JSON file exists. If it's missing, we create it with an empty structure
    def ensure(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps(self.default_structure, indent=2))
#def load method read and return the current JSON content
    def load(self):
        self.ensure()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
# def save method writes updated data back to the JSON file
    def save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

#Created PatientRepository child class for JSONStorageBase that give details about patients information"
"""
 It handles all patient-related operations, plus cleanup of
    related medicines and schedules when a patient is deleted.
    Everything here acts like a tiny in-house database layer.
"""
class PatientRepository:
    def __init__(self, pat_fp: Path, med_fp: Path, sch_fp: Path):
        self.pat_store = JSONStorageBase(pat_fp, {"patients": []})
        self.med_store = JSONStorageBase(med_fp, {"medicines": []})
        self.sch_store = JSONStorageBase(sch_fp, {"schedules": []})

    def _ensure_files(self):
        self.pat_store.ensure()
        self.med_store.ensure()
        self.sch_store.ensure()

    def _load(self, store: JSONStorageBase):
        return store.load()

    def _save(self, store: JSONStorageBase, data):
        store.save(data)

    def list_patients(self, doctor_username):
        data = self._load(self.pat_store)
        return [p for p in data.get("patients", []) if p.get("doctor") == doctor_username]

    def search_patients(self, doctor_username, term):
        term = term.lower()
        return [p for p in self.list_patients(doctor_username)
                if term in p.get("name", "").lower() or term in p.get("id", "").lower()]

    def add_patient(self, doctor_username, patient_name):
        data = self._load(self.pat_store)
        new_id = f"P{int(datetime.now().timestamp())}"
        data["patients"].append({
            "id": new_id,
            "name": patient_name,
            "doctor": doctor_username,
            "user_username": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save(self.pat_store, data)
        return new_id
    """
        Only add a patient if they don’t already exist.
        This avoids duplicates when a patient logs in with the same name/username.
    """
    def add_patient_if_absent(self, doctor_username, patient_name, patient_username=""):
        data = self._load(self.pat_store)
        # If linked to an existing user, return that patient’s ID

        for p in data.get("patients", []):
            if patient_username and p.get("user_username") == patient_username:
                return p.get("id")
            # If same doctor already added this patient manually
        for p in data.get("patients", []):
            if p.get("doctor") == doctor_username and p.get("name") == patient_name:
                return p.get("id")
        pid = self.add_patient(doctor_username, patient_name)
        return pid


    def delete_patient(self, doctor_username, patient_id):
        pat = self._load(self.pat_store)
        before = len(pat.get("patients", []))
        pat["patients"] = [p for p in pat.get("patients", [])
                           if not (p.get("doctor") == doctor_username and p.get("id") == patient_id)]
        self._save(self.pat_store, pat)
        removed = before - len(pat["patients"])

        med = self._load(self.med_store)
        med["medicines"] = [m for m in med.get("medicines", []) if m.get("patient_id") != patient_id]
        self._save(self.med_store, med)

        sch = self._load(self.sch_store)
        sch["schedules"] = [s for s in sch.get("schedules", []) if s.get("patient_id") != patient_id]
        self._save(self.sch_store, sch)

        return removed > 0

    def get_patient_by_id(self, pid):
        data = self._load(self.pat_store)
        for p in data.get("patients", []):
            if p.get("id") == pid:
                return p
        return None

    def link_patient_user(self, pid, username):
        data = self._load(self.pat_store)
        updated = False
        for p in data.get("patients", []):
            if p.get("id") == pid:
                p["user_username"] = username
                updated = True
                break
        if updated:
            self._save(self.pat_store, data)
        return updated

    def get_patient_id_for_user(self, username):
        data = self._load(self.pat_store)
        for p in data.get("patients", []):
            if p.get("user_username") == username:
                return p.get("id")
        return None


# Instantiate repository and provide module-level API for backward compatibility
_repo = PatientRepository(PAT_FILE, MED_FILE, SCH_FILE)


def _ensure_files():
    return _repo._ensure_files()


def _load(fp):
    # keep function signature but delegate to appropriate store
    if Path(fp) == PAT_FILE:
        return _repo._load(_repo.pat_store)
    if Path(fp) == MED_FILE:
        return _repo._load(_repo.med_store)
    if Path(fp) == SCH_FILE:
        return _repo._load(_repo.sch_store)
    # fallback: load arbitrary path
    store = JSONStorageBase(Path(fp), {})
    return store.load()


def _save(fp, data):
    if Path(fp) == PAT_FILE:
        return _repo._save(_repo.pat_store, data)
    if Path(fp) == MED_FILE:
        return _repo._save(_repo.med_store, data)
    if Path(fp) == SCH_FILE:
        return _repo._save(_repo.sch_store, data)
    store = JSONStorageBase(Path(fp), {})
    return store.save(data)


def list_patients(doctor_username):
    return _repo.list_patients(doctor_username)


def search_patients(doctor_username, term):
    return _repo.search_patients(doctor_username, term)


def add_patient(doctor_username, patient_name):
    return _repo.add_patient(doctor_username, patient_name)


def add_patient_if_absent(doctor_username, patient_name, patient_username=""):
    return _repo.add_patient_if_absent(doctor_username, patient_name, patient_username)


def delete_patient(doctor_username, patient_id):
    return _repo.delete_patient(doctor_username, patient_id)


def get_patient_by_id(pid):
    return _repo.get_patient_by_id(pid)

#Created link_patient_user method
def link_patient_user(pid, username):
    return _repo.link_patient_user(pid, username)

# Adding get_patient_id_for_user method
def get_patient_id_for_user(username):
    return _repo.get_patient_id_for_user(username)


