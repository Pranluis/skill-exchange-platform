import uuid
from app import mongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

uri = os.getenv("MONGO_DB_KEY")

client = MongoClient(uri, server_api=ServerApi('1'))
mongo_db = client.get_database('skillexchangedatabase')

def generate_unique_id():
    # Generate a UUID
    random_uuid = uuid.uuid4()
    
    # Convert UUID to integer and take the lower 32 bits
    unique_id = random_uuid.int & 0xFFFFFFFF
    
    return unique_id



def get_work_exp(user_id):
    experiences = list(mongo_db.work_experience.find({"user_id": user_id}))
    return experiences
    

def del_work_exp(work_id_add, user_id_add):
    mongo_db.work_experience.delete_one({"user_id": user_id_add, "work_id": work_id_add})
    
def college_date_only(user_id):
    new_update = {
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
    }
    mongo_db.users.update_one({"_id": user_id}, {"$set": new_update})


def pro_data_only(user_id):
    new_update = {
                'course':'',
                'course_specialization':'',
                'organization':'',
                'duration_start':'',
                'duration_end':'',
                'school_class':'',
                'school_organization':'',
                'fresher_intrested_sector':'',
                'fresher_course_specialization':'',
                'fresher_organization':'',
                'fre_duration_start':'',
                'fre_duration_end':'',
                'organization_sector':'',
                'type_of_organization':'',
                'organizer_organization':'',
    }
    mongo_db.users.update_one({"_id": user_id}, {"$set": new_update})


def fresher_data_only(user_id):
    new_update = {
                'course':'',
                'course_specialization':'',
                'organization':'',
                'duration_start':'',
                'duration_end':'',
                'school_class':'',
                'school_organization':'',
                'organization_sector':'',
                'type_of_organization':'',
                'organizer_organization':'',
                'professional_work_exp':'',
                'professional_sector':'',
                'professional_organization':'',
                'professional_designation':'',
    }
    mongo_db.users.update_one({"_id": user_id}, {"$set": new_update})

def school_data_only(user_id):
    new_update = {
                'course':'',
                'course_specialization':'',
                'organization':'',
                'duration_start':'',
                'duration_end':'',
                'organization_sector':'',
                'type_of_organization':'',
                'organizer_organization':'',
                'professional_work_exp':'',
                'professional_sector':'',
                'professional_organization':'',
                'professional_designation':'',
                'fresher_intrested_sector':'',
                'fresher_course_specialization':'',
                'fresher_organization':'',
                'fre_duration_start':'',
                'fre_duration_end':'',
    }
    mongo_db.users.update_one({"_id": user_id}, {"$set": new_update})


def organizer_data_only(user_id):
    new_update = {
                'course':'',
                'course_specialization':'',
                'organization':'',
                'duration_start':'',
                'duration_end':'',
                'professional_work_exp':'',
                'professional_sector':'',
                'professional_organization':'',
                'professional_designation':'',
                'fresher_intrested_sector':'',
                'fresher_course_specialization':'',
                'fresher_organization':'',
                'fre_duration_start':'',
                'fre_duration_end':'',
                'school_class':'',
                'school_organization':'',
    }
    mongo_db.users.update_one({"_id": user_id}, {"$set": new_update})
