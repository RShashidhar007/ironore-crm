import ReactMarkdown from 'react-markdown'

/**
 * ChatMessage Component
 * Renders individual chat messages and form elements
 */
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
  showOrderProducts,
  orderProducts,
  onSelectProduct,
  showOrderForm,
  selectedProduct,
  orderQuantity,
  onOrderQuantityChange,
  onSubmitOrder,
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
  loading,
}) {
  const isUser = role === 'user'
  
  return (
    <div className={`msg-row ${isUser ? 'msg-row-user' : 'msg-row-bot'}`}>
      {!isUser && <div className="msg-avatar">Fe</div>}
      <div className={`msg-bubble ${isUser ? 'msg-user' : 'msg-bot'} ${isError ? 'msg-error' : ''}`}>
        <ReactMarkdown>{text}</ReactMarkdown>
        
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
