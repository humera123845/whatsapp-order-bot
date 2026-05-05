from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Order received:", data)
    # your WhatsApp sending code goes here
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run()