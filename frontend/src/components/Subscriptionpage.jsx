import { useState } from 'react'
import axios from 'axios'
import './SubscriptionPage.css'

const PLANS = [
  {
    id: 'basic',
    name: 'Basic',
    price: '₹99',
    amount: 9900,
    features: ['1 User', '5GB Storage', 'Email Support'],
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '₹499',
    amount: 49900,
    features: ['5 Users', '50GB Storage', 'Priority Support', 'Analytics'],
  },
  {
    id: 'custom',
    name: 'Custom',
    price: '₹999',
    amount: 99900,
    features: ['Unlimited Users', '500GB Storage', '24/7 Support', 'Custom Features'],
  },
]

function SubscriptionPage() {
  const [form, setForm]         = useState({ name: '', email: '' })
  const [selectedPlan, setPlan] = useState('basic')
  const [loading, setLoading]   = useState(false)
  const [success, setSuccess]   = useState(false)
  const [error, setError]       = useState('')

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
  const razorpayKey = import.meta.env.VITE_RAZORPAY_KEY_ID

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handlePayment = async () => {
    // Validation
    if (!form.name.trim() || !form.email.trim()) {
      setError('Please fill in all fields!')
      return
    }
    if (!/\S+@\S+\.\S+/.test(form.email)) {
      setError('Please enter a valid email!')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Step 1 - Create order from backend
      const { data } = await axios.post(`${backendUrl}/api/create-order`, {
        plan: selectedPlan,
      })

      // Step 2 - Open Razorpay popup
      const options = {
        key:         razorpayKey,
        amount:      data.amount,
        currency:    data.currency,
        name:        'Subscription App',
        description: `${data.plan_name} Plan`,
        order_id:    data.order_id,

        handler: async (response) => {
          // Step 3 - Verify payment on backend
          try {
            const verify = await axios.post(`${backendUrl}/api/verify-payment`, {
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id:   response.razorpay_order_id,
              razorpay_signature:  response.razorpay_signature,
              name:                form.name,
              email:               form.email,
              amount:              data.amount,
            })

            if (verify.data.success) {
              setSuccess(true)
            }
          } catch {
            setError('Payment verification failed. Please contact support.')
          }
        },

        prefill: {
          name:  form.name,
          email: form.email,
        },

        theme: { color: '#6366f1' },

        modal: {
          ondismiss: () => setLoading(false),
        },
      }

      const rzp = new window.Razorpay(options)
      rzp.open()

    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong!')
    } finally {
      setLoading(false)
    }
  }

  // ── Success Screen ──────────────────────────────────────────────────────────
  if (success) {
    return (
      <div className="page">
        <div className="success-card">
          <div className="success-icon">✅</div>
          <h2>Payment Successful!</h2>
          <p>Thank you <strong>{form.name}</strong>!</p>
          <p>A confirmation email has been sent to <strong>{form.email}</strong></p>
          <button className="btn" onClick={() => { setSuccess(false); setForm({ name: '', email: '' }) }}>
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // ── Main Page ───────────────────────────────────────────────────────────────
  return (
    <div className="page">
      <div className="container">

        {/* Header */}
        <div className="header">
          <h1>Choose Your Plan</h1>
          <p>Select a plan and get started today</p>
        </div>

        {/* Plans */}
        <div className="plans">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`plan-card ${selectedPlan === plan.id ? 'active' : ''}`}
              onClick={() => setPlan(plan.id)}
            >
              {plan.id === 'premium' && <div className="badge">Popular</div>}
              <h3>{plan.name}</h3>
              <div className="price">{plan.price}<span>/mo</span></div>
              <ul>
                {plan.features.map((f) => (
                  <li key={f}>✓ {f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Form */}
        <div className="form-card">
          <h3>Your Details</h3>

          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              placeholder="Enter your name"
              value={form.name}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button
            className="btn pay-btn"
            onClick={handlePayment}
            disabled={loading}
          >
            {loading ? 'Processing...' : `Pay Now →`}
          </button>

          <p className="secure-note">🔒 Secured by Razorpay</p>
        </div>

      </div>
    </div>
  )
}

export default SubscriptionPage