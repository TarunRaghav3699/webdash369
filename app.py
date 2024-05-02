import os
# import redis
# from flask_redis import FlaskRedis 
import bcrypt
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_session import Session
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, session, flash

load_dotenv()
app = Flask(__name__)

# redish database from here 

# Session Configuration

# app.config['REDIS_URL'] = os.getenv('REDIS_URL')  # Set your Redis URL from environment variables
# redis_url = os.getenv("REDIS_URL") # Redis URI
# if not redis_url:
#     raise RuntimeError("Environment variable REDIS_URL not set")

# print("Redis URL:", redis_url)

# app.config["SESSION_TYPE"] = "redis"
# app.config["SESSION_REDIS"] = redis.from_url(redis_url)
# app.config["SESSION_COOKIE_SECURE"] = True
# app.config["SESSION_COOKIE_HTTPONLY"] = True
# app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Session(app)
# redis_store = FlaskRedis(app)

# to here

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['fitness-gym']
collection = db['signup']
contact_us = db['contact']

app.secret_key = os.getenv('SECRET_KEY')

# for sending emails to the user
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
mail = Mail(app)


# Modify your MongoDB query function to include caching

# def get_user_from_mongodb(username):
#     # Check if the user exists in the Redis cache
#     cached_user = redis_store.get(username)
#     if cached_user:
#         return cached_user.decode('utf-8')  # Decode the cached user from bytes to string

#     # If the user is not cached, query MongoDB
#     user = collection.find_one({'username': username})

#     # Cache the user in Redis for future access
#     if user:
#         redis_store.set(username, str(user))  # Convert user to string and store in Redis

#     return user




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password").encode('utf-8')
        
        user = collection.find_one({'username': username})
        
        if user and bcrypt.checkpw(password, user['password']):
            session['username'] = username
            return redirect(url_for('dashboard', username=username))
        else:
            flash_message = 'Username or password is incorrect. Please try again.'
            return render_template('signup.html', flash_message=flash_message)

    return render_template("signup.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        username = request.form.get("username")

        # Check if the user with the same username already exists
        if collection.find_one({'username': username}):
            flash_message = 'Username already exists. Please choose another one.'
            return render_template('signup.html', flash_message=flash_message)
        pswd = bcrypt.hashpw(request.form.get("password").encode('utf-8'), bcrypt.gensalt())
        # password = request.form.get("password")
        collection.insert_one({"phone number": phone_number, "email": email, "username": username, "password": pswd})

        try:
            msg_title = 'Hey ' + username
            sender = 'tarunraghav702@gmail.com'
            msg = Message(msg_title, sender=sender, recipients=[email])
            data = {
                'app_name': "Fitness-Gym",
                'title': msg_title,
                'username': username
            }
            msg.html = render_template('thankemail.html', data=data)
            mail.send(msg)
            print("Email sent successfully.")
        except Exception as e:
            print("Error sending email:", e)
            flash("There was an error sending your message. Please try again later.", "error")
            return redirect(url_for('contact'))  # Redirect back to the contact page with a flash message

        flash("Your message has been sent successfully!", "success")        

        # Redirect to the dashboard after successful signup
        session['username'] = username
        return redirect(url_for('dashboard', username=username))

    return render_template("signup.html")

@app.route("/", methods=["GET", "POST"])
def dashboard():
    username = session.get('username')
    if username:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        date = datetime.now()
        result = contact_us.insert_one({"name": name, "email": email, "subject": subject, "message": message, "date": date})
        print("Inserted document ID:", result.inserted_id)
        
        try:
            msg_title = 'Hey ' + name
            sender = 'tarunraghav702@gmail.com'
            msg = Message(msg_title, sender=sender, recipients=[email])
            msg_body = message
            data = {
                'app_name': "Fitness-Gym",
                'title': msg_title,
                'body': msg_body
            }
            msg.html = render_template('email.html', data=data)
            mail.send(msg)
            print("Email sent successfully.")
        except Exception as e:
            print("Error sending email:", e)
            flash("There was an error sending your message. Please try again later.", "error")
            return redirect(url_for('contact'))  # Redirect back to the contact page with a flash message

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route("/bmi")
def bmi():
    return render_template('bmi.html')
    
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
