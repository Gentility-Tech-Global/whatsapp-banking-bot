from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from models import db, WhatsAppAccountOpening
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsapp_accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

user_sessions = {}

def generate_unique_account_number():
    while True:
        number = str(random.randint(1000000000,9999999999))
        existing = WhatsAppAccountOpening.query.filter_by(account_number=number).first()
        if not existing:
            return number

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Respond to incoming WhatsApp messages with a simple menu."""
    from_number = request.form.get('From')
    incoming_msg = request.form.get('Body', '').strip()
    media_url = request.form.get('MediaUrl0')

    response = MessagingResponse()
    msg = response.message()

    #Initialize session
    if from_number not in user_sessions:
        user_sessions[from_number] = {'step': 'start'}

    session = user_sessions[from_number]

    #Flow Logic
    step = session['step']

    if step == 'start':
        if incoming_msg == '1':
            msg.body("📝 Let's open your FunZ account.\nPlease enter your full name:")
            session['step'] = 'get_name'
        else:
            msg.body("👋 Welcome to FunZ WhatsApp Banking Bot!\nPlease reply with:\n1. Open Account\n2. Transfer Money\n3.Scan QR Code\n4. Check Balance\n5. Buy Airtime\n6. Buy Data\n7. Support")

    elif step == 'get_name':
        session['full_name'] = incoming_msg
        msg.body("📅 Please enter your date of birth (Format: YYY-MM-DD):")
        session['step'] = 'get_dob'

    elif step == 'get_dob':
        session['dob'] = incoming_msg
        msg.body("📞 Please Enter your Phone number:")
        session['step'] = 'get_phone'

    elif step == 'get_phone':
        session['phone'] = incoming_msg
        msg.body("🔢 Please enter your 11-digit BVN number:")
        session['step'] = 'get_bvn'

    elif step == 'get_bvn':
        if len(incoming_msg) == 11 and incoming_msg.isdigit():
            session['bvn'] = incoming_msg
            msg.body("📸 Please take a selfie by clicking the 📸 icon below and upload it here:")
            session['step'] = 'get_selfie'
        else:
            msg.body("❌ Invalid BVN. Please enter a valid 11-digit BVN.")
    
    elif step == 'get_selfie':
        print("Entered get_selfie step")
        if media_url:
            session['selfie_url'] = media_url
            print("Media URL received:", media_url)

            # Simulated BVN verification logic (Replace with real API call Later)
            # In Production server, BVN/NIN validation is handled by:
            # The connected bank/fintech via their KYC engines
            # Using external services like verifyMe, IdentityPass, etc

            verification_passed = True

            if verification_passed:
                # 🔢 Simulate account number
                account_number = generate_unique_account_number()
                session['account_number'] = account_number

                # 🧾 Save to DB
                new_account = WhatsAppAccountOpening(
                    full_name=session['full_name'],
                    dob=session['dob'],
                    phone=session['phone'],
                    bvn=session['bvn'],
                    selfie_url=session['selfie_url'],
                    account_number=account_number
                )
                db.session.add(new_account)
                db.session.commit()
                print("✅ User saved to DB successfully")

                msg.body(
                    f"✅ Account created successfully!\n\n"
                    f"👤 Name: {session['full_name']}\n"
                    f"📱 Phone: {session['phone']}\n"
                    f"🏦 Account Number: {account_number}\n\n"
                    f"Type 'Hi' to return to the main menu."
                )

                session['step'] = 'start'

                # 🔗 [📣 FOR BANKS/FINTECHS:]
                # At this point, you can POST this data to the bank/partner’s system:
                # Example (pseudo-code):
                # requests.post('https://partner-api.bank.com/onboard-user', json={
                #     "full_name": session['full_name'],
                #     "dob": session['dob'],
                #     "bvn": session['bvn'],
                #     "phone": session['phone'],
                #     "account_number": account_number,
                #     "selfie_url": media_url
                # }, headers={"Authorization": "Bearer <API_KEY>"}) 
            else:
                msg.body("❌ BVN verification failed. Please try again.")
                session['step'] = 'start'
        else:
            print("⚠️ No media received")
            msg.body("⚠️ Please upload a selfie to proceed.")
    else:
        msg.body("❓ Type 'Hi' to restart.")
        session['step'] = 'start'

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)