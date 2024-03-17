import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY='qwerty'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False