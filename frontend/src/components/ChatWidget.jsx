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
  const [complaintOption, setComplaintOption] = useState(null)
  const [selectedField, setSelectedField] = useState(null)
  const [orderDetails, setOrderDetails] = useState({ selectedProduct: null, quantity: '', availableQuantity: null })
  const [quotationDetails, setQuotationDetails] = useState({ selectedProduct: null, quantity: '', showForm: false })
  const selectedFieldRef = useRef(null)
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

  // Initialize Speech Recognition on mount
  useEffect(() => {
    console.log('[Speech Init] Initializing speech recognition...')
    
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.error('[Speech Init] Speech Recognition not supported in this browser')
      return
    }
    
    try {
      const recognition = new SpeechRecognition()
      console.log('[Speech Init] Recognition object created')
      
      // Configuration
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'
      recognition.maxAlternatives = 1
      
      // Store in ref
      recognitionRef.current = recognition
      
      // ONSTART - fires when recognition starts
      recognition.onstart = function() {
        console.log('[Speech] onstart - Listening started')
        setIsListening(true)
      }
      
      // ONRESULT - fires when result is available
      recognition.onresult = function(event) {
        console.log('[Speech] onresult fired')
        console.log('[Speech] event:', event)
        console.log('[Speech] results:', event.results)
        console.log('[Speech] results.length:', event.results.length)
        
        if (!event.results || event.results.length === 0) {
          console.error('[Speech] No results')
          return
        }
        
        // Collect final transcript
        let finalTranscript = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          const isFinal = event.results[i].isFinal
          const confidence = event.results[i][0].confidence
          
          console.log(`[Speech] Result[${i}]: "${transcript}" | Final: ${isFinal} | Confidence: ${confidence}`)
          
          if (isFinal) {
            finalTranscript += transcript + ' '
          }
        }
        
        finalTranscript = finalTranscript.trim()
        console.log('[Speech] Final transcript:', finalTranscript)
        
        if (finalTranscript) {
          const field = selectedFieldRef.current
          console.log('[Speech] Target field:', field)
          
          // Convert word numbers if quantity field
          let text = finalTranscript
          if (field === 'quotationQuantity' || field === 'orderQuantity') {
            const wordToNum = {
              'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
              'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
              'ten': '10', 'twenty': '20', 'thirty': '30', 'forty': '40', 'fifty': '50',
              'hundred': '00', 'thousand': '000'
            }
            const lower = finalTranscript.toLowerCase().trim()
            if (wordToNum[lower]) {
              text = wordToNum[lower]
              console.log('[Speech] Converted to number:', text)
            }
          }
          
          // Update appropriate state
          if (field === 'quotationQuantity') {
            console.log('[Speech] Updating quotation quantity:', text)
            setQuotationDetails(prev => ({ ...prev, quantity: text }))
          } else if (field === 'orderQuantity') {
            console.log('[Speech] Updating order quantity:', text)
            setOrderDetails(prev => ({ ...prev, quantity: text }))
          } else if (field === 'poNumber') {
            setComplaintDetails(prev => ({ ...prev, poNumber: text }))
          } else if (field === 'dispatchDate') {
            setComplaintDetails(prev => ({ ...prev, dispatchDate: text }))
          } else if (field === 'description') {
            setComplaintDetails(prev => ({ ...prev, description: text }))
          } else if (field === 'complaintIdInput') {
            setComplaintDetails(prev => ({ ...prev, complaintIdInput: text }))
          } else {
            console.log('[Speech] Updating chat input:', text)
            setInput(text)
          }
        }
      }
      
      // ONERROR - fires on error
      recognition.onerror = function(event) {
        console.error('[Speech] onerror fired')
        console.error('[Speech] error:', event.error)
        
        const errors = {
          'no-speech': "I didn't hear you. Please speak clearly and try again.",
          'audio-capture': 'No microphone detected. Please check your microphone.',
          'network': 'Network error. Please check your internet connection.',
          'permission-denied': 'Microphone access denied. Please allow microphone in browser settings.',
          'not-allowed': 'Microphone not allowed. Please check browser permissions.'
        }
        
        const message = errors[event.error] || `Speech recognition error: ${event.error}`
        setMessages(prev => [...prev, { role: 'bot', text: message, isError: true }])
      }
      
      // ONEND - fires when recognition ends
      recognition.onend = function() {
        console.log('[Speech] onend - Listening stopped')
        setIsListening(false)
      }
      
      // ONABORT - fires when recognition is aborted
      recognition.onabort = function() {
        console.log('[Speech] onabort - Recognition aborted')
        setIsListening(false)
      }
      
      console.log('[Speech Init] All handlers registered')
      
    } catch (error) {
      console.error('[Speech Init] Error creating recognition:', error)
    }
    
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch (e) {
          console.error('[Speech] Error aborting:', e)
        }
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
      
      // Check if response is for order placement
      const isOrderResponse = text === 'Place an Order' || action === 'Place an Order'
      
      // Check if response is for quotation request
      const isQuotationResponse = text === 'Ask for a Quotation' || action === 'Ask for a Quotation'
      
      // Check if response is for connect to company
      const isConnectResponse = text === 'Connect to Company' || action === 'Connect to Company' || text === 'Contact Company via Email' || action === 'Contact Company via Email'
      
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: res.reply,
        showComplaintCategories: res.reply.includes('Please select one of the following complaint categories'),
        showComplaintForm: false,
        showPreviousComplaintsOptions: hasPreviousComplaints,
        showOrderProducts: isOrderResponse,
        orderProducts: isOrderResponse && res.data ? res.data : [],
        showQuotationProducts: isQuotationResponse && res.data && res.data.products ? true : false,
        quotationProducts: isQuotationResponse && res.data && res.data.products ? res.data.products : [],
        companyEmail: isConnectResponse && res.data ? res.data.email : null,
        customerName: isConnectResponse && res.data ? res.data.customerName : null
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

  function handleSelectProduct(product) {
    setOrderDetails({ selectedProduct: product, quantity: '', availableQuantity: null })
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastBotMsgIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotMsgIndex !== undefined) {
        newMessages[lastBotMsgIndex] = {
          ...newMessages[lastBotMsgIndex],
          showOrderProducts: false,
          showOrderForm: true,
          selectedProduct: product
        }
      }
      return newMessages
    })
  }

  function handleSelectQuotationProduct(product) {
    setQuotationDetails({ selectedProduct: product, quantity: '', showForm: true })
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastBotMsgIndex = newMessages.map((m, i) => m.role === 'bot' ? i : -1).filter(i => i !== -1).pop()
      if (lastBotMsgIndex !== undefined) {
        newMessages[lastBotMsgIndex] = {
          ...newMessages[lastBotMsgIndex],
          showQuotationProducts: false,
          showQuotationForm: true,
          selectedQuotationProduct: product
        }
      }
      return newMessages
    })
  }

  async function submitOrder() {
    if (!orderDetails.selectedProduct || !orderDetails.quantity) return
    
    setLoading(true)
    try {
      const res = await api.chat(
        `Order: Product ${orderDetails.selectedProduct.PID}, Quantity: ${orderDetails.quantity} MT`,
        `order_quantity:${orderDetails.selectedProduct.PID}:${orderDetails.quantity}`
      )
      
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: res.reply,
        showOrderForm: false
      }])
    } catch (err) {
      const msg = err instanceof ApiError
        ? err.message
        : "I'm unable to process your order right now. Please try again."
      setMessages((prev) => [...prev, { role: 'bot', text: msg, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  async function submitQuotation() {
    if (!quotationDetails.selectedProduct || !quotationDetails.quantity) return
    
    setLoading(true)
    try {
      const res = await api.chat(
        `Quotation: Product ${quotationDetails.selectedProduct.pid}, Quantity: ${quotationDetails.quantity} MT`,
        `submit_quantity_quotation:${quotationDetails.selectedProduct.pid}:${quotationDetails.quantity}`
      )
      
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: res.reply,
        showQuotationForm: false
      }])
      
      setQuotationDetails({ selectedProduct: null, quantity: '', showForm: false })
    } catch (err) {
      const msg = err instanceof ApiError
        ? err.message
        : "I'm unable to generate your quotation right now. Please try again."
      setMessages((prev) => [...prev, { role: 'bot', text: msg, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  function runAction(actionLabel) {
    sendMessage(actionLabel, actionLabel)
  }

  function handleSend() {
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
    setOrderDetails({ selectedProduct: null })
    setQuotationDetails({ selectedProduct: null, quantity: '', showForm: false })
  }

  function toggleListening() {
    console.log('[toggleListening] Called')
    console.log('[toggleListening] recognitionRef.current:', recognitionRef.current)
    console.log('[toggleListening] isListening:', isListening)
    
    if (!recognitionRef.current) {
      console.error('[toggleListening] No recognition object')
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: "Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.", 
        isError: true 
      }])
      return
    }

    if (isListening) {
      console.log('[toggleListening] Stopping recognition')
      recognitionRef.current.stop()
    } else {
      // Determine which field
      if (quotationDetails.showForm && quotationDetails.selectedProduct) {
        console.log('[toggleListening] Set field: quotationQuantity')
        selectedFieldRef.current = 'quotationQuantity'
        setSelectedField('quotationQuantity')
      } else if (orderDetails.selectedProduct) {
        console.log('[toggleListening] Set field: orderQuantity')
        selectedFieldRef.current = 'orderQuantity'
        setSelectedField('orderQuantity')
      } else {
        console.log('[toggleListening] Set field: null (chat input)')
        selectedFieldRef.current = null
        setSelectedField(null)
      }
      
      console.log('[toggleListening] Starting recognition, field:', selectedFieldRef.current)
      try {
        recognitionRef.current.start()
        console.log('[toggleListening] Recognition started successfully')
      } catch (err) {
        console.error('[toggleListening] Error starting recognition:', err)
      }
    }
  }

  async function submitComplaint(category, description, poNumber, dispatchDate) {
    try {
      const data = await api.createComplaint(category, description, poNumber, dispatchDate)
      console.log('Response data:', data)

      setMessages((prev) => [...prev, {
        role: 'bot',
        text: `Thank you for reporting this issue, ${user?.name || 'Customer'}. Your complaint has been registered with tracking number **${data.ComplaintID}**.\n\nWe will investigate the issue and keep you updated on the resolution.\n\nIf you need to reference this complaint, please use the ID: ${data.ComplaintID}`
      }])
      return true
    } catch (err) {
      console.error('Complaint submission error:', err)
      const isNetworkError = err instanceof ApiError && err.status === 0
      const text = isNetworkError
        ? `I'm unable to connect to the CRM service right now. Please try again. Error: ${err.message}`
        : `Sorry, there was an error registering your complaint: ${err.message}`
      setMessages((prev) => [...prev, { role: 'bot', text, isError: true }])
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
                  sendMessage(text, action)
                }}
                onFieldSelect={(field) => {
                  setSelectedField(field)
                  selectedFieldRef.current = field
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
                    submitComplaintId()
                  }
                }}
                showOrderProducts={m.showOrderProducts || false}
                orderProducts={m.orderProducts || []}
                onSelectProduct={handleSelectProduct}
                showOrderForm={m.showOrderForm || false}
                selectedProduct={m.selectedProduct}
                orderQuantity={orderDetails.quantity}
                onOrderQuantityChange={(value) => setOrderDetails({ ...orderDetails, quantity: value })}
                onSubmitOrder={submitOrder}
                availableQuantity={m.availableQuantity}
                showQuotationProducts={m.showQuotationProducts || false}
                quotationProducts={m.quotationProducts || []}
                onSelectQuotationProduct={handleSelectQuotationProduct}
                showQuotationForm={m.showQuotationForm || false}
                selectedQuotationProduct={m.selectedQuotationProduct}
                quotationQuantity={quotationDetails.quantity}
                onQuotationQuantityChange={(value) => setQuotationDetails({ ...quotationDetails, quantity: value })}
                onSubmitQuotation={submitQuotation}
                companyEmail={m.companyEmail || null}
                customerName={m.customerName || null}
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
                placeholder={
                  selectedField === 'quotationQuantity' 
                    ? "Listening for quotation quantity..." 
                    : selectedField === 'orderQuantity'
                    ? "Listening for order quantity..."
                    : "Type your message…"
                }
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setSelectedField(null)}
                rows={1}
                style={{
                  flex: 1,
                  outline: input ? '2px solid var(--accent-ore)' : 'none',
                  boxShadow: input ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
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
