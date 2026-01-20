from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cinemapulse_2026_key'


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com' 
app.config['MAIL_PASSWORD'] = 'your-app-password'   
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


USERS = {"admin@cinema.com": "pulse123"}

MOVIES_DATA = [
    {"rank": 1, "title": "The Shawshank Redemption", "year": 1994, "rating": 9.3, "img": "https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGYtY2UxNmY0YzQyNGRlXkEyXkFqcGdeQXVyMTMzOTQyODU@._V1_.jpg"},
    {"rank": 2, "title": "The Godfather", "year": 1972, "rating": 9.2, "img": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg"},
    {"rank": 3, "title": "The Dark Knight", "year": 2008, "rating": 9.1, "img": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg"},
    
]



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    """Information about CinemaPulse."""
    return render_template('about.html')

@app.route('/support')
def support():
    """Contact or Help page."""
    return render_template('support.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username') 
        password = request.form.get('password')
        if email in USERS and USERS[email] == password:
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if email in USERS:
        return render_template('login.html', error="Account already exists.")
    USERS[email] = password
    session['user_email'] = email
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', movies=MOVIES_DATA)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    new_entry = Feedback(
        user_email=session['user_email'],
        movie_title=request.form.get('movie_title'),
        rating=int(request.form.get('rating')),
        comment=request.form.get('comment')
    )
    db.session.add(new_entry)
    db.session.commit()
    flash(f'Pulse recorded for {request.form.get("movie_title")}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in USERS:
            msg = Message("CinemaPulse - Recovery", recipients=[email])
            msg.body = f"Your password is: {USERS[email]}"
            mail.send(msg)
            return render_template('forgot_password.html', success_email=email)
        return render_template('forgot_password.html', error="Email not found.")
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)