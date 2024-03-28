from app.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    claims = db.relationship('Claim', backref='user', lazy=True)
    appeals = db.relationship('Appeal', backref='user', lazy=True)
    managed_employees = db.relationship('User', lazy=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return self.username


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    # Name is format: "First Middle Last", with capital first letters and spaces between.

    def __repr__(self):
        return self.name
