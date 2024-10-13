from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Folder to store uploaded files
app.config['BACKGROUND_FOLDER'] = 'static/backgrounds/'  # Folder to store background images

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if user is not authenticated

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=True)  # Path to uploaded image
    user = db.relationship('User', backref='posts')  # Relationship to access the user

# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100), nullable=False)  # Store as a string for simplicity

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

@app.route('/')
@login_required
def home():
    posts = Post.query.all()  # Get all posts, including image paths
    events = Event.query.all()  # Get all events
    return render_template('home.html', posts=posts, events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials')
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle file upload
        file = request.files.get('file')
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)  # Save file in the uploads folder

            # Create new post with uploaded image
            new_post = Post(user_id=current_user.id, content="Uploaded an image", image=file.filename)
            db.session.add(new_post)
            db.session.commit()

            flash('File uploaded and post created successfully!')
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    users = User.query.all()  # Get all users
    posts = Post.query.all()  # Get all posts
    events = Event.query.all()  # Get all events

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = request.form.get('user_id')
        post_id = request.form.get('post_id')
        event_id = request.form.get('event_id')
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        background_image = request.files.get('background_image')

        if action == 'create':
            new_user = User(username=username, password=password, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully!')

        elif action == 'edit' and user_id:
            user = User.query.get(user_id)
            if user:
                user.username = username
                user.password = password
                db.session.commit()
                flash('User updated successfully!')

        elif action == 'delete' and user_id:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully!')

        elif action == 'delete_post' and post_id:
            post = Post.query.get(post_id)
            if post:
                db.session.delete(post)
                db.session.commit()
                flash('Post deleted successfully!')

        elif action == 'upload_background' and background_image:
            background_path = os.path.join(app.config['BACKGROUND_FOLDER'], 'background.jpg')
            background_image.save(background_path)
            flash('Background image updated successfully!')

        elif action == 'add_event':
            new_event = Event(title=title, description=description, date=date)
            db.session.add(new_event)
            db.session.commit()
            flash('Event added successfully!')

        elif action == 'delete_event' and event_id:
            event = Event.query.get(event_id)
            if event:
                db.session.delete(event)
                db.session.commit()
                flash('Event deleted successfully!')

        return redirect(url_for('admin'))

    return render_template('admin.html', users=users, posts=posts, events=events)

# New Route for Posts Page
@app.route('/posts')
@login_required
def posts():
    all_posts = Post.query.all()  # Retrieve all posts
    return render_template('posts.html', posts=all_posts)  # Render the posts template

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')

