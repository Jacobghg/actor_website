from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mail import Mail, Message
import os
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
import bcrypt
import subprocess

from dotenv import load_dotenv

#load environemnt variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Configuring Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')


mail = Mail(app)

# Path for static content
STATIC_FOLDER = 'static'
headshot_folder = os.path.join(STATIC_FOLDER, 'headshots')
headshots = [f for f in os.listdir(headshot_folder) if f.endswith(('jpg', 'jpeg', 'png'))]

# User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# In-memory user store
users = {
    'admin': bcrypt.hashpw('password'.encode(), bcrypt.gensalt())
}

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
def home():
    return render_template('index.html', headshots=headshots)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        subject = 'New Contact Form Submission'
        sender = app.config['MAIL_USERNAME']
        recipients = ['jacobgiangiulio@gmail.com']
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        
        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        mail.send(msg)
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/demo-reel')
def demo_reel():
    video_url = "https://dl.dropboxusercontent.com/s/bu6os0bzyeokn7ri15533/demo_reel.mp4"
    return render_template('demo_reel.html', video_url=video_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.checkpw(password.encode(), users[username]):
            login_user(User(username))
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.id != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

if __name__ == "__main__":
    # Run the bash script
    subprocess.run(['bash', 'run.bash'])
    app.run(debug=True, host='0.0.0.0', port=5001)
