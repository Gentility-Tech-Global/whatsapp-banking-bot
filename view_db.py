from models import db, WhatsAppAccountOpening
from app import app
with app.app_context():
    users = WhatsAppAccountOpening.query.all()
    for user in users:
        print(f"{user.full_name} | {user.phone} | {user.bvn} {user.account_number} | {user.created_at} | {user.selfie_url}")