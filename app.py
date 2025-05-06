from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Respond to incoming WhatsApp messages with a simple menu."""
    incoming_msg = request.form.get('Body')
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg:
        incoming_msg = incoming_msg.strip().lower()
        if incoming_msg in ["hi", "hello"]:
            msg.body("👋 Welcome to FunZ WhatsApp Banking Bot!\n\nPlease reply with:\n1. Open Account\n2. Transfer Money\n3.Sccan QR Code\n4. Check Balance\n5. Buy Airtime\n6. Buy Data\n7. Support")
        else:
            msg.body("❓Sorry, I didn't understand that. Type 'Hi' to begin.")
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)