# Subscription App

A full-stack subscription payment application built with React and Flask, integrated with Razorpay payment gateway and Gmail email confirmation.

## Tech Stack

- **Frontend:** React (Vite)
- **Backend:** Python (Flask)
- **Payment:** Razorpay (Test Mode)
- **Email:** Gmail SMTP
- **Webhook Testing:** Ngrok

## Features

- Subscription plans — Basic, Premium, Custom
- Razorpay payment integration with popup
- Payment signature verification on backend
- Automatic email confirmation after payment
- Webhook support for server-side payment confirmation

## Project Structure

```
subscription-app/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── SubscriptionPage.jsx
        └── SubscriptionPage.css
```

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/soumyagithub123/subscription-app.git
cd subscription-app
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create `.env` file in `backend/` folder:

```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxx
GMAIL_USER=youremail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
FLASK_SECRET_KEY=your_secret_key
```

Run the backend:

```bash
python app.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

Create `.env` file in `frontend/` folder:

```
VITE_RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
VITE_BACKEND_URL=http://localhost:5000
```

Run the frontend:

```bash
npm run dev
```

### 4. Webhook Setup (Optional - for local testing)

```bash
# Run ngrok
ngrok http 5000
```

Add the ngrok URL in Razorpay Dashboard:
```
https://your-ngrok-url.ngrok-free.app/api/webhook
```

## Payment Flow

```
User fills form → Clicks Pay
→ Backend creates Razorpay order
→ Razorpay popup opens
→ User completes payment
→ Backend verifies signature
→ Email sent to user ✅
```
