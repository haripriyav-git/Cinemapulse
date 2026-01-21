from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cinemapulse_2026_key'

# --- Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hpriyasvraman@gmail.com' 
app.config['MAIL_PASSWORD'] = 'xrfhlytheljtzpvx'   
app.config['MAIL_DEFAULT_SENDER'] = 'hpriyasvraman@gmail.com'
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- Temporary User Store ---
USERS = {"admin@cinema.com": "pulse123"}

# --- Movie Data (Cleaned and Fixed) ---
MOVIES_DATA = [
    {"rank":1,"title":"The Shawshank Redemption","year":1994,"rating":9.3,"img":"https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGYtY2UxNmY0YzQyNGRlXkEyXkFqcGdeQXVyMTMzOTQyODU@._V1_UX500_.jpg"},
    {"rank":2,"title":"Ramayana: The Legend of Prince Rama","year":1993,"rating":9.2,"img":"https://m.media-amazon.com/images/M/MV5BMDAxYjU2MDMtYjExNi00NThmLTg3NzUtNTE3NzYwMGY2M2UyXkEyXkFqcGdeQXVyMTEzMTI1Mjk3@._V1_UX500_.jpg"},
    {"rank":3,"title":"The Godfather","year":1972,"rating":9.2,"img":"https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX500_.jpg"},
    {"rank":4,"title":"The Dark Knight","year":2008,"rating":9.1,"img":"https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_UX500_.jpg"},
    {"rank":5,"title":"Jai Bhim","year":2021,"rating":8.8,"img":"https://m.media-amazon.com/images/M/MV5BY2I4MmM1N2EtM2YzOS00OWUzLTkzYzctNDc5NDUxZWQzN2IzXkEyXkFqcGdeQXVyMTMzNzIyNDc1@._V1_UX500_.jpg"},
    {"rank":6,"title":"Schindler's List","year":1993,"rating":9.0,"img":"https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctMjRhS00zZGJlLTgzOTctOTUxYjE1ODA2NzE1XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UX500_.jpg"},
    {"rank":7,"title":"Rocketry: The Nambi Effect","year":2022,"rating":8.7,"img":"https://m.media-amazon.com/images/M/MV5BNmU2M2RhYmItNDU4Yy00YmY5LTg1OGQtYjE3Y2NhM2JjZjI0XkEyXkFqcGdeQXVyMTEzNzg0Mjkx@._V1_UX500_.jpg"},
    {"rank":8,"title":"12 Angry Men","year":1957,"rating":9.0,"img":"https://m.media-amazon.com/images/M/MV5BYjBkM2RjMzItM2M3Ni00N2NjLWE3NzMtMGY4MzE4MDAzMTRiXkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_UX500_.jpg"},
    {"rank":9,"title":"Nayakan","year":1987,"rating":8.6,"img":"https://m.media-amazon.com/images/M/MV5BODU2Y2VlZjQtMWJmNy00YmQ0LWFmYWUtY2U0YmI3MGZkM2QwXkEyXkFqcGdeQXVyODEzOTQwNTY@._V1_UX500_.jpg"},
    {"rank":10,"title":"Pulp Fiction","year":1994,"rating":8.9,"img":"https://m.media-amazon.com/images/M/MV5BNGNhMDIzYTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX500_.jpg"},
    {"rank":11,"title":"Inception","year":2010,"rating":8.8,"img":"https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_UX500_.jpg"},
    {"rank":12,"title":"777 Charlie","year":2022,"rating":8.7,"img":"https://m.media-amazon.com/images/M/MV5BMDljNTQ5YjYtZWZlOC00NWVjLTllYmUtYTBmZTY5MGY0NWRiXkEyXkFqcGdeQXVyMTEzNzg0Mjkx@._V1_UX500_.jpg"},
    {"rank":13,"title":"Fight Club","year":1999,"rating":8.8,"img":"https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00YTViLTgxMTItNGZlMWExNzk4M2ZkXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX500_.jpg"},
    {"rank":14,"title":"Manichitrathazhu","year":1993,"rating":8.7,"img":"https://m.media-amazon.com/images/M/MV5BNDhlN2NhMDAtY2Y3OS00N2I3LThhY2ItYTA1ZGY0ZDNmYmU4XkEyXkFqcGdeQXVyMjkxNzQ1NDI@._V1_UX500_.jpg"},
    {"rank":15,"title":"Forrest Gump","year":1994,"rating":8.8,"img":"https://m.media-amazon.com/images/M/MV5BNDYxNWshMTctNmE5OS00NzE0LWEwZTMtODE0YzY3MzVlNjJlXkEyXkFqcGdeQXVyMSM4MzEwNQ@@._V1_UX500_.jpg"},
    {"rank":16,"title":"3 Idiots","year":2009,"rating":8.4,"img":"https://m.media-amazon.com/images/M/MV5BNTkyOGVjM2ItZGYxMy00NTAyLThjN2QtNjQwZDUwZDhlYzUyXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_UX500_.jpg"},
    {"rank":17,"title":"The Matrix","year":1999,"rating":8.7,"img":"https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4@._V1_UX500_.jpg"},
    {"rank":18,"title":"Taare Zameen Par","year":2007,"rating":8.3,"img":"https://m.media-amazon.com/images/M/MV5BMjA0Nzk1OTM2Ml5BMl5BanBnXkFtZTcwNTEzMzY1MQ@@._V1_UX500_.jpg"},
    {"rank":19,"title":"Interstellar","year":2014,"rating":8.7,"img":"https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxOTQyODU@._V1_UX500_.jpg"},
    {"rank":20,"title":"Dangal","year":2016,"rating":8.3,"img":"https://m.media-amazon.com/images/M/MV5BMTQ4MzQzMzM2Nl5BMl5BanBnXkFtZTgwMTQ1NzU3MDI@._V1_UX500_.jpg"}
]

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
   
    feedbacks = Feedback.query.all()
    return render_template('dashboard.html', movies=MOVIES_DATA, feedbacks=feedbacks)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    movie_title = request.form.get('movie_title')
    vibe = request.form.get('vibe') 
    
    new_entry = Feedback(
        user_email=session['user_email'],
        movie_title=movie_title,
        rating=int(request.form.get('rating')),
        vibe=vibe,
        comment=request.form.get('comment')
    )
    db.session.add(new_entry)
    db.session.commit()
    flash(f'Pulse recorded! Your {vibe} vibe for {movie_title} is saved.', 'success')
    return redirect(url_for('dashboard'))
# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
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
    # Passing the raw MOVIES_DATA because Jinja2 will handle the image URLs
    return render_template('dashboard.html', movies=MOVIES_DATA)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    movie_title = request.form.get('movie_title')
    new_entry = Feedback(
        user_email=session['user_email'],
        movie_title=movie_title,
        rating=int(request.form.get('rating')),
        comment=request.form.get('comment')
    )
    db.session.add(new_entry)
    db.session.commit()
    flash(f'Pulse recorded for {movie_title}!', 'success')
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