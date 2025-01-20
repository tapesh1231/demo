from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import  LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import pymysql
from datetime import datetime
import os
import secrets
from database import db, migrate, Signup, UserDetails, Skill, Education, Project, ProjectComponent, create_database, add_image_url_column, add_author_column

print(secrets.token_hex(16))
print(pymysql.__version__)

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'a-secure-random-generated-key'

# Configuration for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tapesh%400811@localhost:3306/apnavision'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_image'), exist_ok=True)  # Ensure profile_image directory exists

# Initialize the database and login manager
db.init_app(app)
migrate.init_app(app, db)  # Initialize Flask-Migrate
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

# Call the function to create the database if not present
create_database()

# Create the database tables if they don't exist and add columns if necessary
with app.app_context():
    db.create_all()
    add_image_url_column()
    add_author_column()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Signup, int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Login route
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

# Signup route
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

# User details route
@app.route('/user-details', methods=['GET', 'POST'])
@login_required
def user_details():
    # Fetch name and email of the current user
    current_user_details = Signup.query.filter_by(id=current_user.id).first()
    name = current_user_details.name
    email = current_user_details.email

    user_details = UserDetails.query.filter_by(email=email).first()

    if request.method == 'POST':
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        phone = request.form['phone']
        bio = request.form.get('bio', '')

        # Handle profile image upload
        profile_image = request.files['profile_image']
        if profile_image:
            filename = secure_filename(f"{current_user.name}_{current_user.id}.jpg")
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profile_image', filename)
            profile_image.save(profile_image_path)
        else:
            filename = user_details.profile_image if user_details else None

        if user_details:
            user_details.name = name
            user_details.dob = dob
            user_details.phone = phone
            user_details.bio = bio
            user_details.profile_image = filename
        else:
            user_details = UserDetails(
                email=email, name=name, dob=dob, phone=phone, bio=bio, profile_image=filename)
            db.session.add(user_details)

        db.session.commit()

        # Handle Skills
        Skill.query.filter_by(user_details_id=user_details.email).delete()
        skills = request.form.getlist('skills[]')
        for skill in skills:
            skill_entry = Skill(skill=skill, user_details_id=user_details.email)
            db.session.add(skill_entry)

        # Handle Education
        Education.query.filter_by(user_details_id=user_details.email).delete()
        education_levels = request.form.getlist('level[]')
        subjects = request.form.getlist('subject[]')
        streams = request.form.getlist('stream[]')
        grades = request.form.getlist('grade[]')
        years = request.form.getlist('year[]')

        for level, subject, stream, grade, year in zip(education_levels, subjects, streams, grades, years):
            education_entry = Education(
                level=level, subject=subject, stream=stream, grade=grade, year=year,
                user_details_id=user_details.email)
            db.session.add(education_entry)

        db.session.commit()

        flash('Details submitted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('form.html', name=name, email=email, user_details=user_details)

# Portfolio route
@app.route('/portfolio')
@login_required
def portfolio():
    print(f"User {current_user.email} is viewing their profile.")
    user_details = UserDetails.query.filter_by(email=current_user.email).first()
    if user_details is None:
        flash('User details not found. Please complete your profile.', 'danger')
        return redirect(url_for('user_details'))
    
    skills = Skill.query.filter_by(user_details_id=user_details.email).all()
    education = Education.query.filter_by(user_details_id=user_details.email).all()
    projects = Project.query.filter_by(user_details_id=user_details.email).all()
    return render_template('portfolio.html', user_details=user_details, skills=skills, education=education, projects=projects)

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    user_details = UserDetails.query.filter_by(email=current_user.email).first()
    if user_details is None:
        flash('User details not found. Please complete your profile.', 'danger')
        return redirect(url_for('user_details'))
    
    projects = Project.query.filter_by(user_details_id=user_details.email).all()
    
    for project in projects:
        print(f"Name: {user_details.name}, Project Title: {project.title}, Overview: {project.overview}, Images: {project.images}")
    
    return render_template('dashboard.html', projects=projects)

@app.route('/project')
def project():
    return render_template('project.html')

# Project detail route
@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('home'))

# Upload project route
@app.route('/uplode_project', methods=['GET', 'POST'])
@login_required
def uplode_project():
    if request.method == 'POST':
        title = request.form['projectTitle']
        overview = request.form['projectOverview']
        objectives = request.form['projectObjectives']
        components = request.form.getlist('components[]')
        quantities = request.form.getlist('quantities[]')
        descriptions = request.form.getlist('descriptions[]')
        working_principle = request.form['workingPrinciple']
        code = request.form['code']
        guide = request.form['stepByStepGuide']
        applications = request.form['applications']
        challenges = request.form['challenges']
        
        # Handle file uploads
        circuit_diagram = request.files['circuitDiagram']
        images = request.files.getlist('images')        
        # Save files to the server
        circuit_diagram_filename = secure_filename(circuit_diagram.filename)
        circuit_diagram.save(os.path.join(app.config['UPLOAD_FOLDER'], circuit_diagram_filename))
        
        image_filenames = []
        for image in images:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            image_filenames.append(image_filename)
        
        # Fetch user details ID for the current user
        user_details = UserDetails.query.filter_by(email=current_user.email).first()
        if not user_details:
            flash('User details not found. Please complete your profile.', 'danger')
            return redirect(url_for('user_details'))
        
        # Create a new project entry
        new_project = Project(
            title=title,
            overview=overview,
            objectives=objectives,
            working_principle=working_principle,
            code=code,
            guide=guide,
            applications=applications,
            challenges=challenges,
            circuit_diagram=circuit_diagram_filename,
            images=','.join(image_filenames),
            user_details_id=user_details.email
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        # Add components to the project
        for component, quantity, description in zip(components, quantities, descriptions):
            new_component = ProjectComponent(
                component=component,
                quantity=quantity,
                description=description,
                project_id=new_project.id
            )
            db.session.add(new_component)
        
        db.session.commit()
        
        flash('Project uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('uplode_project.html')

# Main function to run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)