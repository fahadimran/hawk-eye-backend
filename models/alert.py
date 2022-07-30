from app import db, ma


class Alert(db.Model):
    __tablename__ = 'alerts'
    alert_id = db.Column(db.String(100), primary_key=True)
    case_id = db.Column(db.String(100))
    status = db.Column(db.String(50))
    date_generated = db.Column(db.String(50))
    date_closed = db.Column(db.String(50))
    closed_by = db.Column(db.String(50))
    reason_closure = db.Column(db.String(50))
    comments = db.Column(db.String(300))

    def __init__(self, alert_id, case_id, status, date_generated, date_closed, closed_by, reason_closure, comments):
        self.alert_id = alert_id
        self.case_id = case_id
        self.status = status
        self.date_generated = date_generated
        self.date_closed = date_closed
        self.closed_by = closed_by
        self.reason_closure = reason_closure
        self.comments = comments


class AlertSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
