from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
import uuid
import os
from datetime import datetime
from collections import Counter
from itsdangerous import URLSafeTimedSerializer
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'cinemapulse_2026_key'

# --- AWS Configuration ---
REGION = 'us-east-1' 


dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables (Ensure these are created in AWS Console)
# Partition Key for both should be 'email' or 'id' as specified below
users_table = dynamodb.Table('CinemaUsers')      # Partition Key: email (String)
feedback_table = dynamodb.Table('CinemaFeedback') # Partition Key: id (String)
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:aws_capstone_topic' # Replace with your Topic ARN

app.config['SECURITY_PASSWORD_SALT'] = 'cinema-pulse-salt-secure'

def send_sns_notification(subject, message):
    try:

        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)

    except ClientError as e:
        print(f"SNS Error: {e}")

# --- Token Logic ---
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=1800):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email

# --- Static Movie Data ---
MOVIES_DATA =  [
    {
        "rank": 1, "title": "The Shawshank Redemption", "year": 1994, "rating": 9.3,
        "lang": "English", "genre": "Drama",
        "desc": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSf1DK32xKMQzqSl8wnY1BLVu_gdwsRYzVSNM6A03r6c-fEwrif8raKzkFRuerw1KHdDICvOw&s=10"
    },
    {
        "rank": 2, "title": "Rocketry: The Nambi Effect", "year": 2022, "rating": 8.7,
        "lang": "Tamil / Hindi", "genre": "Biography / Drama",
        "desc": "Based on the life of ISRO scientist Nambi Narayanan who was falsely accused of espionage and fought for justice.",
        "img": "https://resizing.flixster.com/uFl3KWEoQIaP7EpRoUAFVN6g4uA=/ems.cHJkLWVtcy1hc3NldHMvbW92aWVzL2Q1NjdmZTUyLTgyYjgtNGQyNy04OWNjLTI2ODQyZDNkOTY1My5qcGc="
    },
    {
        "rank": 3, "title": "Nayakan", "year": 1987, "rating": 8.6,
        "lang": "Tamil", "genre": "Epic / Crime",
        "desc": "An odyssey of power and justice, where the lines between criminal and savior blur in the shadows of Bombay",
        "img": "https://i.pinimg.com/736x/4f/b2/b3/4fb2b3b8cf1ebf2aeec49673c52a79cb.jpg"
    },
    {
        "rank": 4, "title": "Jai Bhim", "year": 2021, "rating": 8.8,
        "lang": "Tamil", "genre": "Legal / Drama",
        "desc": "A brave activist-lawyer fights for justice when a tribal man is unlawfully detained and disappears from police custody.",
        "img": "https://static.pib.gov.in/WriteReadData/userfiles/image/jai-49C7H.jpg"
    },
    {
        "rank": 5, "title": "777 Charlie", "year": 2022, "rating": 8.7,
        "lang": "Kannada", "genre": "Adventure / Drama",
        "desc": "Dharma is stuck in a rut with his negative lifestyle until a stray dog named Charlie enters and changes his life forever.",
        "img": "https://m.media-amazon.com/images/S/pv-target-images/37690c1b70566b17065f54427b3209b18ee4b3780f530a7333ef2b73ec1d1917.jpg"
    },
    {
        "rank": 6, "title": "Manichitrathazhu", "year": 1993, "rating": 8.7,
        "lang": "Malayalam", "genre": "Horror / Thriller",
        "desc": "A psychiatrist arrives at a supposedly haunted ancestral home to solve a mystery involving his friend's wife.",
        "img": "https://m.media-amazon.com/images/M/MV5BNjllNGZiYjAtMjVjMy00ZGI4LThiZDAtYzFlOGRkY2E0NDA3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "rank": 7, "title": "3 Idiots", "year": 2009, "rating": 8.4,
        "lang": "Hindi", "genre": "Comedy / Drama",
        "desc": "Two friends search for their long-lost companion while revisiting their college days and the pressure of the education system.",
        "img": "https://play-lh.googleusercontent.com/2plinRZ5j5LJ9fLBKbY8LRSmUjcHoJHQGnJtviRlhO9WF7T9eYfzMbPoGKydzKcnVZCI4Z8LXzxUV4Q10pQ=w240-h480-rw"
    },
    {
        "rank": 8, "title": "Taare Zameen Par", "year": 2007, "rating": 8.3,
        "lang": "Hindi", "genre": "Family / Drama",
        "desc": "An unconventional art teacher helps an 8-year-old boy with dyslexia find his true potential.",
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLKhA9TsgkzaYnU6vWozqFidVVhRcNxqJywYjdYjNVnRftciOf"
    },
    {
        "rank": 9, "title": "Dangal", "year": 2016, "rating": 8.3,
        "lang": "Hindi", "genre": "Sports / Drama",
        "desc": "A former wrestler trains his daughters to become world-class wrestlers, defying social stigmas in their village.",
        "img": "https://m.media-amazon.com/images/M/MV5BMTQ4MzQzMzM2Nl5BMl5BanBnXkFtZTgwMTQ1NzU3MDI@._V1_QL75_UX380_CR0,0,380,562_.jpg"
    },
    {
        "rank": 10, "title": "Goodfellas", "year": 1990, "rating": 8.7,
        "lang": "English", "genre": "Biography / Crime",
        "desc": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen and his mob partners.",
        "img": "https://m.media-amazon.com/images/M/MV5BN2E5NzI2ZGMtY2VjNi00YTRjLWI1MDUtZGY5OWU1MWJjZjRjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "rank": 11, "title": "Avatar: Fire and Ash", "year": 2025, "rating": 10,
        "lang": "English", "genre": "Sci-Fi / Action",
        "desc": "Jake Sully and Neytiri encounter a new, aggressive Na'vi tribe—the Ash People—as survival on Pandora demands fire.",
        "img": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQJfdu01GP05dCCbubLMIXZgxz4SqKIpQx92wu9zHT7pXovv-Sn"
    },
    {
        "rank": 12, "title": "Jersey", "year": 2019, "rating": 9,
        "lang": "Telugu", "genre": "Sports / Drama",
        "desc": "A failed cricketer decides to return to the sport in his late thirties to fulfill his son's wish and prove his worth.",
        "img": "https://m.media-amazon.com/images/M/MV5BZmRiMGIzYWQtZTk1YS00ZTE0LWJlOTUtZmViZTZjOTA1YzAyXkEyXkFqcGc@._V1_.jpg"
    },
    {
        "rank": 13, "title": "Sardar Udham", "year": 2021, "rating": 8.4,
        "lang": "Hindi", "genre": "Historical / Drama",
        "desc": "A biographical drama about Udham Singh, who assassinated Michael O'Dwyer to avenge the Jallianwala Bagh massacre.",
        "img": "https://m.media-amazon.com/images/M/MV5BNWRkOWY0NjQtYzNjNC00MjA0LTk2MzgtNGZlMjM3YTBiMDA0XkEyXkFqcGc@._V1_.jpg"
    },
    {
        "rank": 14, "title": "Lagaan", "year": 2001, "rating": 8.9,
        "lang": "Hindi", "genre": "Epic / Sports",
        "desc": "Villagers in British India stake their future on a game of cricket against their arrogant rulers to avoid high taxes.",
        "img": "https://m.media-amazon.com/images/M/MV5BM2FmODM4OTktOTRjOS00ZTIzLWIzZjAtMDBhOGEzYThkNzMzXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "rank": 15, "title": "Vikram", "year": 2022, "rating": 10,
        "lang": "Tamil", "genre": "Action / Thriller",
        "desc": "A special ops squad tracks down masked vigilantes, uncovering a massive drug syndicate led by a ruthless drug lord.",
        "img": "https://m.media-amazon.com/images/M/MV5BNDEyMWQ0ZDktNTY0MC00YWRkLWFlMjQtMDUxMjRlMDhmMmRlXkEyXkFqcGc@._V1_.jpg"
    },
    {
        "rank": 16, "title": "The Godfather", "year": 1972, "rating": 9.2,
        "lang": "English", "genre": "Crime / Drama",
        "desc": "The aging patriarch of an organized crime dynasty transfers control of his empire to his reluctant youngest son.",
        "img": "https://m.media-amazon.com/images/M/MV5BNGEwYjgwOGQtYjg5ZS00Njc1LTk2ZGEtM2QwZWQ2NjdhZTE5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "rank": 17, "title": "Ponniyin Selvan: 2", "year": 2023, "rating": 10,
        "lang": "Tamil", "genre": "Historical / Action",
        "desc": "Arulmozhi Varman continues his journey to become Rajaraja I, facing deadly conspiracies against the Chola throne.",
        "img": "https://upload.wikimedia.org/wikipedia/en/5/5e/Ponniyin_Selvan_II.jpg"
    },
    {
        "rank": 18, "title": "Masaan", "year": 2015, "rating": 8.9,
        "lang": "Hindi", "genre": "Independent / Drama",
        "desc": "In Varanasi, four lives intersect along the Ganges as they attempt to escape the restrictions of a hidebound society.",
        "img": "https://thereviewmonk.com/assets/media/movies/posters/w300/b958298f4060803c8015f7ae8e732690.jpg"
    },
    {
        "rank": 19, "title": "M.S. Dhoni: The Untold Story", "year": 2016, "rating": 10,
        "lang": "Hindi", "genre": "Biography / Sports",
        "desc": "The life journey of Mahendra Singh Dhoni, from being a ticket collector to a World Cup-winning captain of India.",
        "img": "https://m.media-amazon.com/images/M/MV5BM2UwZTNkMmItYmYzOS00MTk3LTg3NDgtNzg5ZjYxNTIzNzY4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "rank": 20, "title": "Baahubali: The Epic", "year": 2025, "rating": 10,
        "lang": "Telugu", "genre": "Epic / Action",
        "desc": "A unified remastered version of the saga following Shivudu's quest to liberate the kingdom of Mahishmati.",
        "img": "https://m.media-amazon.com/images/M/MV5BNjYzNDM0MzktMzU5NC00YjAxLWEwZDItYjg3ODUxMDk5MjJmXkEyXkFqcGc@._V1_.jpg"
    }
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
        
        response = users_table.get_item(Key={'email': email})
        if 'Item' in response and response['Item']['password'] == password:
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    
    response = users_table.get_item(Key={'email': email})
    if 'Item' in response:
        return render_template('login.html', error="Account already exists.")
    
    users_table.put_item(Item={'email': email, 'password': password})
    session['user_email'] = email
    send_sns_notification("New CinemaPulse User", f"User {email} has joined the platform!")
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Fetch all feedback from DynamoDB
    all_feedbacks = feedback_table.scan().get('Items', [])
    
    movie_stats = {}
    vibe_labels = ['Mind-Blowing', 'Heartwarming', 'Tear-Jerker', 'Edge-of-Seat', 'Pure-Joy', 'Thought-Provoking']

    for movie in MOVIES_DATA:
        m_title = movie['title']
        m_vibes = [f['vibe'] for f in all_feedbacks if f['movie_title'] == m_title]
        
        if m_vibes:
            counts = Counter(m_vibes)
            total = len(m_vibes)
            movie_stats[m_title] = {v: (counts.get(v, 0) / total) * 100 for v in vibe_labels}
        else:
            movie_stats[m_title] = {v: 0 for v in vibe_labels}

    # Dynamic Metrics using scan (for production, consider a Global Secondary Index)
    top_movie = "N/A"
    if all_feedbacks:
        movie_counts = Counter([f['movie_title'] for f in all_feedbacks])
        top_movie = movie_counts.most_common(1)[0][0]

    return render_template('dashboard.html', 
                           movies=MOVIES_DATA, 
                           feedbacks=all_feedbacks,
                           top_movie=top_movie,
                           movie_stats=movie_stats)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in USERS:
            token = generate_token(email)
            reset_url = url_for('reset_with_token', token=token, _external=True)
            
            msg = Message("CinemaPulse - Reset Link", recipients=[email])
            msg.body = f"Click here to reset your password: {reset_url}\nValid for 30 minutes."
            mail.send(msg)
            
            return render_template('forgot_password.html', success_email=email)
        return render_template('forgot_password.html', error="Email not found.")
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = confirm_token(token)
    if not email:
        return "The reset link is invalid or has expired.", 400

    if request.method == 'POST':
        new_password = request.form.get('password')
        USERS[email] = new_password
        flash('Password successfully updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_new_password.html', token=token)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session['user_email']
    user_display_name = email.split('@')[0].capitalize()
    
    feedback_id = str(uuid.uuid4())
    new_entry = {
        'id': feedback_id,
        'user_name': user_display_name,
        'user_email': email,
        'movie_title': request.form.get('movie_title'),
        'rating': int(request.form.get('rating', 10)),
        'vibe': request.form.get('vibe'),
        'comment': request.form.get('comment'),
        'date_posted': datetime.utcnow().isoformat()
    }
    
    feedback_table.put_item(Item=new_entry)
    flash("Pulse recorded! Thank you for sharing.")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)