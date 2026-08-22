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
  onSendMessage // Add this prop to send messages
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
            <input 
              type="text" 
              placeholder="e.g., CMP-20240820-0001"
              value={complaintDetails.complaintIdInput}
              onChange={(e) => onComplaintIdChange(e.target.value)}
              onFocus={() => onFieldSelect('complaintIdInput')}
              disabled={loading}
              style={{ 
                width: '100%', background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box',
                outline: selectedField === 'complaintIdInput' ? '2px solid var(--accent-ore)' : 'none',
                boxShadow: selectedField === 'complaintIdInput' ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
              }}
            />
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
            <input 
              type="text" 
              placeholder="Enter PO number"
              value={complaintDetails.poNumber}
              onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, poNumber: e.target.value })}
              onFocus={() => onFieldSelect('poNumber')}
              disabled={loading}
              style={{ 
                width: '100%', background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box',
                outline: selectedField === 'poNumber' ? '2px solid var(--accent-ore)' : 'none',
                boxShadow: selectedField === 'poNumber' ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
              }}
            />
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Dispatch Date</label>
            <input 
              type="date" 
              value={complaintDetails.dispatchDate}
              onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, dispatchDate: e.target.value })}
              onFocus={() => onFieldSelect('dispatchDate')}
              disabled={loading}
              style={{ 
                width: '100%', background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', boxSizing: 'border-box',
                outline: selectedField === 'dispatchDate' ? '2px solid var(--accent-ore)' : 'none',
                boxShadow: selectedField === 'dispatchDate' ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
              }}
            />
            
            <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px', color: 'var(--text-dim)' }}>Complaint Description</label>
            <textarea
              placeholder="Describe the issue in detail..."
              value={complaintDetails.description}
              onChange={(e) => onComplaintDetailsChange({ ...complaintDetails, description: e.target.value })}
              onFocus={() => onFieldSelect('description')}
              rows={3}
              disabled={loading}
              style={{ 
                width: '100%', background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', 
                padding: '8px', borderRadius: '6px', fontSize: '13px', resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit',
                outline: selectedField === 'description' ? '2px solid var(--accent-ore)' : 'none',
                boxShadow: selectedField === 'description' ? '0 0 0 2px rgba(196, 98, 45, 0.3)' : 'none'
              }}
            />
            
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
      </div>
    </div>
  )
}
