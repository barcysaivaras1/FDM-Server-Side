from app.extensions import db


class Bug(db.Model):
    __tablename__ = 'bug'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
