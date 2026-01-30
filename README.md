CinemaPulse 🎬
CinemaPulse is a web-based movie feedback and review platform designed to bridge the gap between cinephiles and their favorite films. Users can explore movies, share their insights, and engage with a community of film enthusiasts.

🚀 Features
User Authentication: Secure login and registration for personalized experiences.

Movie Insights: Detailed views for various films including descriptions and ratings.

Feedback System: Real-time posting of reviews and ratings for movies.

Responsive Design: Clean, modern UI that works across desktop and mobile devices.

Search & Filter: Easily find movies based on titles or genres.

🛠️ Tech Stack
Backend: Python, Flask

Frontend: HTML5, CSS3, JavaScript (Jinja2 templates)

Database: SQLite

Environment: Virtualenv

📦 Installation & Setup
Clone the repository

Bash
git clone https://github.com/haripriyav-git/cinemapulse.git
cd cinemapulse
Create a virtual environment



Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies



Bash
pip install -r requirements.txt
Initialize the database

Bash
# Run your database setup script or migrations
python database_setup.py
Run the application

Bash
python app.py
The app will be available at http://127.0.0.1:5000/.

📁 Project Structure
Plaintext
CinemaPulse/
├── app.py              # Main application entry point
├── models.py           # Database schemas
├── static/             # CSS, Images, and JS files
├── templates/          # HTML templates (Jinja2)
├── requirements.txt    # List of dependencies
└── README.md           # Project documentation
