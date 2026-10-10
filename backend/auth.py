# backend/auth.py
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
from filelock import FileLock

STUDENT_DB = 'student_records_template.csv'
LOCK_FILE = 'student_records.lock'

def init_db():
    if not os.path.exists(STUDENT_DB) or os.stat(STUDENT_DB).st_size == 0:
        df = pd.DataFrame(columns=['StudentName', 'Password', 'StudentsID', 'HasHostel', 'Gender', 'Room_Number', 'Role'])
        df.to_csv(STUDENT_DB, index=False)

def register_student(name, student_id, password, gender, role='student'):
    init_db()
    with FileLock(LOCK_FILE):
        df = pd.read_csv(STUDENT_DB)
        if str(student_id) in df['StudentsID'].astype(str).values:
            return False, "Student ID already registered."
        
        hashed_pw = generate_password_hash(password)
        new_student = pd.DataFrame([{
            'StudentName': name,
            'Password': hashed_pw,
            'StudentsID': student_id,
            'HasHostel': False,
            'Gender': gender,
            'Room_Number': None,
            'Role': role
        }])
        
        df = pd.concat([df, new_student], ignore_index=True)
        df.to_csv(STUDENT_DB, index=False)
        return True, "Registration successful."

def verify_login(student_id, password):
    init_db()
    df = pd.read_csv(STUDENT_DB)
    user = df[df['StudentsID'].astype(str) == str(student_id)]
    
    if user.empty:
        return False, None
    
    stored_hash = user.iloc[0]['Password']
    if check_password_hash(stored_hash, password):
        return True, user.iloc[0].to_dict()
    
    return False, None