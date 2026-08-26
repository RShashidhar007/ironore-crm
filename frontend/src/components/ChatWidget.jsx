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

  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event) => {
        try {
          console.log('[Speech Recognition] onresult fired, event:', event)
          console.log('[Speech Recognition] Results length:', event.results.length)
          console.log('[Speech Recognition] Results:', event.results)
          
          // Safety check: make sure we have results
          if (!event.results || event.results.length === 0) {
            console.error('[Speech Recognition] No results captured')
            setIsListening(false)
            return
          }
          
          // Get the last result (most recent speech)
          const lastResultIndex = event.results.length - 1
          const lastResult = event.results[lastResultIndex]
          
          if (!lastResult || lastResult.length === 0) {
            console.error('[Speech Recognition] Last result is empty')
            setIsListening(false)
            return
          }
          
          let transcript = lastResult[0].transcript.trim()
          const field = selectedFieldRef.current
          const isFinal = lastResult.isFinal
          
          console.log('[Speech Recognition] Transcript:', transcript, 'Is Final:', isFinal, 'Target field:', field)
          
          // Only process final results
          if (!isFinal) {
            console.log('[Speech Recognition] Interim result, waiting for final...')
            return
          }
          
          // Convert word numbers to digits for quantity fields
          if (field === 'quotationQuantity' || field === 'orderQuantity') {
            // Try to convert common spoken numbers to digits
            const wordToNum = {
              'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 
              'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
              'ten': '10', 'twenty': '20', 'thirty': '30', 'forty': '40', 'fifty': '50',
              'hundred': '00', 'thousand': '000'
            }
            
            const lowerTranscript = transcript.toLowerCase().trim()
            // If it's a word number, try to convert
            if (wordToNum[lowerTranscript]) {
              transcript = wordToNum[lowerTranscript]
              console.log('[Speech Recognition] Converted to number:', transcript)
            }
          }
          
          // Route to the specific field only, don't put in input
          if (field === 'quotationQuantity') {
            console.log('[Speech Recognition] Updating quotationDetails.quantity to:', transcript)
            setQuotationDetails(prev => ({ 
              ...prev, 
              quantity: transcript 
            }))
          } else if (field === 'orderQuantity') {
            console.log('[Speech Recognition] Updating orderDetails.quantity to:', transcript)
            setOrderDetails(prev => ({ 
              ...prev, 
              quantity: transcript 
            }))
          } else if (field === 'poNumber') {
            setComplaintDetails(prev => ({ ...prev, poNumber: transcript }))
          } else if (field === 'dispatchDate') {
            setComplaintDetails(prev => ({ ...prev, dispatchDate: transcript }))
          } else if (field === 'description') {
            setComplaintDetails(prev => ({ ...prev, description: transcript }))
          } else if (field === 'complaintIdInput') {
            setComplaintDetails(prev => ({ ...prev, complaintIdInput: transcript }))
          } else {
            // Only put in input field for chat messages
            console.log('[Speech Recognition] Updating input field (chat) to:', transcript)
            setInput(transcript)
          }
          
          setIsListening(false)
          setSelectedField(null)
          selectedFieldRef.current = null
        } catch (err) {
          console.error('[Speech Recognition] Error in onresult handler:', err)
          setIsListening(false)
        }
      }

      recognitionRef.current.onerror = (event) => {
        console.error('[Speech Recognition] Error event:', event)
        console.error('[Speech Recognition] Error:', event.error)
        setIsListening(false)
        
        let errorMessage = "Speech recognition error. Please try again."
        
        switch (event.error) {
          case 'no-speech':
            errorMessage = "I didn't hear anything. Please speak clearly and try again."
            break
          case 'audio-capture':
            errorMessage = "No microphone found. Please check your microphone settings."
            break
          case 'network':
            errorMessage = "Network error. Please check your internet connection."
            break
          case 'permission-denied':
            errorMessage = "Microphone permission denied. Please allow access to your microphone in browser settings."
            break
          case 'not-allowed':
            errorMessage = "Speech recognition not allowed. Please check your browser permissions."
            break
          default:
            errorMessage = `Speech recognition error: ${event.error}`
        }
        
        setMessages((prev) => [...prev, { role: 'bot', text: errorMessage, isError: true }])
      }

      recognitionRef.current.onstart = () => {
        console.log('[Speech Recognition] Started listening...')
      }
      
      recognitionRef.current.onend = () => {
        console.log('[Speech Recognition] Stopped listening')
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

  function handleSelectProduct(product) {
    setOrderDetails({ selectedProduct: product, quantity: '', availableQuantity: null })
    // Update the last bot message to show order form
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
    // Update the last bot message to show quotation form
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
      // Send order with product PID and quantity to backend for validation
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
      // Send quotation request with product PID and quantity
      const res = await api.chat(
        `Quotation: Product ${quotationDetails.selectedProduct.pid}, Quantity: ${quotationDetails.quantity} MT`,
        `submit_quantity_quotation:${quotationDetails.selectedProduct.pid}:${quotationDetails.quantity}`
      )
      
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        text: res.reply,
        showQuotationForm: false
      }])
      
      // Reset quotation details after submission
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
    setOrderDetails({ selectedProduct: null })
    setQuotationDetails({ selectedProduct: null, quantity: '', showForm: false })
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
    } else {
      // For quotation form - set field to capture quantity
      if (quotationDetails.showForm && quotationDetails.selectedProduct) {
        console.log('[toggleListening] Setting quotationQuantity field')
        setSelectedField('quotationQuantity')
        selectedFieldRef.current = 'quotationQuantity'
      } 
      // For order form - set field to capture quantity
      else if (orderDetails.selectedProduct) {
        console.log('[toggleListening] Setting orderQuantity field')
        setSelectedField('orderQuantity')
        selectedFieldRef.current = 'orderQuantity'
      } 
      // Default to chat input
      else {
        console.log('[toggleListening] No form active, defaulting to chat input')
        setSelectedField(null)
        selectedFieldRef.current = null
      }
      console.log('[toggleListening] selectedFieldRef.current =', selectedFieldRef.current)
      recognitionRef.current.start()
      setIsListening(true)
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
