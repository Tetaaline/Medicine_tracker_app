# Medicine_tracker_app- Smart Medicine Reminder & Patient Management System
---
A Python-based application that allows doctors to manage patients, assign  medicines, and automate medication reminders. Patients can log in using their full name and receive real-time notifications. Built using Object-Oriented Programming (OOP) and JSON-based storage.

---
## 1. Project Title
**MediTracker – Smart Medicine Reminder System**
---
A Python application that empowers doctors to easily manage patient prescriptions and enables patients to receive automated medication reminders.

## 2. Project Description

MediTracker was created to solve a real-world issue:  
**Patients often forget to take their medicine on time**, and doctors lack tools to track medication progress.  

Our solution provides:
- A simple and user-friendly doctor–patient management flow  
- Automatic reminder notifications  
- A clean and maintainable OOP code structure  
- Easy JSON storage databases
---
**Why these technologies?**
- **Python**: Beginner-friendly, powerful, and ideal for a terminal-based system.  
- **OOP**: Required for PLP 2 and ensures scalability and maintainability.  
- **JSON storage**: Lightweight and perfect for small projects.  
- **Colorama**: Enhances the terminal interface, making the DEMO attractive.

**Challenges we faced**
- Linking patient accounts without passwords → Solved using *Full Name Mapping*  
- Getting notifications to trigger correctly → Solved using *a background daemon thread*  
- Ensuring all services work together under OOP → Solved using *repository classes*  
- Keeping the code modular for GitHub collaboration → Achieved by splitting into service modules  
---
## 3. Table of Contents
- Project Title  
- Project Description  
- Table of Contents  
- How to Install & Run  
- How to Use the Project  
- Credits  
- License  

---

##  4. How to Install and Run the Project

Follow these steps to clone and run the project on your local machine.

### **Step 1 — Clone the Repository**
<!-- ```bash -->
git clone githttps://github.com/Tetaaline/Medicine_tracker_app.git
cd <Medicine_tracker_app>

### **Step 2 — Install the required package**
<!-- ``` cmd terminal -->
pip install colorama
### **Step 3 — Navigate to the src Folder **
cd src

### **Step 4 — Confirm the project structure**
Make sure your files are arranged like this:
src/
    main.py
    services/
    interface/
data/
    patients.json
    medicines.json
    schedules.json
README.md
If the data files don’t exist, the program automatically creates them.

### **Step 5 — Accessing JSON database on Linux/Ubuntu Terminal**
Navigate to the src Folder
Since this project utilizes JSON files as its database (as opposed to MySQL or PostgreSQL), there is no server to start. All data is stored locally inside the project folder in:
/data/
   ├── users.txt
   ├── patients.json
   ├── medicines.json
   └── schedules.json
These files are automatically created by the program the first time you run it.

Below are the simple Linux/Ubuntu commands to view, edit, and inspect your JSON database.
Steps to access JSON database: 
- Navigate to the project directory
    cd medicine-tracker-app
-  Navigate into the data folder
    cd data
- View JSON data in the terminal
    cat patients.json
- View nicely formatted JSON
cat patients.json | python3 -m json.tool
- Scroll through long JSON files
less patients.json
- Search inside JSON for a word
grep "John" -n patients.json
- Edit JSON manually
    nano medicines.json
    vim  medicines.json
- Check that JSON exists
ls -l
- Delete a JSON file (if you want to reset the database)
    rm patients.json
    rm medicines.json
    rm schedules.json
- Run the application again
    python3 main.py


### **Step 4 — Run the application**

From the src directory, run:
python main.py
---
## How to Use the Project
When the program starts, you will be asked to choose a role:
a. Doctor
b. Patient
c. User Admin
d. Exit

### **Doctor Workflow**


As a doctor, you can:

- Sign up or log in.

- Add a patient using their full name.

- Add medicines, edit them, and delete them.

- Set reminders for specific medicines.

- Edit existing reminders.

- Search for a patient or a medicine.

- Delete a patient when treatment is done.

- Every time a doctor adds a patient, an automatic patient account is created behind the scenes.


### **Patient Workflow**

Patients simply:

- Log in using their Full Name (no password needed).

- View all medicines assigned.

- View reminders.

- Receive pop-up notifications at the exact reminder time.

Important:
Patients must keep the terminal window open to allow the reminder system to run in the background.

