from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
import MySQLdb
import pymysql

db = SQLAlchemy()
migrate = Migrate()

# Define the Signup model
class Signup(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Define the UserDetails model
class UserDetails(db.Model):
    email = db.Column(db.String(120), db.ForeignKey('signup.email'), primary_key=True)  # Make email the primary key and a foreign key
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)  # Add profile_image field
    skills = db.relationship('Skill', backref='user_details', lazy=True)
    education = db.relationship('Education', backref='user_details', lazy=True)

# Define the Skill model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(100), nullable=False)
    user_details_id = db.Column(db.String(120), db.ForeignKey('user_details.email'), nullable=False)  # Update foreign key reference

# Define the Education model
class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    user_details_id = db.Column(db.String(120), db.ForeignKey('user_details.email'), nullable=False)  # Update foreign key reference

# Define the ProjectComponent model
class ProjectComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    working_principle = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=False)
    guide = db.Column(db.Text, nullable=False)
    applications = db.Column(db.Text, nullable=False)
    challenges = db.Column(db.Text, nullable=False)
    circuit_diagram = db.Column(db.String(255), nullable=False)
    images = db.Column(db.String(255), nullable=False)  # Store image filenames as a comma-separated string
    user_details_id = db.Column(db.String(120), db.ForeignKey('user_details.email'), nullable=False)  # Update foreign key reference
    image_url = db.Column(db.String(255), nullable=True)  # Make this nullable

    def __repr__(self):
        return f'<Project {self.title}>'

# Function to create the database if it doesn't exist
def create_database():
    try:
        connection = MySQLdb.connect(host='localhost', user='root', passwd='Tapesh@0811')
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS apnavision")
        connection.commit()
        cursor.close()
        connection.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

# Function to add the image_url column to the Project table if it doesn't exist
def add_image_url_column():
    with db.engine.connect() as connection:
        cursor = connection.connection.cursor()
        try:
            cursor.execute("ALTER TABLE project ADD COLUMN image_url VARCHAR(255)")
            connection.connection.commit()
        except pymysql.err.OperationalError as e:
            if "Duplicate column name 'image_url'" in str(e):
                print("Column 'image_url' already exists.")
            else:
                raise
        finally:
            cursor.close()

# Function to add the author column to the Project table if it doesn't exist
def add_author_column():
    pass  # Remove the function body as the author column is no longer needed
