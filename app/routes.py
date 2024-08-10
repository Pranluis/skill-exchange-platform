import base64
from datetime import datetime, timedelta
from bson import ObjectId
from bson.objectid import ObjectId
from flask import abort, app, render_template, redirect, send_file, url_for, flash, request, Blueprint, Flask, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import requests
from . import db
from .models import User
from app import oauth
from app import mongo
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import os
import gridfs
from werkzeug.utils import secure_filename
from app.main_func import generate_unique_id, get_work_exp, del_work_exp, get_logo_work_exp


main = Blueprint('main', __name__)
logging.basicConfig(level=logging.DEBUG)

fs = gridfs.GridFS(mongo.db)

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
            'school_class':'',
            'school_organization':'',
            'professional_work_exp':'',
            'professional_sector':'',
            'professional_organization':'',
            'professional_designation':'',
            'fresher_intrested_sector':'',
            'fresher_course_specialization':'',
            'fresher_organization':'',
            'fre_duration_start':'',
            'fre_duration_end':'',
            'organization_sector':'',
            'type_of_organization':'',
            'organizer_organization':'',
            'about':'',
            'skills':'',
            'interested_domain':'',
            'phone_num':'',
            'alternative_phone_num':'',
            'permanent_address':'',
            'per_address_2':'',
            'country':'',
            'state':'',
            'city':'',
            'postal_code':'',
        }
        mongo.db.users.insert_one(new_user)
        return render_template('dashboard.html', data=current_user)


@main.route('/news')
@login_required
def news():
    api_key = os.getenv('NEWS_API_KEY')
    url = f'https://newsapi.org/v2/top-headlines?country=us&category=technology'
    params = {  # You can change the country code as needed
        'apiKey': api_key
    }
    response = requests.get(url, params=params)
    news_data = response.json()

    articles = news_data.get('articles', [])

    return render_template('news.html', articles=articles)


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
    phone_num = request.form.get('phone_num')
    alt_phone_num = request.form.get('alt-phone-num')
    per_address = request.form.get('per-address')
    per_address_2 = request.form.get('per-address-2')
    country = request.form.get('country')
    state = request.form.get('state')
    city = request.form.get('city')
    pos_code = request.form.get('pos-code')

    update_user = {
        'about':about,
        'skills':skills,
        'interested_domain':domains,
        'phone_num':phone_num,
        'alternative_phone_num':alt_phone_num,
        'permanent_address':per_address,
        'per_address_2':per_address_2,
        'country':country,
        'state':state,
        'city':city,
        'postal_code':pos_code,

    }
    mongo.db.users.update_one({"_id": current_user.id}, {"$set": update_user})
    user_data = mongo.db.users.find_one({'_id': current_user.id})
    experiences = get_work_exp(current_user.id)

    return render_template('edit.html', data=current_user, user=user_data, experiences=experiences)



@main.route('/work_experience', methods=['POST', 'GET'])
@login_required
def add_work_experience():
    messages = session.pop('_flashes', [])
    experiences = get_work_exp(current_user.id)
    if request.method == 'POST':
        work_id = generate_unique_id()
        postion = request.form.get('position')
        company = request.form.get('company')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        des = request.form.get('description')

        new_work_exp = {
            'user_id':current_user.id,
            'work_id':work_id,
            'position':postion,
            'company':company,
            'start_date':start_date,
            'end_date':end_date,
            'description':des
        }
        mongo.db.work_experience.insert_one(new_work_exp)
        user_data = mongo.db.users.find_one({'_id': current_user.id})

    experiences = get_work_exp(current_user.id)
    return redirect(url_for('main.edit'))


@main.route('/work_del_experience/<int:work_id>', methods=['GET'])
@login_required
def delete_work_experience(work_id):
    user_id = current_user.id
    del_work_exp(work_id, user_id)

    return redirect(url_for('main.edit'))


