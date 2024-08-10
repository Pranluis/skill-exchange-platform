import uuid
from app import mongo

def generate_unique_id():
    # Generate a UUID
    random_uuid = uuid.uuid4()
    
    # Convert UUID to integer and take the lower 32 bits
    unique_id = random_uuid.int & 0xFFFFFFFF
    
    return unique_id



def get_work_exp(user_id):
    experiences = list(mongo.db.work_experience.find({"user_id": user_id}))
    return experiences
    

def del_work_exp(work_id_add, user_id_add):
    mongo.db.work_experience.delete_one({"user_id": user_id_add, "work_id": work_id_add})
    

def get_logo_work_exp(user_id):
    experiences = list(mongo.db.work_experiences.find({'user_id': user_id}))
    
    # Mapping of company names to their logo URLs
    logos = {
        'google': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/368px-Google_2015_logo.svg.png',
        'microsoft': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/368px-Microsoft_logo.svg.png',
        'apple': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/368px-Apple_logo_black.svg.png',
        'amazon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/368px-Amazon_logo.svg.png',
        'facebook': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Facebook_Logo_2019.svg/368px-Facebook_Logo_2019.svg.png',
        # Add more companies and their logos here
    }

    # Add the logo URL to each work experience
    for exp in experiences:
        company_name = exp.get('company', '').lower()
        exp['logo_url'] = logos.get(company_name)

    return experiences
