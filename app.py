# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from backend.auth import register_student, verify_login
from backend.inventory import get_grouped_availability, request_booking
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # Required for secure sessions and flash messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        gender = request.form.get('gender')
        
        success, message = register_student(name, student_id, password, gender)
        flash(message)
        if success:
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        
        success, user_data = verify_login(student_id, password)
        if success:
            session['student_id'] = user_data['StudentsID']
            session['gender'] = user_data['Gender']
            flash('Login successful!')
            return redirect(url_for('hostels'))
        else:
            flash('Invalid Student ID or Password.')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/hostels')
def hostels():
    if 'student_id' not in session:
        flash('Please login to view hostels.')
        return redirect(url_for('login'))
        
    user_gender = session.get('gender')
    # Filter available rooms by the logged-in student's gender
    rooms = get_grouped_availability(gender_filter=user_gender)
    return render_template('hostels.html', rooms=rooms)

@app.route('/book', methods=['POST'])
def book():
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    hostel_name = request.form.get('hostel_name')
    room_number = request.form.get('room_number')
    student_id = session.get('student_id')
    
    success, message = request_booking(student_id, hostel_name, int(room_number))
    flash(message)
    return redirect(url_for('hostels'))

if __name__ == '__main__':
    # Creates an empty student database if it doesn't exist yet
    from backend.auth import init_db
    init_db()
    app.run(debug=True, port=5000)