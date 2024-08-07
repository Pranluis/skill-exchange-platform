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
    
