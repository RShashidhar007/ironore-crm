import { useState, useEffect } from 'react'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import { getToken, getUser, clearSession } from './api.js'

export default function App() {
  const [session, setSession] = useState(null)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    const token = getToken()
    const user = getUser()
    if (token && user) setSession({ token, user })
    setChecked(true)
  }, [])

  function handleLogin(user) {
    setSession({ token: getToken(), user })
  }

  function handleLogout() {
    clearSession()
    setSession(null)
  }

  if (!checked) return null

  return session
    ? <Dashboard user={session.user} onLogout={handleLogout} />
    : <Login onLogin={handleLogin} />
}
