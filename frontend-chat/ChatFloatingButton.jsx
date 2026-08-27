import React, { useEffect, useRef, useState } from 'react'
import ChatMessage from './ChatMessage.jsx'
import './chat-button.css'

const QUICK_ACTIONS = [
  'Ask for a Quotation',
  'Place an Order',
  'Product Information',
  'Raise a Complaint',
  'Connect to Company',
]

const WELCOME = "Hello! I'm your CRM assistant. How can I help you today?"

/**
 * ChatFloatingButton Component
 * 
 * A standalone, self-contained chat interface component that can be embedded
 * in any React application. Includes speech recognition, complaint tracking,
 * order placement, quotation requests, and more.
 * 
 * Props:
 * - user: { customerName?, customerCompany?, name?, email? }
 * - apiBaseUrl: (required) Base URL for API calls (e.g., 'http://localhost:8000')
 * - open?: boolean - Controlled open state (optional)
 * - onToggle?: (open: boolean) => void - Callback when chat is toggled
 * 
 * Usage:
 * <ChatFloatingButton 
 *   user={{ name: 'John Doe', customerCompany: 'ABC Corp' }}
 *   apiBaseUrl="http://localhost:8000"
 * />
 */
export default function ChatFloatingButton({ user = {}, apiBaseUrl = '', open: controlledOpen, onToggle }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([{ role: 'bot', text: WELCOME }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [complaintDetails, setComplaintDetails] = useState({ category: '', description: '', poNumber: '', dispatchDate: '', complaintIdInput: '' })
  const [selectedComplaintCategory, setSelectedComplaintCategory] = useState(null)
  const [selectedField, setSelectedField] = useState(null)
  const [orderDetails, setOrderDetails] = useState({ selectedProduct: null, quantity: '', availableQuantity: null })
  const [quotationDetails, setQuotationDetails] = useState({ selectedProduct: null, quantity: '', showForm: false })
  
  const selectedFieldRef = useRef(null)
  const scrollRef = useRef(null)
  const recognitionRef = useRef(null)

  // Use controlled or uncontrolled open state
  const open = controlledOpen !== undefined ? controlledOpen : isOpen
  
  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading, open])

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.warn('[ChatWidget] Speech Recognition not supported')
      return
    }
    
    try {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        console.log('[Speech] Listening started')
        setIsListening(true)
      }

      recognition.onresult = (event) => {
        try {
          if (!event.results || event.results.length === 0) return
          
          let finalTranscript = ''
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' '
            }
          }
          
          finalTranscript = finalTranscript.trim()
          if (finalTranscript) {
            const field = selectedFieldRef.current
            
            // Convert words to numbers for quantity fields
            let text = finalTranscript
            if (field === 'quotationQuantity' || field === 'orderQuantity') {
              const wordToNum = {
                'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
                'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
                'ten': '10', 'twenty': '20', 'thirty': '30', 'forty': '40', 'fifty': '50',
                'hundred': '00', 'thousand': '000'
              }
              const lower = finalTranscript.toLowerCase().trim()
              if (wordToNum[lower]) text = wordToNum[lower]
            }
            
            // Route to appropriate field
            if (field === 'quotationQuantity') {
              setQuotationDetails(prev => ({ ...prev, quantity: text }))
            } else if (field === 'orderQuantity') {
              setOrderDetails(prev => ({ ...prev, quantity: text }))
            } else if (field === 'poNumber') {
              setComplaintDetails(prev => ({ ...prev, poNumber: text }))
            } else if (field === 'description') {
              setComplaintDetails(prev => ({ ...prev, description: text }))
            } else {
              setInput(text)
            }
          }
        } catch (err) {
          console.error('[Speech] onresult error:', err)
        }
      }

      recognition.onerror = (event) => {
        console.error('[Speech] Error:', event.error)
        const errors = {
          'no-speech': "I didn't hear you. Please speak again.",
          'audio-capture': 'No microphone detected.',
          'permission-denied': 'Microphone permission denied.',
          'network': 'Network error. Check internet connection.',
          'not-allowed': 'Browser microphone access not allowed.'
        }
        const msg = errors[event.error] || `Speech error: ${event.error}`
        setMessages(prev => [...prev, { role: 'bot', text: msg, isError: true }])
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognitionRef.current = recognition
    } catch (err) {
      console.error('[Speech Init] Error:', err)
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch (e) {
          console.error('[Speech] Abort error:', e)
        }
      }
    }
  }, [])

  // API helper function
  const makeRequest = async (endpoint, options = {}) => {
    if (!apiBaseUrl) {
      throw new Error('apiBaseUrl not configured')
    }
    
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    return response.json()
  }

  // Send message to backend
  const sendMessage = async (text, action = null) => {
    if (!text.trim() && !action) return
    
    setMessages(prev => [...prev, { role: 'user', text: action || text }])
    setInput('')
    setLoading(true)
    
    try {
      const res = await makeRequest('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text, action: action })
      })
      
      const hasPreviousComplaints = res.reply?.includes('You have') && res.reply?.includes('previous complaint(s)')
      const isOrderResponse = text === 'Place an Order' || action === 'Place an Order'
      const isQuotationResponse = text === 'Ask for a Quotation' || action === 'Ask for a Quotation'
      const isConnectResponse = text === 'Connect to Company' || action === 'Connect to Company'
      
      setMessages(prev => [...prev, {
        role: 'bot',
        text: res.reply || 'No response',
        showComplaintCategories: res.reply?.includes('Please select one of the following complaint categories'),
        showOrderProducts: isOrderResponse,
        orderProducts: isOrderResponse && res.data ? res.data : [],
        showQuotationProducts: isQuotationResponse && res.data?.products ? true : false,
        quotationProducts: isQuotationResponse && res.data?.products ? res.data.products : [],
        companyEmail: isConnectResponse && res.data?.email ? res.data.email : null,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: `Error: ${err.message}. Is the backend running at ${apiBaseUrl}?`,
        isError: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleCategorySelect = (category) => {
    setSelectedComplaintCategory(category)
    setMessages(prev => {
      const newMessages = [...prev]
      const lastBotIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotIndex !== undefined) {
        newMessages[lastBotIndex] = {
          ...newMessages[lastBotIndex],
          showComplaintCategories: false,
          showComplaintForm: true,
          selectedCategory: category
        }
      }
      return newMessages
    })
  }

  const handleSelectProduct = (product) => {
    setOrderDetails({ selectedProduct: product, quantity: '' })
    setMessages(prev => {
      const newMessages = [...prev]
      const lastBotIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotIndex !== undefined) {
        newMessages[lastBotIndex] = {
          ...newMessages[lastBotIndex],
          showOrderProducts: false,
          showOrderForm: true,
          selectedProduct: product
        }
      }
      return newMessages
    })
  }

  const handleSelectQuotationProduct = (product) => {
    setQuotationDetails({ selectedProduct: product, quantity: '', showForm: true })
    setMessages(prev => {
      const newMessages = [...prev]
      const lastBotIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotIndex !== undefined) {
        newMessages[lastBotIndex] = {
          ...newMessages[lastBotIndex],
          showQuotationProducts: false,
          showQuotationForm: true,
          selectedQuotationProduct: product
        }
      }
      return newMessages
    })
  }

  const submitOrder = async () => {
    if (!orderDetails.selectedProduct || !orderDetails.quantity) return
    
    setLoading(true)
    try {
      const res = await makeRequest('/api/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: `Order: Product ${orderDetails.selectedProduct.PID}, Quantity: ${orderDetails.quantity} MT`,
          action: `order_quantity:${orderDetails.selectedProduct.PID}:${orderDetails.quantity}`
        })
      })
      
      setMessages(prev => [...prev, { role: 'bot', text: res.reply, showOrderForm: false }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: `Error: ${err.message}`, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  const submitQuotation = async () => {
    if (!quotationDetails.selectedProduct || !quotationDetails.quantity) return
    
    setLoading(true)
    try {
      const res = await makeRequest('/api/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: `Quotation: Product ${quotationDetails.selectedProduct.pid}, Quantity: ${quotationDetails.quantity} MT`,
          action: `submit_quantity_quotation:${quotationDetails.selectedProduct.pid}:${quotationDetails.quantity}`
        })
      })
      
      setMessages(prev => [...prev, { role: 'bot', text: res.reply, showQuotationForm: false }])
      setQuotationDetails({ selectedProduct: null, quantity: '', showForm: false })
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: `Error: ${err.message}`, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setMessages(prev => [...prev, { 
        role: 'bot',
        text: 'Speech recognition not supported. Use Chrome, Edge, or Safari.',
        isError: true
      }])
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
    } else {
      if (quotationDetails.showForm && quotationDetails.selectedProduct) {
        selectedFieldRef.current = 'quotationQuantity'
      } else if (orderDetails.selectedProduct) {
        selectedFieldRef.current = 'orderQuantity'
      } else {
        selectedFieldRef.current = null
      }
      
      try {
        recognitionRef.current.start()
      } catch (err) {
        console.error('[Speech] Start error:', err)
      }
    }
  }

  const handleSend = () => {
    sendMessage(input)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleToggle = () => {
    if (onToggle) {
      onToggle(!open)
    } else {
      setIsOpen(!isOpen)
    }
  }

  const handleClear = () => {
    setMessages([{ role: 'bot', text: WELCOME }])
    setInput('')
  }

  return (
    <>
      <button
        className="chat-fab"
        onClick={handleToggle}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '✕' : 'Fe'}
      </button>

      {open && (
        <div className="chat-window" role="dialog" aria-label="Chat Assistant">
          <div className="chat-header">
            <div>
              <div className="chat-header-title">CRM Assistant</div>
              <div className="chat-header-sub">Support Bot</div>
            </div>
            <button className="btn-ghost small" onClick={handleClear}>Clear</button>
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
                showOrderProducts={m.showOrderProducts}
                orderProducts={m.orderProducts}
                onSelectProduct={handleSelectProduct}
                showOrderForm={m.showOrderForm}
                selectedProduct={m.selectedProduct}
                orderQuantity={orderDetails.quantity}
                onOrderQuantityChange={(value) => setOrderDetails({ ...orderDetails, quantity: value })}
                onSubmitOrder={submitOrder}
                showQuotationProducts={m.showQuotationProducts}
                quotationProducts={m.quotationProducts}
                onSelectQuotationProduct={handleSelectQuotationProduct}
                showQuotationForm={m.showQuotationForm}
                selectedQuotationProduct={m.selectedQuotationProduct}
                quotationQuantity={quotationDetails.quantity}
                onQuotationQuantityChange={(value) => setQuotationDetails({ ...quotationDetails, quantity: value })}
                onSubmitQuotation={submitQuotation}
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
              <button 
                key={a} 
                className="chip" 
                onClick={() => sendMessage(a, a)} 
                disabled={loading}
              >
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
              >
                {isListening ? '🎤' : '🎙️'}
              </button>
              <textarea
                placeholder="Type your message…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                style={{ flex: 1 }}
              />
            </div>
            <button 
              className="btn-primary small" 
              onClick={handleSend} 
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  )
}
