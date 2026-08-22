import React, { useEffect, useRef, useState } from 'react'
import ChatMessage from './ChatMessage.jsx'
import { api, ApiError } from '../api.js'

const QUICK_ACTIONS = [
  'Ask for a Quotation',
  'Place an Order',
  'Product Information',
  'Raise a Complaint',
  'Connect to Company',
]

const WELCOME = "Hello! I'm your CRM assistant. How can I help you today?"

export default function ChatWidget({ user, open, onToggle, pendingAction, onConsumePendingAction }) {
  // Get customer name for personalized greeting
  const customerName = user?.customerName || user?.customerCompany || user?.name || ''
  const personalizedWelcome = customerName 
    ? `Hello ${customerName}! I'm your CRM assistant. How can I help you today?`
    : WELCOME
  
  const [messages, setMessages] = useState([{ role: 'bot', text: personalizedWelcome }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [complaintDetails, setComplaintDetails] = useState({ category: '', description: '', poNumber: '', dispatchDate: '', complaintIdInput: '' })
  const [selectedComplaintCategory, setSelectedComplaintCategory] = useState(null)
  const [complaintOption, setComplaintOption] = useState(null) // 'track' or 'new'
  const [selectedField, setSelectedField] = useState(null) // Track which field is selected ('poNumber', 'dispatchDate', 'description')
  const selectedFieldRef = useRef(null) // Ref to track selected field for speech input - initialize to null
  const scrollRef = useRef(null)
  const handledActionRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading, open])

  useEffect(() => {
    if (open && pendingAction && handledActionRef.current !== pendingAction) {
      handledActionRef.current = pendingAction
      runAction(pendingAction)
      onConsumePendingAction()
    }
  }, [open, pendingAction])

  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        const field = selectedFieldRef.current
        if (field === 'poNumber') {
          setComplaintDetails(prev => ({ ...prev, poNumber: transcript }))
          setSelectedField(null)
          selectedFieldRef.current = null
        } else if (field === 'dispatchDate') {
          setComplaintDetails(prev => ({ ...prev, dispatchDate: transcript }))
          setSelectedField(null)
          selectedFieldRef.current = null
        } else if (field === 'description') {
          setComplaintDetails(prev => ({ ...prev, description: transcript }))
          setSelectedField(null)
          selectedFieldRef.current = null
        } else if (field === 'complaintIdInput') {
          setComplaintDetails(prev => ({ ...prev, complaintIdInput: transcript }))
          setSelectedField(null)
          selectedFieldRef.current = null
        } else {
          setInput(transcript)
        }
        setIsListening(false)
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        if (event.error === 'no-speech') {
          setMessages((prev) => [...prev, { role: 'bot', text: "I didn't hear anything. Please try again.", isError: true }])
        }
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  async function sendMessage(text, action = null) {
    if (!text.trim() && !action) return
    setMessages((prev) => [...prev, { role: 'user', text: action || text }])
    setInput('')
    setLoading(true)
    try {
      const res = await api.chat(text, action)
      
      // Check if the response mentions previous complaints
      const hasPreviousComplaints = res.reply.includes('You have') && res.reply.includes('previous complaint(s)')
      
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: res.reply,
        showComplaintCategories: res.reply.includes('Please select one of the following complaint categories'),
        showComplaintForm: false,
        showPreviousComplaintsOptions: hasPreviousComplaints
      }])
    } catch (err) {
      const msg = err instanceof ApiError
        ? err.message
        : "I'm unable to connect to the CRM service right now. Please try again."
      setMessages((prev) => [...prev, { role: 'bot', text: msg, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  function handleCategorySelect(category) {
    setSelectedComplaintCategory(category)
    // Update the last bot message to show the form instead of categories
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastBotMsgIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotMsgIndex !== undefined) {
        newMessages[lastBotMsgIndex] = {
          ...newMessages[lastBotMsgIndex],
          showComplaintCategories: false,
          showComplaintForm: true,
          selectedCategory: category
        }
      }
      return newMessages
    })
  }

  // Function to handle previous complaints options (track or new)

  function runAction(actionLabel) {
    sendMessage(actionLabel, actionLabel)
  }

  function handleSend() {
    // If we're listening to a field, don't send to chat
    if (selectedField) {
      return
    }
    sendMessage(input)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleClear() {
    setMessages([{ role: 'bot', text: personalizedWelcome }])
    handledActionRef.current = null
    setSelectedComplaintCategory(null)
    setComplaintDetails({ category: '', description: '', poNumber: '', dispatchDate: '', complaintIdInput: '' })
    setComplaintOption(null)
  }

  function toggleListening() {
    if (!recognitionRef.current) {
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: "Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.", 
        isError: true 
      }])
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
      setSelectedField(null)
      selectedFieldRef.current = null
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  async function submitComplaint(category, description, poNumber, dispatchDate) {
    try {
      const token = sessionStorage.getItem('ferrum_crm_token') || sessionStorage.getItem('crm_token')
      
      const res = await fetch('http://localhost:8000/api/complaints', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          category_type: category, 
          description: description,
          po_number: poNumber || null,
          dispatch_date: dispatchDate || null
        }),
      })
      console.log('Response status:', res.status);
      const data = await res.json()
      console.log('Response data:', data);
      
      if (res.ok) {
        setMessages((prev) => [...prev, { 
          role: 'bot', 
          text: `Thank you for reporting this issue, ${user?.name || 'Customer'}. Your complaint has been registered with tracking number **${data.ComplaintID}**.\n\nWe will investigate the issue and keep you updated on the resolution.\n\nIf you need to reference this complaint, please use the ID: ${data.ComplaintID}` 
        }])
        return true
      } else {
        // Handle error response - try to extract the error message
        console.error('Complaint submission error - Status:', res.status, 'Response:', data);
        
        // Try multiple ways to extract error message
        let errorDetail = 'Unknown error';
        if (data && typeof data === 'object') {
          // Check each possible error field
          if (data.detail) errorDetail = String(data.detail);
          else if (data.message) errorDetail = String(data.message);
          else if (data.error) errorDetail = String(data.error);
          else {
            // If no specific error field, use JSON.stringify
            errorDetail = JSON.stringify(data);
          }
        }
        
        // Ensure it's a string (double-check)
        if (typeof errorDetail !== 'string') {
          errorDetail = String(errorDetail);
        }
        
        // Truncate for display
        errorDetail = errorDetail.substring(0, 200);
        
        setMessages((prev) => [...prev, { 
          role: 'bot', 
          text: `Sorry, there was an error registering your complaint: ${errorDetail} (HTTP ${res.status})`, 
          isError: true 
        }])
        return false
      }
    } catch (err) {
      console.error('Complaint submission exception:', err);
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: `I'm unable to connect to the CRM service right now. Please try again. Error: ${err.message}`, 
        isError: true 
      }])
      return false
    }
  }

  async function submitComplaintPrompt(category, description, poNumber, dispatchDate) {
    setLoading(true)
    const success = await submitComplaint(category, description, poNumber, dispatchDate)
    setLoading(false)
    
    if (success) {
      setComplaintDetails({ category: '', description: '', poNumber: '', dispatchDate: '' })
      setSelectedComplaintCategory(null)
    }
  }

  async function submitComplaintId() {
    const complaintId = complaintDetails.complaintIdInput?.trim()
    if (complaintId) {
      setLoading(true)
      // Send the complaint ID for tracking
      setMessages((prev) => [...prev, { role: 'user', text: `Check complaint ${complaintId}` }])
      setInput('')
      try {
        const res = await api.chat(`Check complaint ${complaintId}`)
        setMessages((prev) => [...prev, { role: 'bot', text: res.reply }])
      } catch (err) {
        const msg = err instanceof ApiError
          ? err.message
          : "I'm unable to connect to the CRM service right now. Please try again."
        setMessages((prev) => [...prev, { role: 'bot', text: msg, isError: true }])
      } finally {
        setLoading(false)
        setComplaintDetails({ category: '', description: '', poNumber: '', dispatchDate: '', complaintIdInput: '' })
      }
    }
  }

  return (
    <>
      <button
        className="chat-fab"
        onClick={onToggle}
        aria-label={open ? 'Close chat' : 'Open CRM assistant chat'}
      >
        {open ? '✕' : 'Fe'}
      </button>

      {open && (
        <div className="chat-window" role="dialog" aria-label="CRM Assistant Chat">
          <div className="chat-header">
            <div>
              <div className="chat-header-title">CRM Assistant</div>
              <div className="chat-header-sub">CRM Support Bot</div>
            </div>
            <button className="btn-ghost small" onClick={handleClear}>Clear chat</button>
          </div>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <ChatMessage 
                key={i} 
                role={m.role} 
                text={m.text} 
                isError={m.isError}
                showComplaintCategories={m.showComplaintCategories}
                showComplaintForm={m.showComplaintForm}
                selectedCategory={m.selectedCategory}
                onCategorySelect={handleCategorySelect}
                complaintDetails={complaintDetails}
                onComplaintDetailsChange={setComplaintDetails}
                onSubmitComplaint={submitComplaintPrompt}
                showPreviousComplaintsOptions={m.showPreviousComplaintsOptions || false}
                complaintIdInput={complaintDetails.complaintIdInput || ''}
                onComplaintIdChange={(value) => {
                  setComplaintDetails({ ...complaintDetails, complaintIdInput: value })
                }}
                onSendMessage={(text, action) => {
                  // Send message with optional action
                  sendMessage(text, action)
                }}
                onFieldSelect={(field) => {
                  setSelectedField(field)
                  selectedFieldRef.current = field
                  // If already listening, stop and restart
                  if (isListening) {
                    recognitionRef.current.stop()
                    setIsListening(false)
                    recognitionRef.current.start()
                  }
                }}
                selectedField={selectedField}
                isListening={isListening}
                loading={loading}
                onSubmitComplaintId={(action) => {
                  if (action === 'track') {
                    setComplaintOption('track')
                    runAction('Track my Complaint')
                  } else if (action === 'new') {
                    setComplaintOption('new')
                    setComplaintDetails({ category: '', description: '', poNumber: '', dispatchDate: '', complaintIdInput: '' })
                    setSelectedComplaintCategory(null)
                    setComplaintOption(null)
                    // Show complaint categories after selecting 'new'
                    setMessages((prev) => {
                      const newMessages = [...prev]
                      const lastBotMsgIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
                      if (lastBotMsgIndex !== undefined) {
                        newMessages[lastBotMsgIndex] = {
                          ...newMessages[lastBotMsgIndex],
                          showPreviousComplaintsOptions: false,
                          showComplaintCategories: true
                        }
                      }
                      return newMessages
                    })
                  } else if (action === 'submit') {
                    // Submit complaint ID for tracking
                    submitComplaintId()
                  }
                }}
                loading={loading}
              />
            ))}
            {loading && (
              <div className="msg-row msg-row-bot">
                <div className="msg-avatar">Fe</div>
                <div className="msg-bubble msg-bot typing-bubble">
                  <span className="dot" /><span className="dot" /><span className="dot" />
                </div>
              </div>
            )}
          </div>

          <div className="chat-actions">
            {QUICK_ACTIONS.map((a) => (
              <button key={a} className="chip" onClick={() => runAction(a)} disabled={loading}>
                {a}
              </button>
            ))}
          </div>

          <div className="chat-input-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1 }}>
              <button 
                className={`btn-mic ${isListening ? 'listening' : ''}`}
                onClick={toggleListening}
                disabled={loading}
                title={isListening ? 'Stop listening' : 'Click to speak'}
                aria-label={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? '🎤' : '🎙️'}
              </button>
              <textarea
                placeholder={selectedField === null ? "Type your message…" : "Listening to " + selectedField + "..."}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setSelectedField(null)}
                rows={1}
                style={{
                  flex: 1,
                  outline: selectedField === null && input ? '2px solid var(--accent-ore)' : 'none',
                  boxShadow: selectedField === null && input ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
                }}
              />
            </div>
            <button className="btn-primary small" onClick={handleSend} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  )
}
