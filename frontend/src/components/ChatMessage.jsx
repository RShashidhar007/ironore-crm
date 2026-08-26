import ReactMarkdown from 'react-markdown'
import { useState } from 'react'

export default function ChatMessage({ 
  role, 
  text, 
  isError, 
  showComplaintCategories, 
  showComplaintForm, 
  selectedCategory, 
  onCategorySelect, 
  complaintDetails, 
  onComplaintDetailsChange, 
  onSubmitComplaint, 
  showPreviousComplaintsOptions,
  complaintIdInput,
  onComplaintIdChange,
  onSubmitComplaintId,
  onFieldSelect,
  selectedField,
  isListening,
  loading,
  onSendMessage,
  showOrderProducts,
  orderProducts,
  onSelectProduct,
  showOrderForm,
  selectedProduct,
  orderQuantity,
  onOrderQuantityChange,
  onSubmitOrder,
  availableQuantity,
  showQuotationProducts,
  quotationProducts,
  onSelectQuotationProduct,
  showQuotationForm,
  selectedQuotationProduct,
  quotationQuantity,
  onQuotationQuantityChange,
  onSubmitQuotation,
  companyEmail,
  customerName,
}) {
  const isUser = role === 'user'
  
  // Function to handle clicking on a complaint ID
  const handleComplaintIdClick = (complaintId) => {
    if (onSendMessage) {
      onSendMessage(complaintId, `view_complaint:${complaintId}`)
    }
  }
  
  // Custom renderer to make complaint IDs clickable
  const renderText = (text) => {
    if (!text) return null
    
    // Split by markdown bold markers and complaint ID pattern
    const parts = []
    const regex = /(\*\*CMP-\d{8}-\d{4}\*\*)/g
    let lastIndex = 0
    let match
    
    while ((match = regex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.substring(lastIndex, match.index)
        })
      }
      
      // Extract complaint ID (remove the ** markers)
      const complaintId = match[1].replace(/\*\*/g, '')
      parts.push({
        type: 'complaint-id',
        content: complaintId
      })
      
      lastIndex = regex.lastIndex
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex)
      })
    }
    
    return parts.length > 0 ? parts : [{ type: 'text', content: text }]
  }
  
  const textParts = renderText(text)
  
  return (
    <div className={`msg-row ${isUser ? 'msg-row-user' : 'msg-row-bot'}`}>
      {!isUser && <div className="msg-avatar">Fe</div>}
      <div className={`msg-bubble ${isUser ? 'msg-user' : 'msg-bot'} ${isError ? 'msg-error' : ''}`}>
        {textParts.map((part, idx) => {
          if (part.type === 'complaint-id') {
            return (
              <button
                key={idx}
                onClick={() => handleComplaintIdClick(part.content)}
                disabled={loading}
                style={{
                  background: 'var(--accent-ore)',
                  color: 'white',
                  border: 'none',
                  padding: '4px 12px',
                  borderRadius: '6px',
                  fontWeight: 'bold',
                  fontSize: '13px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  margin: '0 4px',
                  display: 'inline-block',
                  opacity: loading ? 0.5 : 1,
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'scale(1.05)'
                    e.target.style.boxShadow = '0 2px 8px rgba(196, 98, 45, 0.4)'
                  }
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'scale(1)'
                  e.target.style.boxShadow = 'none'
                }}
              >
                🔍 {part.content}
              </button>
            )
          } else {
            return <ReactMarkdown key={idx}>{part.content}</ReactMarkdown>
          }
        })}
        
        {/* Order Form with Quantity Input */}
        {showOrderForm && selectedProduct && (
          <div style={{ marginTop: '15px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
            <p style={{ marginTop: 0, marginBottom: '12px', fontWeight: 'bold', color: '#c4622d' }}>
              {selectedProduct.name}
            </p>
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Quantity (MT)</label>
            <input 
              type="number" 
              placeholder="Speak or type quantity in MT"
              value={orderQuantity}
              onChange={(e) => onOrderQuantityChange(e.target.value)}
              disabled={loading}
              min="0"
              step="0.01"
              style={{ 
                width: '100%',
                background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box'
              }}
            />
            
            <button 
              onClick={() => onSubmitOrder()}
              disabled={loading || !orderQuantity || orderQuantity <= 0}
              style={{ 
                marginTop: '12px', 
                width: '100%',
                background: 'var(--accent-ore)', 
                color: 'white', 
                padding: '10px', 
                border: 'none', 
                borderRadius: '6px', 
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !orderQuantity || orderQuantity <= 0 ? 'not-allowed' : 'pointer',
                opacity: loading || !orderQuantity || orderQuantity <= 0 ? 0.5 : 1
              }}
            >
              {loading ? 'Checking...' : 'Check Availability'}
            </button>
          </div>
        )}
        
        {/* Quotation Form with Quantity Input */}
        {showQuotationForm && selectedQuotationProduct && (
          <div style={{ marginTop: '15px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
            <p style={{ marginTop: 0, marginBottom: '12px', fontWeight: 'bold', color: '#c4622d' }}>
              {selectedQuotationProduct.name}
            </p>
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Quantity (MT)</label>
            <input 
              type="number" 
              placeholder="Speak or type quantity in MT"
              value={quotationQuantity}
              onChange={(e) => onQuotationQuantityChange(e.target.value)}
              disabled={loading}
              min="0"
              step="0.01"
              style={{ 
                width: '100%',
                background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box'
              }}
            />
            
            <button 
              onClick={() => onSubmitQuotation()}
              disabled={loading || !quotationQuantity || quotationQuantity <= 0}
              style={{ 
                marginTop: '12px', 
                width: '100%',
                background: 'var(--accent-ore)', 
                color: 'white', 
                padding: '10px', 
                border: 'none', 
                borderRadius: '6px', 
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !quotationQuantity || quotationQuantity <= 0 ? 'not-allowed' : 'pointer',
                opacity: loading || !quotationQuantity || quotationQuantity <= 0 ? 0.5 : 1
              }}
            >
              {loading ? 'Generating...' : 'Generate Quotation'}
            </button>
          </div>
        )}
        
        {/* Product Selection for Orders */}
        {showOrderProducts && orderProducts && orderProducts.length > 0 && (
          <div style={{ marginTop: '15px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {orderProducts.map((product) => (
                <button 
                  key={product.PID} 
                  className="chip" 
                  onClick={() => onSelectProduct(product)}
                  disabled={loading}
                  style={{ margin: 0 }}
                >
                  {product.name}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Product Selection for Quotations */}
        {showQuotationProducts && quotationProducts && quotationProducts.length > 0 && (
          <div style={{ marginTop: '15px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {quotationProducts.map((product) => (
                <button 
                  key={product.pid} 
                  className="chip" 
                  onClick={() => onSelectQuotationProduct(product)}
                  disabled={loading}
                  style={{ margin: 0 }}
                >
                  {product.name}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Previous Complaints Options */}
        {showPreviousComplaintsOptions && (
          <div style={{ marginTop: '15px' }}>
            <p style={{ marginBottom: '10px', fontWeight: 'bold' }}>What would you like to do?</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              <button 
                className="chip" 
                onClick={() => onSubmitComplaintId('track')}
                disabled={loading}
                style={{ margin: 0 }}
              >
                Track Existing Complaint
              </button>
              <button 
                className="chip" 
                onClick={() => onSubmitComplaintId('new')}
                disabled={loading}
                style={{ margin: 0 }}
              >
                Raise New Complaint
              </button>
            </div>
          </div>
        )}
        
        {/* Complaint ID Input for tracking */}
        {showComplaintForm && complaintDetails.complaintIdInput && (
          <div style={{ marginTop: '15px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
            <p style={{ marginTop: 0, marginBottom: '12px', fontWeight: 'bold', color: '#c4622d' }}>
              Track Complaint
            </p>
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Complaint ID</label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input 
                type="text" 
                placeholder="e.g., CMP-20240820-0001"
                value={complaintDetails.complaintIdInput}
                onChange={(e) => onComplaintIdChange(e.target.value)}
                disabled={loading}
                style={{ 
                  flex: 1,
                  background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                  padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box'
                }}
              />
            </div>
            <button 
              onClick={() => onSubmitComplaintId('submit')}
              disabled={loading || !complaintDetails.complaintIdInput.trim()}
              style={{ 
                marginTop: '12px', 
                width: '100%',
                background: 'var(--accent-ore)', 
                color: 'white', 
                padding: '10px', 
                border: 'none', 
                borderRadius: '6px', 
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !complaintDetails.complaintIdInput.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !complaintDetails.complaintIdInput.trim() ? 0.5 : 1
              }}
            >
              {loading ? 'Checking...' : 'Check Status'}
            </button>
          </div>
        )}
        
        {/* Complaint Category Buttons inside bubble */}
        {showComplaintCategories && (
          <div style={{ marginTop: '15px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {['Fe T Deviation', 'CCS Deviation', 'Sponge Fines Generation', 'Yield Deviation', 'Moisture Deviation', 'Phosphorus Deviation'].map((category) => (
                <button 
                  key={category} 
                  className="chip" 
                  onClick={() => onCategorySelect(category)}
                  disabled={loading}
                  style={{ margin: 0 }}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Complaint Form inside bubble */}
        {showComplaintForm && !complaintDetails.complaintIdInput && (
          <div style={{ marginTop: '15px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
            <p style={{ marginTop: 0, marginBottom: '12px', fontWeight: 'bold', color: '#c4622d' }}>
              Selected: {selectedCategory}
            </p>
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>PO Number</label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input 
                type="text" 
                placeholder="Enter PO number"
                value={complaintDetails.poNumber}
                onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, poNumber: e.target.value })}
                disabled={loading}
                style={{ 
                  flex: 1,
                  background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                  padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box'
                }}
              />
            </div>
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Dispatch Date</label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input 
                type="date" 
                value={complaintDetails.dispatchDate}
                onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, dispatchDate: e.target.value })}
                disabled={loading}
                style={{ 
                  flex: 1,
                  background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                  padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box'
                }}
              />
            </div>
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Complaint Description</label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
              <textarea
                placeholder="Describe the issue in detail..."
                value={complaintDetails.description}
                onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, description: e.target.value })}
                rows={3}
                disabled={loading}
                style={{ 
                  flex: 1,
                  background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                  padding: '8px', borderRadius: '6px', fontSize: '13px', resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit'
                }}
              />
            </div>
            
            <button 
              onClick={() => onSubmitComplaint(selectedCategory, complaintDetails.description, complaintDetails.poNumber, complaintDetails.dispatchDate)}
              disabled={loading || !complaintDetails.description.trim() || !complaintDetails.poNumber.trim() || !complaintDetails.dispatchDate}
              style={{ 
                marginTop: '12px', 
                width: '100%',
                background: 'var(--accent-ore)', 
                color: 'white', 
                padding: '10px', 
                border: 'none', 
                borderRadius: '6px', 
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !complaintDetails.description.trim() || !complaintDetails.poNumber.trim() || !complaintDetails.dispatchDate ? 'not-allowed' : 'pointer',
                opacity: loading || !complaintDetails.description.trim() || !complaintDetails.poNumber.trim() || !complaintDetails.dispatchDate ? 0.5 : 1
              }}
            >
              {loading ? 'Submitting...' : 'Submit Complaint'}
            </button>
          </div>
        )}

        {/* Company Email Display */}
        {companyEmail && (
          <div style={{ marginTop: '15px', background: 'rgba(196, 98, 45, 0.1)', padding: '12px', borderRadius: '8px', border: '1px solid var(--accent-ore)' }}>
            <p style={{ marginTop: 0, marginBottom: '12px', fontWeight: 'bold', color: '#c4622d' }}>
              📧 Contact Us
            </p>
            {customerName && (
              <p style={{ marginTop: 0, marginBottom: '12px', fontSize: '14px', color: 'var(--text)' }}>
                Hello <strong>{customerName}</strong>! Reach out to us via email:
              </p>
            )}
            <a 
              href={`https://mail.google.com/mail/?view=cm&fs=1&to=${companyEmail}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-block',
                background: 'var(--accent-ore)',
                color: 'white',
                padding: '10px 16px',
                borderRadius: '6px',
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '14px',
                transition: 'all 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.05)'
                e.target.style.boxShadow = '0 4px 12px rgba(196, 98, 45, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)'
                e.target.style.boxShadow = 'none'
              }}
            >
              ✉️ Open Gmail to Send Email
            </a>
            <p style={{ marginTop: '10px', marginBottom: 0, fontSize: '12px', color: 'var(--text-dim)' }}>
              Click the button above to open Gmail and send us a message.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