@main.route('/delete_certificate/<file_id>', methods=['DELETE'])
@login_required
def delete_certificate(file_id):
    try:
        object_id = ObjectId(file_id)
        
        fs.delete(object_id)
        logging.info(f"File with ID {file_id} deleted from GridFS")
        
        result = mongo.db.certificates.delete_one({'file_id': file_id})
        if result.deleted_count == 0:
            logging.warning(f"No document found with file_id {file_id}")
            return jsonify({'message': 'Document not found'}), 404
        
        logging.info(f"Document with file_id {file_id} deleted from MongoDB")
        return jsonify({'message': 'Certificate deleted successfully'}), 200
    
    except gridfs.errors.NoFile:
        logging.error(f"File with ID {file_id} not found in GridFS")
        return jsonify({'message': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error deleting certificate: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@main.route('/add_certificate', methods=['POST'])
@login_required
def add_certificate():
    user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))
    title = request.form['certificate_title']
    institution = request.form['certificate_institution']
    issue_date = request.form['certificate_issue_date']
    description = request.form['certificate_description']
    skills = request.form.getlist('skills_learned[]')
    file = request.files['certificate_file']

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_id = fs.put(file, filename=filename) # type: ignore

        certificate = {
            'user_id': current_user.id,
            'title': title,
            'institution': institution,
            'issue_date': issue_date,
            'description': description,
            'skills': skills,
            'file_id': str(file_id)
        }

        mongo.db.certificates.insert_one(certificate)
        user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))
        flash('Certificate uploaded successfully!', 'success')
        return redirect(url_for('main.edit'))
    else:
        user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))
        flash('Invalid file type. Only PDFs are allowed.', 'danger')
        return redirect(url_for('main.edit'))

@main.route('/certificate/<file_id>')
@login_required
def get_certificate(file_id):
    try:
        object_id = ObjectId(file_id)
        pdf_file = fs.get(object_id)  
        
        if not pdf_file:
            abort(404)

        return send_file(pdf_file, download_name=f"{file_id}.pdf", as_attachment=False)
    except gridfs.errors.NoFile:
        logging.error(f"File with ID {file_id} not found in GridFS")
        abort(404)
    except Exception as e:
        logging.error(f"Error retrieving file: {e}")
        abort(500)


@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    messages = session.pop('_flashes', [])
    user_data = mongo.db.users.find_one({"_id": current_user.id})
    experiences = get_work_exp(current_user.id)
    user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))
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
        fre_sector = request.form.get('fre-current_sector')
        course = request.form.get('course')
        course_spec = request.form.get('specialization')
        duration_start = request.form.get('duration-start')
        duration_end = request.form.get('duration-end')
        organisation = request.form.get('organisation')
        school_class = request.form.get('school_class')
        school_org = request.form.get('sch-organisation')
        pro_work_exp = request.form.get('work_experience')
        pro_current_sector = request.form.get('current_sector')
        pro_org = request.form.get('pro-organisation')
        pro_desg = request.form.get('designation')
        fre_course_spc = request.form.get('fre-specialization')
        fre_org = request.form.get('fre-organisation')
        fre_duration_strt = request.form.get('fre-duration-start')
        fre_duration_end = request.form.get('fre-duration-end')
        org_sector = request.form.get('op-current_sector')
        typ_of_org = request.form.get('organization_type')
        op_organization = request.form.get('op-organisation')


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
                'school_class':school_class,
                'school_organization':school_org,
                'professional_work_exp':pro_work_exp,
                'professional_sector':pro_current_sector,
                'professional_organization':pro_org,
                'professional_designation':pro_desg,
                'fresher_intrested_sector':fre_sector,
                'fresher_course_specialization':fre_course_spc,
                'fresher_organization':fre_org,
                'fre_duration_start':fre_duration_strt,
                'fre_duration_end':fre_duration_end,
                'organization_sector':org_sector,
                'type_of_organization':typ_of_org,
                'organizer_organization':op_organization,

        }

        mongo.db.users.update_one({"_id": current_user.id}, {"$set": update_user})
        user_data = mongo.db.users.find_one({'_id': current_user.id})
        experiences = get_work_exp(current_user.id)
        user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))


    return render_template('edit.html', data=current_user, user=user_data, experiences=experiences, certificates=user_certificates)


@main.route('/profile')
@login_required
def profile():
    user_data = mongo.db.users.find_one({'_id': current_user.id})
    experiences = get_work_exp(current_user.id)
    user_certificates = list(mongo.db.certificates.find({'user_id': current_user.id}))

    return render_template('profile.html', user=user_data, work_exp=experiences, certificates=user_certificates)


@main.route('/search-user')
@login_required
def search_user():
    documents = list(mongo.db.users.find())

    return render_template('searchuser.html', users = documents)
       


@main.route('/profile-other/<int:id>')
@login_required
def profile_other(id):
    user_data = mongo.db.users.find_one({'_id': id})
    experiences = get_work_exp(id)
    user_certificates = list(mongo.db.certificates.find({'user_id': id}))

    return render_template('profile.html', user=user_data, work_exp=experiences, certificates=user_certificates)


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
