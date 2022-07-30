from app import db, ma


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.String(100), primary_key=True)
    fullName = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    organization = db.Column(db.String(50))
    contact = db.Column(db.String(50))

    def __init__(self, id, fullName, email, password, organization, contact):
        self.id = id
        self.fullName = fullName
        self.email = email
        self.password = password
        self.organization = organization
        self.contact = contact


class AdminSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
