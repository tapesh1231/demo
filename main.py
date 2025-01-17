from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb
import pymysql
from datetime import datetime
import secrets
print(secrets.token_hex(16))


print(pymysql.__version__)

app = Flask(__name__)
app.secret_key = 'a-secure-random-generated-key'

# Configuration for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tapesh%400811@localhost:3306/student_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

# Function to create the database if it doesn't exist
def create_database():
    try:
        connection = MySQLdb.connect(host='localhost', user='root', passwd='Tapesh@0811')
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_db")
        connection.commit()
        cursor.close()
        connection.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

# Call the function to create the database if not present
create_database()

# signup table
class Signup(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), db.ForeignKey('signup.email'), nullable=False)
    skills = db.relationship('Skill', backref='user_details', lazy=True)
    education = db.relationship('Education', backref='user_details', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(100), nullable=False)
    user_details_id = db.Column(db.Integer, db.ForeignKey('user_details.id'), nullable=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    user_details_id = db.Column(db.Integer, db.ForeignKey('user_details.id'), nullable=False)


# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

from flask_login import login_user, login_required

# Ensure login is successful and the user session is set properly
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Signup.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Login the user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Correct hashing method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if user already exists
        if Signup.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
        else:
            new_user = Signup(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/user-details', methods=['GET', 'POST'])
@login_required
def user_details():
    # Fetch name and email of the current user
    current_user_details = Signup.query.filter_by(id=current_user.id).first()
    name = current_user_details.name
    email = current_user_details.email

    if request.method == 'POST':
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        phone = request.form['phone']
        bio = request.form.get('bio', '')

        # Create UserDetails entry with fetched name and email
        user_details = UserDetails(
            name=name, dob=dob, phone=phone, bio=bio, email=email)

        db.session.add(user_details)
        db.session.commit()

        # Handle Skills
        skills = request.form.getlist('skills[]')
        for skill in skills:
            skill_entry = Skill(skill=skill, user_details_id=user_details.id)
            db.session.add(skill_entry)

        # Handle Education
        education_levels = request.form.getlist('level[]')
        subjects = request.form.getlist('subject[]')
        streams = request.form.getlist('stream[]')
        grades = request.form.getlist('grade[]')
        years = request.form.getlist('year[]')

        for level, subject, stream, grade, year in zip(education_levels, subjects, streams, grades, years):
            education_entry = Education(
                level=level, subject=subject, stream=stream, grade=grade, year=year,
                user_details_id=user_details.id)
            db.session.add(education_entry)

        db.session.commit()

        flash('Details submitted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('form.html', name=name, email=email)

@app.route('/portfolio')
@login_required
def portfolio():
    print(f"User {current_user.email} is viewing their profile.")
    user_details = UserDetails.query.filter_by(email=current_user.email).first()
    skills = Skill.query.filter_by(user_details_id=user_details.id).all()
    education = Education.query.filter_by(user_details_id=user_details.id).all()
    return render_template('portfolio.html', user_details=user_details, skills=skills, education=education)






@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)