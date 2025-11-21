import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MED_FILE = DATA_DIR / "medicines.json"


# Creation of JSONStorageBase class that serves as a parent class to the rest of the child classes and that will contain storage details.
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



