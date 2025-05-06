from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WhatsAppAccountOpening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    bvn = db.Column(db.String(20))
    selfie_url = db.Column(db.String(255))
    account_number = db.Column(db.String(10), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)