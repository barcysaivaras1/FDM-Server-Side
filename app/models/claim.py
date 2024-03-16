from app.extensions import db

class Claim(db.Model):
    __tablename__ = "Claim"
    id = db.Column(db.Integer, primary_key=True)