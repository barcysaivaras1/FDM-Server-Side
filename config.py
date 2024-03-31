import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = 'qwerty'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    UPLOAD_FOLDER = 'app/static/profile-pictures'

    # SESSION_PROTECTION = None
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)