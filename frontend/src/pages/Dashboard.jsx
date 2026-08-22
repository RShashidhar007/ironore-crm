import { useState } from 'react'
import ChatWidget from '../components/ChatWidget.jsx'

export default function Dashboard({ user, onLogout }) {
  const [chatOpen, setChatOpen] = useState(true) // Open by default
  const [pendingAction, setPendingAction] = useState(null)

  // Get display name - prioritize customer name, then user name, then userId
  const displayName = user.customerName || user.customerCompany || user.name || user.userId
  const userRole = user.userRole ? `(${user.userRole})` : ''

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <span className="brand-mark small">Fe</span>
          <span className="brand-name">CRM Bot</span>
        </div>
        <div className="topbar-user">
          <span className="user-greeting">Hello, {displayName} {userRole}</span>
          <button className="btn-ghost" onClick={onLogout}>Log out</button>
        </div>
      </header>

      <main className="dashboard-main" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        minHeight: 'calc(100vh - 60px)',
        padding: '2rem'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '600px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#2c3e50' }}>
            Welcome, {user.customerName || user.name || displayName}
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#7f8c8d', marginBottom: '2rem' }}>
            Your AI-powered CRM assistant for iron ore and pellet products
          </p>
          <button 
            onClick={() => setChatOpen(true)}
            style={{
              padding: '1rem 2rem',
              fontSize: '1.1rem',
              backgroundColor: '#d35400',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.3s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#e67e22'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#d35400'}
          >
            Start Chat
          </button>
        </div>
      </main>

      <ChatWidget
        user={user}
        open={chatOpen}
        onToggle={() => setChatOpen((v) => !v)}
        pendingAction={pendingAction}
        onConsumePendingAction={() => setPendingAction(null)}
      />
    </div>
  )
}
