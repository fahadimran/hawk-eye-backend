from app import db, ma


class RegisteredCase(db.Model):
    __tablename__ = 'registered-cases'
    case_id = db.Column(db.String(100), primary_key=True)
    fullName = db.Column(db.String(50))
    age = db.Column(db.String(10))
    details = db.Column(db.String(300))
    crime = db.Column(db.String(50))
    imageURL = db.Column(db.String(100))
    datetime = db.Column(db.String(100))

    def __init__(self, case_id, fullName, age, details, crime, imageURL, datetime):
        self.case_id = case_id
        self.fullName = fullName
        self.age = age
        self.details = details
        self.crime = crime
        self.imageURL = imageURL
        self.datetime = datetime


class RegisteredCaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RegisteredCase
