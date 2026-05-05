from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "confirm" in incoming_msg:
        msg.body("✅ Confirmed! Thank you.")
    else:
        msg.body("Please reply CONFIRM to confirm.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
