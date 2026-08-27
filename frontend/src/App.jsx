import { useState, useEffect } from 'react'
import ChatWidget from './components/ChatWidget.jsx'
import { getToken, getUser } from './api.js'

export default function App() {
  const [session, setSession] = useState(null)
  const [checked, setChecked] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

  useEffect(() => {
    const token = getToken()
    const user = getUser()
    if (token && user) setSession({ token, user })
    setChecked(true)
  }, [])

  if (!checked) return null

  return (
    <div style={{ minHeight: '100vh', background: '#14181c' }}>
      {session && (
        <ChatWidget
          user={session.user}
          open={chatOpen}
          onToggle={() => setChatOpen((v) => !v)}
        />
      )}
    </div>
  )
}
