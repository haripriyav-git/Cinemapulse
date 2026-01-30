from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
import uuid
import os
from datetime import datetime
from collections import Counter
from itsdangerous import URLSafeTimedSerializer
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Security settings
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cinemapulse_2026_key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('FLASK_SALT', 'cinema-pulse-salt-secure')

# --- AWS Configuration ---
REGION = 'us-east-1' 
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

users_table = dynamodb.Table('CinemaUsers')      
feedback_table = dynamodb.Table('CinemaFeedback') 
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:aws_capstone_topic'

def send_sns_notification(subject, message):
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    except ClientError as e:
        print(f"SNS Error: {e}")

# --- Token Logic ---
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=1800):
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email

# --- Static Movie Data ---
MOVIES_DATA = [
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

# --- AWS Ready API for Individual Doughnut/Radar Charts ---
@app.route('/api/radar-comparison')
def radar_comparison():
    movie_title = request.args.get('m1')
    labels = ['Mind-Blowing', 'Heartwarming', 'Tear-Jerker', 'Edge-of-Seat', 'Pure-Joy', 'Thought-Provoking']
    
    if not movie_title:
        return jsonify({'labels': labels, 'datasets': [{'data': [0] * 6}]})

    try:
        # Use DynamoDB Scan with Filter instead of SQL
        response = feedback_table.scan(FilterExpression=Attr('movie_title').eq(movie_title))
        items = response.get('Items', [])
        counts_dict = Counter([item['vibe'] for item in items if 'vibe' in item])
        data = [counts_dict.get(label, 0) for label in labels]

        return jsonify({
            'labels': labels,
            'datasets': [{
                'label': movie_title,
                'data': data,
                'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
            }]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Standard Routes ---

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
        if 'Item' in response and check_password_hash(response['Item']['password'], password):
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if 'Item' in users_table.get_item(Key={'email': email}):
        flash("Account already exists.", "warning")
        return redirect(url_for('login'))
    
    users_table.put_item(Item={'email': email, 'password': generate_password_hash(password)})
    session['user_email'] = email
    send_sns_notification("New CinemaPulse User", f"User {email} has joined!")
    return redirect(url_for('dashboard'))

# ... (Keep your imports and AWS config as they are)

# --- Added Forgot Password Route ---
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Check if user exists in DynamoDB
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' in response:
            token = generate_token(email)
            # Use _external=True to generate a full URL (http://your-ec2-ip:5000/...)
            reset_url = url_for('reset_with_token', token=token, _external=True)
            
            # Send the reset link via SNS
            subject = "CinemaPulse - Password Reset Request"
            message = f"Hello,\n\nYou requested a password reset. Click the link below to set a new password:\n{reset_url}\n\nThis link expires in 30 minutes."
            send_sns_notification(subject, message)
            
            flash("If that email is registered, a reset link has been sent via SNS.", "info")
            return redirect(url_for('login'))
        
        flash("Email not found.", "danger")
    return render_template('forgot_password.html')

# --- Added Reset Password Route ---
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    # Verify the token
    email = confirm_token(token)
    if not email:
        flash("The reset link is invalid or has expired.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = generate_password_hash(new_password)
        
        # Update the password in DynamoDB
        try:
            users_table.update_item(
                Key={'email': email},
                UpdateExpression="set password = :p",
                ExpressionAttributeValues={':p': hashed_password}
            )
            flash("Your password has been updated! You can now login.", "success")
            return redirect(url_for('login'))
        except ClientError as e:
            print(e.response['Error']['Message'])
            flash("An error occurred. Please try again.", "danger")

    return render_template('reset_new_password.html', token=token)

# ... (Rest of your standard routes: login, signup, dashboard, etc.)

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    try:
        all_feedbacks = feedback_table.scan().get('Items', [])
    except:
        all_feedbacks = []

    movie_stats = {}
    vibe_labels = ['Mind-Blowing', 'Heartwarming', 'Tear-Jerker', 'Edge-of-Seat', 'Pure-Joy', 'Thought-Provoking']

    for movie in MOVIES_DATA:
        m_title = movie['title']
        m_vibes = [f['vibe'] for f in all_feedbacks if f['movie_title'] == m_title]
        counts = Counter(m_vibes)
        total = len(m_vibes) or 1
        movie_stats[m_title] = {v: (counts.get(v, 0) / total) * 100 for v in vibe_labels}

    top_movie = Counter([f['movie_title'] for f in all_feedbacks]).most_common(1)[0][0] if all_feedbacks else "N/A"
    return render_template('dashboard.html', movies=MOVIES_DATA, feedbacks=all_feedbacks, top_movie=top_movie, movie_stats=movie_stats)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session: return redirect(url_for('login'))
    email = session['user_email']
    feedback_table.put_item(Item={
        'id': str(uuid.uuid4()),
        'user_name': email.split('@')[0].capitalize(),
        'user_email': email,
        'movie_title': request.form.get('movie_title'),
        'rating': int(request.form.get('rating', 10)),
        'vibe': request.form.get('vibe'),
        'comment': request.form.get('comment'),
        'date_posted': datetime.utcnow().isoformat()
    })
    flash("Pulse recorded!")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)