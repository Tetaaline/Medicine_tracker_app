import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MED_FILE = DATA_DIR / "medicines.json"


# Creation of JSONStorageBase class that serves as a parent class to the rest of child classes and that will contain storage details
class JSONStorageBase:
    # Base class to encapsulate JSON file storage responsibilities.
    # Provides ensure / load / save methods used by subclasses.
    
    def __init__(self, file_path: Path, root_key: str, default_structure=None):
        self.file_path = Path(file_path)
        self.root_key = root_key
        self.default_structure = default_structure if default_structure is not None else {self.root_key: []}

    def _ensure(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps(self.default_structure, indent=2))

    def _load(self):
        self._ensure()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

v]class MedicineInventory(JSONStorageBase):
    
    # Medicine-specific storage logic. Inherits file operations from JSONStorageBase\ 
    # and exposes the same behavior/logic as the original procedural module.
   
    def __init__(self, file_path: Path):
        super().__init__(file_path, "medicines", {"medicines": []})
# method that lists patient's medicine and their id 
    def list_medicines(self, patient_id):
        data = self._load()
        return [m for m in data.get("medicines", []) if m.get("patient_id") == patient_id]
# method to search medicine
    def search_medicines(self, patient_id, term):
        term = term.lower()
        return [m for m in self.list_medicines(patient_id) if term in m.get("name", "").lower()]
#Added method to add medine
    def add_medicine(self, patient_id, name, dosage, quantity, expiry_date, added_by):
        data = self._load()
        data["medicines"].append({
            "patient_id": patient_id,
            "name": name,
            "dosage": dosage,
            "quantity": quantity,
            "expiry_date": expiry_date,
            "added_by": added_by,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save(data)
#Added a method that will enable the doctor to edit patient's medicine specifically adjusting the name, dosage, quantity, and expiry date
    def edit_medicine(self, patient_id, index, name, dosage, quantity, expiry_date):
        data = self._load()
        meds = [m for m in data.get("medicines", []) if m.get("patient_id") == patient_id]
        if 0 <= index < len(meds):
            all_meds = data.get("medicines", [])
            global_idx = [i for i, m in enumerate(all_meds) if m.get("patient_id") == patient_id][index]
            data["medicines"][global_idx].update({
                "name": name,
                "dosage": dosage,
                "quantity": quantity,
                "expiry_date": expiry_date
            })
            self._save(data)
            return True
        return False
# I added a method that allows doctor to delete medicine especially when the patient has recovered and is not under doctor's surper
    def delete_medicine(self, patient_id, index):
        data = self._load()
        meds = [m for m in data.get("medicines", []) if m.get("patient_id") == patient_id]
        if 0 <= index < len(meds):
            all_meds = data.get("medicines", [])
            global_idx = [i for i, m in enumerate(all_meds) if m.get("patient_id") == patient_id][index]
            all_meds.pop(global_idx)
            self._save(data)
            return True
        return False


# Backward-compatibility wrappers that forward previous function calls before applying OOP organization style
_inventory = MedicineInventory(MED_FILE)


# Module-level functions to keep backward compatibility with the rest of the codebase.
def _ensure():
    return _inventory._ensure()
# These functions keep the former project code running by redirecting

def _load():
    return _inventory._load()


def _save(data):
    return _inventory._save(data)


def list_medicines(patient_id):
    return _inventory.list_medicines(patient_id)


def search_medicines(patient_id, term):
    return _inventory.search_medicines(patient_id, term)


def add_medicine(patient_id, name, dosage, quantity, expiry_date, added_by):
    return _inventory.add_medicine(patient_id, name, dosage, quantity, expiry_date, added_by)


def edit_medicine(patient_id, index, name, dosage, quantity, expiry_date):
    return _inventory.edit_medicine(patient_id, index, name, dosage, quantity, expiry_date)


def delete_medicine(patient_id, index):
    return _inventory.delete_medicine(patient_id, index)


