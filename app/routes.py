import base64
from datetime import datetime, timedelta
from flask import app, render_template, redirect, url_for, flash, request, Blueprint, Flask, session
from flask_login import login_user, logout_user, login_required, current_user
import requests
from . import db
from .models import User
from app import oauth
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
import os


main = Blueprint('main', __name__)


google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@main.route('/')
def index():
    return render_template('main.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    
    messages = session.pop('_flashes', [])

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()

        if not user.password:
            flash('Login Unsuccessful. Please check email and password', 'danger')
        
        else:
            if user and check_password_hash(user.password, password):
                login_user(user, remember=remember)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')



@main.route('/signup', methods=['GET', 'POST'])
def signup():
    messages = session.pop('_flashes', [])

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email address already registered.", 'danger')
        
        else:
            if password == confirm_password and len(password) >= 6: 

                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = User(name=name, email=email, password=hashed_password, provider='local')
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('main.login'))
            else:
                flash('Passwords do not match the requirements!', 'danger')

    return render_template('register.html')


@main.route('/login/google')
def login_google():
    redirect_uri = url_for('main.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@main.route('/login/google/authorized')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']
    user = User.query.filter_by(email=email).first()

    profile_picture_url = user_info.get('picture')
    if profile_picture_url:
        profile_picture_data = requests.get(profile_picture_url).content
    else:
        profile_picture_data = None

    if not user:
        user = User(name=user_info['name'], email=email, provider='google', image=profile_picture_data)
        db.session.add(user)
        db.session.commit()
    else:
        user.profile_picture = user_info.get('picture')
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.dashboard'))



@main.route('/dashboard')
@login_required
def dashboard():
    user_data = mongo.db.users.find_one({"email": current_user.email})
    if user_data:
        flash('Welcome to your dashboard!', 'success')
        messages = session.pop('_flashes', [])
        return render_template('dashboard.html', data=current_user)
    
    else:
        new_user = {
            "_id":current_user.id,
            "name":current_user.name,
            "email":current_user.email,
            "provider":current_user.provider,
            'username': '',
            'location':'',
            'date_of_birth':'',
            'gender':'',
            'martial_status':'',
            'social_media_links':'',
            'user_type':'',
            'course':'',
            'course_specialization':'',
            'organization':'',
            'duration_start':'',
            'duration_end':'',
            'about':'',
            'skills':'',
            'interested_domain':''

        }
        mongo.db.users.insert_one(new_user)
        return render_template('dashboard.html', data=current_user)


@main.route('/news')
@login_required
def news():
    api_key = os.getenv('NEWS_API_KEY')
    url = 'https://newsapi.org/v2/top-headlines?country=us&category=technology'
    params = {  # You can change the country code as needed
        'apiKey': os.getenv('NEWS_API_KEY')
    }
    response = requests.get(url, params=params)
    news_data = response.json()

    articles = news_data.get('articles', [])

    return render_template('news.html', articles=articles)


@main.route('/profile')
@login_required
def profile():
    messages = session.pop('_flashes', []) 

    return render_template('profile.html', data=current_user)

@main.route('/rand')
@login_required
def rand():
    messages = session.pop('_flashes', []) 

    return render_template('maintemplate.html', data=current_user)


@main.route('/profile/edit-about', methods=['POST'])
@login_required
def edit_about():
    user_data = mongo.db.users.find_one({"_id": current_user.id})
    about = request.form.get('about')
    skills = request.form.getlist('skills_offered[]')
    domains = request.form.getlist('domains_offered[]')

    update_user = {
        'about':about,
        'skills':skills,
        'interested_domain':domains
    }
    mongo.db.users.update_one({"_id": current_user.id}, {"$set": update_user})
    user_data = mongo.db.users.find_one({'_id': current_user.id})

    return render_template('edit.html', data=current_user, user=user_data)


@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    messages = session.pop('_flashes', [])
    user_data = mongo.db.users.find_one({"_id": current_user.id})
    if request.method == 'POST':
        image = request.files.get('image')
        new_name = request.form.get('new_name')
        new_username = request.form.get('username')
        location = request.form.get('location')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        martial_status = request.form.get('martial')
        social_media = request.form.getlist('social_media_links[]')
        media_types = request.form.getlist('web-links-type[]')
        user_type = request.form.get('user-type')
        sector = request.form.get('fre-current_sector')
        course = request.form.get('course')
        course_spec = request.form.get('specialization')
        duration_start = request.form.get('duration-start')
        duration_end = request.form.get('duration-end')
        organisation = request.form.get('organisation')

        image_data = None
        if image and image.filename != '':
            image_data = image.read()
            print(f"Image Data Length: {len(image_data)}")  # Debug statement to print the length of image data
        else:
            print("No image uploaded or image filename is empty") 

        if image:
            current_user.image = image_data
                
        current_user.name = new_name

        try:
            db.session.commit()
            print('Updated')
            flash('User updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f'Error:{e}')
            flash(f'Error: {e}', 'danger')        

        social_media_links = []
        for i in range(len(media_types)):
            if media_types[i] != 'none' and social_media[i]:
                social_media_links.append({
                    'type': media_types[i],
                    'url': social_media[i]
                })

        update_user = {
                'name':new_name,
                'username': new_username,
                'location':location,
                'date_of_birth':dob,
                'gender':gender,
                'martial_status':martial_status,
                'social_media_links':social_media_links,
                'user_type':user_type,
                'course':course,
                'course_specialization':course_spec,
                'organization':organisation,
                'duration_start':duration_start,
                'duration_end':duration_end,

        }
        mongo.db.users.update_one({"_id": current_user.id}, {"$set": update_user})
        user_data = mongo.db.users.find_one({'_id': current_user.id})

    return render_template('edit.html', data=current_user, user=user_data)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.app_template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ''
