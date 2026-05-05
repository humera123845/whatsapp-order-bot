from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

ULTRAMSG_TOKEN = os.environ.get("ULTRAMSG_TOKEN")
ULTRAMSG_INSTANCE = os.environ.get("ULTRAMSG_INSTANCE")


def send_whatsapp(phone, message):
    if not ULTRAMSG_TOKEN or not ULTRAMSG_INSTANCE:
        raise RuntimeError("UltraMsg credentials are not configured")
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {"token": ULTRAMSG_TOKEN, "to": phone, "body": message}
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response


def parse_order(data):
    if not data:
        raise ValueError("Invalid or missing JSON body")
    phone = data.get("customer_phone")
    if not phone:
        raise ValueError("customer_phone is required")
    return {
        "customer_name": data.get("customer_name", "Customer"),
        "customer_phone": phone,
        "order_id": data.get("order_id", "N/A"),
        "order_total": data.get("order_total", "N/A"),
    }


def handle_webhook(message_template):
    data = request.get_json(silent=True)
    try:
        order = parse_order(data)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    message = message_template.format(**order)

    try:
        send_whatsapp(order["customer_phone"], message)
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "UltraMsg API request timed out"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "Could not connect to UltraMsg API"}), 502
    except requests.exceptions.HTTPError as e:
        return jsonify({"status": "error", "message": f"UltraMsg API error: {e.response.status_code}"}), 502

    return jsonify({"status": "success"}), 200


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Order Bot is Running!", 200


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    return handle_webhook(
        "Hello {customer_name}! Your order #{order_id} is confirmed. "
        "Total: {order_total}. Thank you!"
    )


@app.route("/webhook/confirm", methods=["POST"])
def webhook_confirm():
    return handle_webhook(
        "Hello {customer_name}! Your order #{order_id} has been CONFIRMED. "
        "Total: {order_total}. We will deliver soon. Thank you!"
    )


@app.route("/webhook/cancel", methods=["POST"])
def webhook_cancel():
    return handle_webhook(
        "Hello {customer_name}! Unfortunately your order #{order_id} has been CANCELLED. "
        "Total: {order_total}. Please contact us for refund or reorder. Sorry!"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
