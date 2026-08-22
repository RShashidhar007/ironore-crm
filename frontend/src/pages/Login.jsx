import { useState } from 'react'
import { api, saveSession, ApiError } from '../api.js'

export default function Login({ onLogin }) {
  const [userId, setUserId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!userId.trim() || !password) {
      setError('Please enter both your user ID and password.')
      return
    }
    setLoading(true)
    try {
      const res = await api.login(userId.trim(), password)
      const user = { 
        name: res.user_name, 
        role: res.user_role, 
        customerId: res.customer_id,
        customerName: res.customer_name,
        customerCompany: res.customer_company,
        responsibleSeller: res.responsible_seller,
        userId: userId.trim() 
      }
      saveSession(res.access_token, user)
      onLogin(user)
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Invalid user ID or password. Please check your credentials and try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="login-brand">
        <div className="brand-mark">Fe</div>
        <h1>CRM bot</h1>
        <p className="brand-tag">Customer Portal — Iron Ore &amp; Iron Pellet Supply</p>

        <div className="assay-card" aria-hidden="true">
          <div className="assay-title">SAMPLE ASSAY CERTIFICATE</div>
          <div className="assay-row"><span>Fe</span><i /><span>63.5%</span></div>
          <div className="assay-row"><span>SiO₂</span><i /><span>4.0%</span></div>
          <div className="assay-row"><span>Al₂O₃</span><i /><span>1.8%</span></div>
          <div className="assay-row"><span>Size</span><i /><span>9–16mm</span></div>
        </div>
      </div>

      <div className="login-panel">
        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Sign in to your account</h2>
          <p className="form-sub">Access your orders, specifications, and support in one place.</p>

          <label htmlFor="userId">User ID</label>
          <input
            id="userId"
            type="text"
            autoComplete="username"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="e.g. shreeji.rakesh"
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />

          {error && <div className="form-error" role="alert">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
