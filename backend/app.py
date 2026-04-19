from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import razorpay
import hmac
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Razorpay client
client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

# ─── Plans ───────────────────────────────────────────────────────────────────
PLANS = {
    "basic":   {"name": "Basic",   "amount": 9900},   # ₹99
    "premium": {"name": "Premium", "amount": 49900},  # ₹499
    "custom":  {"name": "Custom",  "amount": 99900},  # ₹999
}

# ─── Create Order ─────────────────────────────────────────────────────────────
@app.route("/api/create-order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        plan_id = data.get("plan", "basic")
        plan    = PLANS.get(plan_id, PLANS["basic"])

        order = client.order.create({
            "amount":   plan["amount"],
            "currency": "INR",
            "payment_capture": 1
        })

        return jsonify({
            "order_id":  order["id"],
            "amount":    plan["amount"],
            "currency":  "INR",
            "plan_name": plan["name"],
            "key_id":    os.getenv("RAZORPAY_KEY_ID")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Verify Payment ───────────────────────────────────────────────────────────
@app.route("/api/verify-payment", methods=["POST"])
def verify_payment():
    try:
        data       = request.get_json()
        payment_id = data.get("razorpay_payment_id")
        order_id   = data.get("razorpay_order_id")
        signature  = data.get("razorpay_signature")
        user_name  = data.get("name")
        user_email = data.get("email")
        amount     = data.get("amount")

        # Signature verify karo
        msg    = f"{order_id}|{payment_id}"
        secret = os.getenv("RAZORPAY_KEY_SECRET").encode()
        gen_sig = hmac.new(secret, msg.encode(), hashlib.sha256).hexdigest()

        if gen_sig != signature:
            return jsonify({"error": "Payment verification failed!"}), 400

        # Email bhejo
        send_confirmation_email(user_name, user_email, payment_id, amount)

        return jsonify({
            "success": True,
            "message": "Payment verified! Email sent."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Webhook ──────────────────────────────────────────────────────────────────
@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        webhook_secret    = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        webhook_signature = request.headers.get("X-Razorpay-Signature", "")
        payload           = request.get_data()

        # Webhook signature verify
        gen_sig = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if gen_sig != webhook_signature:
            return jsonify({"error": "Invalid webhook signature"}), 400

        event = request.get_json()

        if event.get("event") == "payment.captured":
            payment = event["payload"]["payment"]["entity"]
            print(f"✅ Payment captured: {payment['id']}")

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Email ────────────────────────────────────────────────────────────────────
def send_confirmation_email(name, email, payment_id, amount):
    gmail_user     = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ Payment Confirmation - Subscription App"
    msg["From"]    = gmail_user
    msg["To"]      = email

    amount_inr = int(amount) / 100  # paise to rupees

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 30px; background: #f4f4f4;">
        <div style="max-width: 500px; margin: auto; background: white;
                    padding: 30px; border-radius: 10px;">
            <h2 style="color: #4CAF50;">✅ Payment Successful!</h2>
            <p>Hi <strong>{name}</strong>,</p>
            <p>Thank you for subscribing! Here are your payment details:</p>
            <table style="width:100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; color: #555;">Payment ID</td>
                    <td style="padding: 8px;"><strong>{payment_id}</strong></td>
                </tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding: 8px; color: #555;">Amount Paid</td>
                    <td style="padding: 8px;"><strong>₹{amount_inr:.2f}</strong></td>
                </tr>
            </table>
            <p style="margin-top: 20px;">We're glad to have you on board! 🎉</p>
            <p style="color: #888; font-size: 12px;">— Subscription App Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, msg.as_string())

    print(f"📧 Email sent to {email}")


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)