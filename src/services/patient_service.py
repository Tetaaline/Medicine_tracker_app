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

