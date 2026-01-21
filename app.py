from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import Counter

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
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    vibe = db.Column(db.String(50))  
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- Temporary User Store ---
USERS = {"admin@cinema.com": "pulse123"}


MOVIES_DATA = [
    {"rank":1,"title":"The Shawshank Redemption","year":1994,"rating":9.3,"img":"https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRedemptionMoviePoster.jpg"},
    {"rank":2,"title":"Rocketry: The Nambi Effect","year":2022,"rating":8.7,"img":"https://resizing.flixster.com/uFl3KWEoQIaP7EpRoUAFVN6g4uA=/ems.cHJkLWVtcy1hc3NldHMvbW92aWVzL2Q1NjdmZTUyLTgyYjgtNGQyNy04OWNjLTI2ODQyZDNkOTY1My5qcGc="},
    {"rank":3,"title":"Nayakan","year":1987,"rating":8.6,"img":"https://m.media-amazon.com/images/M/MV5BNTM3MTU1NWYtZjE3ZC00ODYzLTg0NWYtNDhiYTMxMTAzYzIzXkEyXkFqcGc@._V1_.jpg"},
    {"rank":4,"title":"Jai Bhim","year":2021,"rating":8.8,"img":"https://miro.medium.com/1*y0eu9R_ZzN36LD3dj5x7hw.jpeg"},
    {"rank":5,"title":"777 Charlie","year":2022,"rating":8.7,"img":"https://cdn.sacnilk.com/image/movie/2022/6249.jpg"},
    {"rank":6,"title":"Manichitrathazhu","year":1993,"rating":8.7,"img":"https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcTFuLrVXuPP1tra9hdNn57WNh89EtehGHsc_k-VtnWQLgAPXV2N"},
    {"rank":7,"title":"3 Idiots","year":2009,"rating":8.4,"img":"https://bollywoodmoviesposter.com/wp-content/uploads/2025/04/IMG-20250407-WA0056.jpg"},
    {"rank":9,"title":"Dangal","year":2016,"rating":8.3,"img":"https://m.media-amazon.com/images/M/MV5BMTQ4MzQzMzM2Nl5BMl5BanBnXkFtZTgwMTQ1NzU3MDI@._V1_QL75_UX380_CR0,0,380,562_.jpg"},
    {"rank":10,"title": "Goodfellas", "year": 1990, "rating": 8.7, "img": "https://m.media-amazon.com/images/M/MV5BN2E5NzI2ZGMtY2VjNi00YTRjLWI1MDUtZGY5OWU1MWJjZjRjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
    {"rank":11,"title":"Avatar: Fire and Ash","year":2025,"rating":10,"img":"https://upload.wikimedia.org/wikipedia/en/thumb/9/95/Avatar_Fire_and_Ash_poster.jpeg/250px-Avatar_Fire_and_Ash_poster.jpeg"},
    {"rank":12,"title":"Jersey","year":2019,"rating":9,"img":"https://m.media-amazon.com/images/M/MV5BZmRiMGIzYWQtZTk1YS00ZTE0LWJlOTUtZmViZTZjOTA1YzAyXkEyXkFqcGc@._V1_.jpg"},
    {"rank":13,"title":"Sardar Udham","year":2021,"rating":8.4,"img":"https://m.media-amazon.com/images/M/MV5BNWRkOWY0NjQtYzNjNC00MjA0LTk2MzgtNGZlMjM3YTBiMDA0XkEyXkFqcGc@._V1_.jpg"},
    {"rank":14,"title":"Lagaan","year":2001,"rating":8.9,"img":"https://m.media-amazon.com/images/M/MV5BM2FmODM4OTktOTRjOS00ZTIzLWIzZjAtMDBhOGEzYThkNzMzXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
    {"rank":15,"title":"Vikram","year":2022,"rating":10,"img":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQWd4P3cuGFbsMtu8doLKdoFi-EU-_PJorQ_A&s"},
    {"rank":16,"title":"The Godfather","year":1972,"rating":9.2,"img":"https://m.media-amazon.com/images/M/MV5BNGEwYjgwOGQtYjg5ZS00Njc1LTk2ZGEtM2QwZWQ2NjdhZTE5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
    {"rank":17,"title":"Ponniyin Selvan 2","year":2023,"rating":10,"img":"https://upload.wikimedia.org/wikipedia/en/5/5e/Ponniyin_Selvan_II.jpg"},
    {"rank":18,"title":"Masaan","year":2015,"rating":8.9,"img":"https://thereviewmonk.com/assets/media/movies/posters/w300/b958298f4060803c8015f7ae8e732690.jpg"},
    {"rank":19,"title":"M.S. Dhoni: The Untold Story","year":2016,"rating":10,"img":"https://m.media-amazon.com/images/M/MV5BM2UwZTNkMmItYmYzOS00MTk3LTg3NDgtNzg5ZjYxNTIzNzY4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
    {"rank":20,"title":"Baahubali: The Epic","year":2025,"rating":10,"img":"https://m.media-amazon.com/images/M/MV5BNjYzNDM0MzktMzU5NC00YjAxLWEwZDItYjg3ODUxMDk5MjJmXkEyXkFqcGc@._V1_.jpg"}
]

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
    
    all_feedbacks = Feedback.query.all()
    movie_stats = {}
    
    for movie in MOVIES_DATA:
        vibe_list = [f.vibe for f in all_feedbacks if f.movie_title == movie['title']]
        total = len(vibe_list)
        if total > 0:
            counts = Counter(vibe_list)
            movie_stats[movie['title']] = {vibe: round((count / total) * 100) for vibe, count in counts.items()}
        else:
            movie_stats[movie['title']] = {}

    return render_template('dashboard.html', 
                           movies=MOVIES_DATA, 
                           feedbacks=all_feedbacks, 
                           movie_stats=movie_stats) 

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_display_name = session.get('user_name')
    if not user_display_name:
        user_display_name = session['user_email'].split('@')[0].capitalize()

    new_entry = Feedback(
        user_name=user_display_name,
        user_email=session['user_email'],
        movie_title=request.form.get('movie_title'),
        rating=int(request.form.get('rating')),
        vibe=request.form.get('vibe'),
        comment=request.form.get('comment')
    )
    db.session.add(new_entry)
    db.session.commit()
    
    flash(f'Pulse recorded by {user_display_name}!', 'success')
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