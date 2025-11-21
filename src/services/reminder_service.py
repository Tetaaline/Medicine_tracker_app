import json, sys, time, platform, subprocess, ctypes, shutil
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SCH_FILE = DATA_DIR / "schedules.json"

#class that will contain child classes containing data with details about how the doctor will give the patient reminders and how the patient will access them.
# Other classes can inherit from this, so we don't repeat storage logic everywhere
class JSONStorageBase:
    def __init__(self, file_path: Path, default_structure):
        self.file_path = Path(file_path)
        self.default_structure = default_structure

    def ensure(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps(self.default_structure, indent=2))

    def load(self):
        self.ensure()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

# Creates ScheduleManager child class for JSONStorageBase that give details on how the doctor will regulate schedules
class ScheduleManager(JSONStorageBase):
    def __init__(self, file_path: Path):
        super().__init__(file_path, {"schedules": []})

    # These helper methods keep the original function-based names intact  
    def _ensure(self):
        return self.ensure()

    def _load(self):
        return self.load()

    def _save(self, data):
        return self.save(data)

# Core reminder operations    
    def add_reminder(self, patient_id, medicine_name, dosage, time_hms, days, created_by):
        data = self._load()
        data["schedules"].append({
            "patient_id": patient_id,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "time": time_hms,
            "days": days,
            "created_by": created_by
        })
        self._save(data)

    def list_reminders(self, patient_id):
        data = self._load()
        return [r for r in data.get("schedules", []) if r.get("patient_id") == patient_id]

    def edit_reminder(self, patient_id, index, medicine_name, dosage, time_hms, days):
        data = self._load()
        rems = [r for r in data.get("schedules", []) if r.get("patient_id") == patient_id]
        if 0 <= index < len(rems):
            all_rems = data.get("schedules", [])
            global_idx = [i for i, r in enumerate(all_rems) if r.get("patient_id") == patient_id][index]
            all_rems[global_idx].update({
                "medicine_name": medicine_name,
                "dosage": dosage,
                "time": time_hms,
                "days": days
            })
            self._save(data)
            return True
        return False

    def _matches_now(self, reminder, now):
        try:
            r_hms = reminder.get("time", "00:00:00")
            r_hm = r_hms[:5]  # HH:MM
            now_hm = now.strftime("%H:%M")
            day_ok = now.strftime("%a")[:3] in reminder.get("days", [])
            return day_ok and (r_hm == now_hm)
        except Exception:
            return False

    def due_reminders_for_patient(self, patient_id, now=None):
        if now is None:
            now = datetime.now()
        data = self._load()
        return [r for r in data.get("schedules", []) if r.get("patient_id") == patient_id and self._matches_now(r, now)]

    # notification helpers (preserve original behavior)
    def beep(self):
        sys.stdout.write("\a")
        sys.stdout.flush()

    def notify_popup(self, title, message):
        border = "=" * 60
        print(f"""
{border}
 🔔 {title}
 {message}
{border}
""")
        self.beep()

    def patient_notification_daemon(self, patient_id, interval_seconds=10):
        last_sent_keys = set()  # (medicine_name, yyyy-mm-dd, HH:MM)
        try:
            while True:
                now = datetime.now()
                due = self.due_reminders_for_patient(patient_id, now=now)
                today = now.strftime("%Y-%m-%d")
                hm = now.strftime("%H:%M")
                for r in due:
                    key = (r.get("medicine_name", ""), today, hm)
                    if key in last_sent_keys:
                        continue
                    self.notify_popup("Medicine Reminder", f"Take {r['medicine_name']} - {r['dosage']} (now)")
                    last_sent_keys.add(key)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            pass
# instantiate manager and expose original module-level API for backward compatibility
_scheduler = ScheduleManager(SCH_FILE)


def _ensure():
    return _scheduler._ensure()


def _load():
    return _scheduler._load()


def _save(data):
    return _scheduler._save(data)

#Adding reminder method for patient's id, dosage, medicine_name. daya, and create_by
def add_reminder(patient_id, medicine_name, dosage, time_hms, days, created_by):
    return _scheduler.add_reminder(patient_id, medicine_name, dosage, time_hms, days, created_by)

#Adding list_reminder
def list_reminders(patient_id):
    return _scheduler.list_reminders(patient_id)

#Adding edit_reminder method
def edit_reminder(patient_id, index, medicine_name, dosage, time_hms, days):
    return _scheduler.edit_reminder(patient_id, index, medicine_name, dosage, time_hms, days)

# Creation of due_reminder method
def due_reminders_for_patient(patient_id, now=None):
    return _scheduler.due_reminders_for_patient(patient_id, now=now)

#Creation patient_notification_daemon

def patient_notification_daemon(patient_id, interval_seconds=10):
    return _scheduler.patient_notification_daemon(patient_id, interval_seconds=interval_seconds)



