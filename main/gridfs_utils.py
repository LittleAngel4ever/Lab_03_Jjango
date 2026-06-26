from pymongo import MongoClient
from gridfs import GridFS
from django.conf import settings


def get_gridfs():
    client = MongoClient(settings.DATABASES['mongo']['CLIENT']['host'])
    db = client[settings.DATABASES['mongo']['NAME']]
    return GridFS(db)

def save_image(file_data, filename):
    fs = get_gridfs()
    return fs.put(file_data, filename=filename)

def get_image(file_id):
    fs = get_gridfs()
    try:
        return fs.get(file_id).read()
    except:
        return None

def delete_image(file_id):
    fs = get_gridfs()
    try:
        fs.delete(file_id)
    except:
        pass
