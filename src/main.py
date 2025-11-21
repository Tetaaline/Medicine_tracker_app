#!/usr/bin/python3

import os
import threading
from colorama import init, Fore, Back, Style

#This is really to integrate or initialize colorama so that it can work properly on all systems 
init(autoreset=True)

#Thi will import UI display  functions and input validators
from interface.menu import print_header
from interface.validators import (
    is_letters_only, is_alnum_username, is_valid_dosage,
    is_valid_time_hms, normalize_days
)
from services.user_service import save_user, authenticate, user_exists, list_doctors, get_user
from services.patient_service import (
    list_patients, add_patient, delete_patient, search_patients,
    link_patient_user, get_patient_id_for_user, get_patient_by_id, add_patient_if_absent
)
from services.inventory_service import list_medicines, add_medicine, edit_medicine, delete_medicine, search_medicines
from services.reminder_service import add_reminder, list_reminders, edit_reminder, patient_notification_daemon


ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

class MediTrackerApp:
    def __init__(self):
#This will track which type of user is currently logged in if its either (doctor/patient/none) 
        self.CURRENT_ROLE = "neutral"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self):
        input("\nPress Enter to continue...")

    def get_input(self, prompt, min_len=1):
        # Apply different colors to the input prompt based on the active role
        if self.CURRENT_ROLE == "doctor":
            prompt = Back.RESET + Fore.LIGHTGREEN_EX + prompt + Style.RESET_ALL
        elif self.CURRENT_ROLE == "patient":
            prompt = Back.RESET + Fore.CYAN + prompt + Style.RESET_ALL
        else:
            # Neutral / admin / main menu style
            prompt = Fore.LIGHTCYAN_EX + prompt + Style.RESET_ALL
        while True:
            v = input(prompt).strip()
            if len(v) >= min_len:
                return v
            print(Fore.LIGHTRED_EX + "Input must be at least {} characters.".format(min_len))

    # ===== Doctor =====
    def doctor_signup(self):
        self.clear_screen()
        print_header("Doctor Sign Up")
        username = self.get_input("Create username (letters & numbers only): ", 3)
        if not is_alnum_username(username):
            print(Fore.LIGHTRED_EX + "Please enter letters and characters only " + Style.RESET_ALL)
            return None
        if user_exists(username):
            print(Fore.LIGHTRED_EX + "Username already exists!" + Style.RESET_ALL)
            return None
        email = self.get_input("Email: ")
        org = self.get_input("Organization name: ", 2)
        pwd = self.get_input("Create password (min 8 chars): ", 8)
        save_user(username, pwd, username, email, role="doctor", org=org)
        print(f"\nWelcome Dr. {username}! Account created successfully.") 
        return {"username": username, "name": username, "role":"doctor", "org": org}

    def login_flow(self, role_label):
        self.clear_screen()
        print_header(f"{role_label.title()} Login")
        if role_label == "patient":
            # Full name only (no password)
            full_name = self.get_input("Your Full Name: ", 2)
            user = get_user(full_name)  # stored as username for patients
            if not user or user.get("role") != "patient":
                print("Invalid patient full name.")
                return None
            pid = get_patient_id_for_user(user["username"])
            if not pid:
                print("No patient record linked to this account yet.")
                return None
            user["patient_id"] = pid
            print(f"\nWelcome back, {user['name']}!")
            return user
        else:
            # Doctor login requires password as before
            user_or_email = self.get_input("Username or Email: ", 1)
            pwd = self.get_input("Password: ", 1)
            user = authenticate(user_or_email, pwd)
            if not user:
                print("Invalid credentials!")
                return None
            if user["role"] != role_label:
                print(f"Account role mismatch. You are registered as '{user['role']}'.")
                return None
            print(f"\nWelcome back, {user['name']}!")
            return user

    def pick_patient(self, doctor_username):
        pats = list_patients(doctor_username)
        if not pats:
            print("No patients yet.")
            return None, []
        for i, p in enumerate(pats, start=1):
            print(f"[{i}] {p['name']} (ID: {p['id']})  Linked Full Name: {p.get('user_username','-')}")
        try:
            idx = int(self.get_input("Select patient number: ", 1)) - 1
            if 0 <= idx < len(pats):
                return pats[idx], pats
        except ValueError:
            pass
        print("Invalid selection.")
        return None, pats

    def doctor_menu(self, user):
        while True:
            self.clear_screen()
            print_header(f"Doctor Panel - Dr. {user['name']} ({user.get('org','')})")
            print(Fore.LIGHTBLUE_EX+"1." +Style.RESET_ALL +"Add Patient (auto-creates patient login via full name)")
            print(Fore.LIGHTBLUE_EX+"2." +Style.RESET_ALL + " View/Edit Patient's Medicine")
            print(Fore.LIGHTBLUE_EX+"3." +Style.RESET_ALL + " Delete Patient (finished dose)")
            print(Fore.LIGHTBLUE_EX+"4." +Style.RESET_ALL + "Add Reminder for a Patient's Medicine")
            print(Fore.LIGHTBLUE_EX+"5." +Style.RESET_ALL + "Edit Reminder")
            print(Fore.LIGHTBLUE_EX+"6." +Style.RESET_ALL + " View Reminders for a Patient")
            print(Fore.LIGHTBLUE_EX+"7." +Style.RESET_ALL + "Search/Filter (Patients & Medicines)")
            print(Fore.LIGHTBLUE_EX+"8." +Style.RESET_ALL + " Logout")
            choice = self.get_input("Choose option (1-8): ", 1)

            if choice == "1":
                pname = self.get_input("Patient FULL NAME (letters only): ", 2)
                if not is_letters_only(pname):
                    print('Invalid input, please enter patient name in letters')
                    self.pause(); continue
                pid = add_patient(user["username"], pname)
                save_user(pname, "", pname, "", role="patient", org="")
                link_patient_user(pid, pname)
                print(f"Patient '{pname}' added with ID {pid}.")
                print("Tell the patient to log in using their FULL NAME only (no password).")
                self.pause()

            elif choice == "2":
                print_header("Select Patient")
                p, _ = self.pick_patient(user["username"])
                if not p: self.pause(); continue
                self.manage_patient_medicine(user["username"], p["id"], p["name"])

            elif choice == "3":
                print_header("Delete Patient")
                p, _ = self.pick_patient(user["username"])
                if not p: self.pause(); continue
                ok = delete_patient(user["username"], p["id"])
                print("Patient deleted." if ok else "Failed to delete.")
                self.pause()

            elif choice == "4":
                self.add_reminder_flow(user)

            elif choice == "5":
                self.edit_reminder_flow(user)

            elif choice == "6":
                self.view_reminders_flow(user)

            elif choice == "7":
                self.search_flow(user)

            elif choice == "8":
                print(Fore.LIGHTYELLOW_EX + "Logging out..." + Style.RESET_ALL)
                break
            else:
                print("Invalid choice.")
                self.pause()

    def manage_patient_medicine(self, doctor_username, patient_id, patient_name):
        from services.inventory_service import list_medicines, add_medicine, edit_medicine, delete_medicine, search_medicines
        while True:
            self.clear_screen()
            print_header(f"Medicines for {patient_name}")
            print(Fore.CYAN + "1." + Style.RESET_ALL + "View Medicines")
            print(Fore.CYAN + "2." + Style.RESET_ALL + "Add Medicine")
            print(Fore.CYAN + "3." + Style.RESET_ALL + "Edit Medicine")
            print(Fore.CYAN + "4." + Style.RESET_ALL + "Delete Medicine")
            print(Fore.CYAN + "5." + Style.RESET_ALL + "Search Medicines")
            print(Fore.CYAN + "6." + Style.RESET_ALL +  "Back")
            ch = self.get_input("Choose option (1-6): ", 1)

            if ch == "1":
                meds = list_medicines(patient_id)
                if not meds: print("No medicines."); self.pause(); continue
                for i, m in enumerate(meds, start=1):
                    print(f"[{i}] {m['name']} | {m['dosage']} | Qty: {m['quantity']} | Exp: {m['expiry_date']}")
                self.pause()

            elif ch == "2":
                mname = self.get_input("Medicine name (letters only): ", 2)
                if not is_letters_only(mname):
                    print("Invalid input, please enter medicine name in letters"); self.pause(); continue
                dosage = self.get_input("Dosage (e.g., 500mg, 1g, 0.2l): ", 2)
                if not is_valid_dosage(dosage):
                    print("Input dosage in mg,g,or liters and write it as a number"); self.pause(); continue
                qty = self.get_input("Quantity (number): ", 1)
                if not qty.replace('.','',1).isdigit():
                    print("Invalid quantity; enter a number"); self.pause(); continue
                exp = self.get_input("Expiry date (YYYY-MM-DD): ", 10)
                add_medicine(patient_id, mname, dosage, qty, exp, added_by=doctor_username)
                print("Medicine added.")
                self.pause()

            elif ch == "3":
                meds = list_medicines(patient_id)
                if not meds: print("No medicines."); self.pause(); continue
                for i, m in enumerate(meds, start=1):
                    print(f"[{i}] {m['name']} | {m['dosage']} | Qty: {m['quantity']} | Exp: {m['expiry_date']}")
                try:
                    idx = int(self.get_input("Select number to edit: ", 1)) - 1
                except ValueError:
                    print("Invalid number"); self.pause(); continue
                if not (0 <= idx < len(meds)):
                    print("Invalid selection"); self.pause(); continue

                mname = self.get_input("New name (letters only): ", 2)
                if not is_letters_only(mname):
                    print("Invalid input, please enter medicine name in letters"); self.pause(); continue
                dosage = self.get_input("New dosage (e.g., 500mg): ", 2)
                if not is_valid_dosage(dosage):
                    print("Input dosage in mg,g,or liters and write it as a number"); self.pause(); continue
                qty = self.get_input("New quantity (number): ", 1)
                if not qty.replace('.','',1).isdigit():
                    print("Invalid quantity; enter a number"); self.pause(); continue
                exp = self.get_input("New expiry date (YYYY-MM-DD): ", 10)
                ok = edit_medicine(patient_id, idx, mname, dosage, qty, exp)
                print("Updated." if ok else "Failed to update.")
                self.pause()

            elif ch == "4":
                meds = list_medicines(patient_id)
                if not meds: print("No medicines."); self.pause(); continue
                for i, m in enumerate(meds, start=1):
                    print(f"[{i}] {m['name']} | {m['dosage']} | Qty: {m['quantity']}")
                try:
                    idx = int(self.get_input("Select number to delete: ", 1)) - 1
                except ValueError:
                    print("Invalid number"); self.pause(); continue
                ok = delete_medicine(patient_id, idx)
                print("Deleted." if ok else "Failed to delete.")
                self.pause()

            elif ch == "5":
                term = self.get_input("Search term: ", 1)
                results = search_medicines(patient_id, term)
                if not results:
                    print("No medicines match your search.")
                else:
                    for m in results:
                        print(f"- {m['name']} | {m['dosage']} | Qty: {m['quantity']} | Exp: {m['expiry_date']}")
                self.pause()

            elif ch == "6":
                break
            else:
                print(Fore.LIGHTRED_EX + "Invalid choice." + Style.RESET_ALL); self.pause()

    def add_reminder_flow(self, user):
        print_header("Add Reminder")
        p, _ = self.pick_patient(user["username"])
        if not p: self.pause(); return
        meds = list_medicines(p["id"])
        if not meds:
            print("No medicines for this patient yet. Add medicine first.")
            self.pause(); return
        for i, m in enumerate(meds, start=1):
            print(f"[{i}] {m['name']} ({m['dosage']})")
        try:
            midx = int(self.get_input("Select medicine number: ", 1)) - 1
            if not (0 <= midx < len(meds)):
                print("Invalid selection."); self.pause(); return
        except ValueError:
            print("Invalid selection."); self.pause(); return
        time_hms = self.get_input("Time (HH:MM:SS): ", 8)
        if not is_valid_time_hms(time_hms):
            print(" Invalid input, enter hours, minutes, and seconds")
            self.pause(); return
        days_raw = self.get_input(" Days (comma-separated Mon,Tue,Wed,Thu,Fri,Sat,Sun) or leave blank for daily: ", 0)
        if days_raw.strip():
            days = normalize_days([d for d in days_raw.split(",") if d.strip()])
            if not days:
                print("Invalid input, please enter days from Mon to Sun"); self.pause(); return
        else:
            days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        d = meds[midx]["dosage"]
        if not is_valid_dosage(d):
            print('Input dosage in mg,g,or liters and write it as a number'); self.pause(); return
        add_reminder(p["id"], meds[midx]["name"], d, time_hms, days, created_by=user["username"])
        print(Fore.LIGHTGREEN_EX + "Reminder added successfully." + Style.RESET_ALL)
        self.pause()

    def edit_reminder_flow(self, user):
        print_header("Edit Reminder")
        p, _ = self.pick_patient(user["username"])
        if not p: self.pause(); return
        rems = list_reminders(p["id"])
        if not rems:
            print("No reminders for this patient."); self.pause(); return
        for i, r in enumerate(rems, start=1):
            print(f"[{i}] {r['medicine_name']} {r['dosage']} at {r['time']} on {','.join(r['days'])}")
        try:
            ridx = int(self.get_input("Select reminder number to edit: ", 1)) - 1
        except ValueError:
            print("Invalid number"); self.pause(); return
        if not (0 <= ridx < len(rems)):
            print("Invalid selection"); self.pause(); return
        med_name = self.get_input("New medicine name (letters only): ", 2)
        if not is_letters_only(med_name):
            print("Invalid input, please enter medicine name in letters"); self.pause(); return
        dosage = self.get_input("New dosage (e.g., 500mg): ", 2)
        if not is_valid_dosage(dosage):
            print("Input dosage in mg,g,or liters and write it as a number"); self.pause(); return
        time_hms = self.get_input("New Time (HH:MM:SS): ", 8)
        if not is_valid_time_hms(time_hms):
            print(" Invalid input, enter hours, minutes, and seconds"); self.pause(); return
        days_raw = self.get_input(" Days (comma-separated Mon,Tue,Wed,Thu,Fri,Sat,Sun) or leave blank for daily: ", 0)
        if days_raw.strip():
            days = normalize_days([d for d in days_raw.split(",") if d.strip()])
            if not days:
                print("Invalid input, please enter days from Mon to Sun"); self.pause(); return
        else:
            days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        ok = edit_reminder(p["id"], ridx, med_name, dosage, time_hms, days)
        print("Reminder updated." if ok else "Failed to update reminder.")
        self.pause()

    def view_reminders_flow(self, user):
        print_header("View Reminders")
        p, _ = self.pick_patient(user["username"])
        if not p: self.pause(); return
        rems = list_reminders(p["id"])
        if not rems:
            print("No reminders for this patient."); self.pause(); return
        for i, r in enumerate(rems, start=1):
            print(f"[{i}] {r['medicine_name']} {r['dosage']} at {r['time']} on {','.join(r['days'])}")
        self.pause()

    def search_flow(self, user):
        print_header("Search / Filter")
        term = self.get_input("Enter search term: ", 1)

        pats = search_patients(user["username"], term)
        from services.inventory_service import list_medicines
        all_pats = list_patients(user["username"])
        matched_meds = []
        for p in all_pats:
            for m in list_medicines(p["id"]):
                if term.lower() in m.get("name","").lower():
                    matched_meds.append((p, m))

        if not pats and not matched_meds:
            print("No patients or medicines matched your search.")
        else:
            if pats:
                print("\nPatients:")
                for p in pats:
                    print(f"- {p['name']} (ID: {p['id']})  Linked Full Name: {p.get('user_username','-')}")
            if matched_meds:
                print("\nMedicines (matching across all patients):")
                for p, m in matched_meds:
                    print(f"- {m['name']} | {m['dosage']} | Qty: {m['quantity']} | Patient: {p['name']} (ID: {p['id']})")
        self.pause()
  # ===== Patient =====
    def start_patient_notifications_background(self, patient_id):
        t = threading.Thread(target=patient_notification_daemon, args=(patient_id, 10), daemon=True)
        t.start()
        return t

    def patient_menu(self, user):
        self.start_patient_notifications_background(user["patient_id"])
        while True:
            self.clear_screen()
            print_header(f"Welcome {user['name']}")
            print("(Keep this window open to receive pop-up reminders.)")
            print(Fore.LIGHTCYAN_EX +"1."+  Style.RESET_ALL + "View My Medicines")
            print(Fore.LIGHTCYAN_EX + "2."+  Style.RESET_ALL + "View/Check My Reminders")
            print(Fore.LIGHTCYAN_EX + "3." + Style.RESET_ALL +   "Logout")
            ch = self.get_input("Choose option (1-3): ", 1)
            if ch == "1":
                pid = user.get("patient_id")
                meds = list_medicines(pid)
                if not meds:
                    print("No medicines assigned yet.")
                else:
                    for i, m in enumerate(meds, start=1):
                        print(f"[{i}] {m['name']} | {m['dosage']} | Qty: {m['quantity']} | Exp: {m['expiry_date']}")
                self.pause()
            elif ch == "2":
                pid = user.get("patient_id")
                rems = list_reminders(pid)
                if not rems:
                    print("No reminders set for you yet.")
                else:
                    for i, r in enumerate(rems, start=1):
                        print(f"[{i}] {r['medicine_name']} {r['dosage']} at {r['time']} on {','.join(r['days'])}")
                self.pause()
            elif ch == "3":
                print(Fore.LIGHTYELLOW_EX + "Logging out..." + Style.RESET_ALL); break
            else:
                print(Fore.LIGHTRED_EX + "Invalid choice." + Style.RESET_ALL); self.pause()

    # ===== Admin =====
    # def admin_menu(self):
    #     self.clear_screen()
    #     print_header("User Admin Login")
    #     u = self.get_input("Username: ", 1)
    #     p = self.get_input("Password: ", 1)
    #     if u != ADMIN_USER or p != ADMIN_PASS:
    #         print("Invalid admin credentials."); self.pause(); return
    #     while True:
    #         self.clear_screen()
    #         print_header("User Admin")
    #         print("1. View doctors list")
    #         print("2. Back")
    #         c = self.get_input("Choose (1-2): ", 1)
    #         if c == "1":
    #             docs = list_doctors()
    #             if not docs:
    #                 print("No doctors have signed up yet.")
    #             else:
    #                 for d in docs:
    #                     print(f"- Dr. {d['name']} | Org: {d['org']} | Username: {d['username']}")
    #             self.pause()
    #         elif c == "2":
    #             break
    #         else:
    #             print(Fore.LIGHTRED_EX + "Invalid choice." + Style.RESET_ALL); self.pause()

    def main(self):
        while True:
            self.CURRENT_ROLE = "neutral"
            self.clear_screen()
            # Title screen
            print(Fore.LIGHTCYAN_EX + "="*60 + Style.RESET_ALL)
            print(Fore.WHITE + "███   MEDI-TRACKER   ███".center(60) + Style.RESET_ALL)
            print(Fore.LIGHTGREEN_EX + "A Smart Medicine Reminder System".center(60) + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + "="*60 + Style.RESET_ALL)
            print()
            print(Fore.LIGHTCYAN_EX + "Select Role:" + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + "a." + Style.RESET_ALL + " Doctor")
            print(Fore.LIGHTCYAN_EX + "b." + Style.RESET_ALL + " Patient")
            # print(Fore.LIGHTCYAN_EX + "c." + Style.RESET_ALL + " User Admin")
            print(Fore.LIGHTCYAN_EX + "c." + Style.RESET_ALL + " Exit")
            role_choice = self.get_input("Choose option (a-d): ", 1).lower()

            if role_choice == "a":
                self.CURRENT_ROLE = "doctor"
                self.clear_screen()
                print_header("Doctor Access")
                print(Fore.LIGHTCYAN_EX + "1." + Style.RESET_ALL + " Sign Up")
                print(Fore.LIGHTCYAN_EX + "2." + Style.RESET_ALL + " Log In")
                print(Fore.LIGHTCYAN_EX + "3." + Style.RESET_ALL + " Back")
                c = self.get_input("Choose (1-3): ", 1)
                if c == "1":
                    u = self.doctor_signup()
                    if u: self.doctor_menu(u)
                elif c == "2":
                    u = self.login_flow("doctor")
                    if u: self.doctor_menu(u)
                elif c == "3":
                    continue
                else:
                    print(Fore.LIGHTRED_EX + "Invalid choice."); self.pause()

            elif role_choice == "b":
                self.CURRENT_ROLE = "patient"
                self.clear_screen()
                print_header("Patient Access")
                print(Fore.LIGHTCYAN_EX + "1." + Style.RESET_ALL + " Log In (Full Name only)")
                print(Fore.LIGHTCYAN_EX + "2." + Style.RESET_ALL + " Back")
                c = self.get_input("Choose (1-2): ", 1)
                if c == "1":
                    u = self.login_flow("patient")
                    if u: self.patient_menu(u)
                elif c == "2":
                    continue
                else:
                    print(Fore.LIGHTRED_EX + "Invalid choice."); self.pause()

            # elif role_choice == "c":
            #     self.CURRENT_ROLE = "neutral"
            #     self.admin_menu()

            elif role_choice == "c":
                print(Fore.LIGHTGREEN_EX + "Goodbye!"); break
            else:
                print(Fore.LIGHTRED_EX + "Invalid choice."); self.pause()

if __name__ == "__main__":
    app = MediTrackerApp()
    app.main()
