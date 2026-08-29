import React from 'react'

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
  onSendMessage,
  onFieldSelect,
  selectedField,
  isListening,
  loading,
  onSubmitComplaintId,
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
  const COMPLAINT_CATEGORIES = [
    'Product Quality',
    'Delivery Issues',
    'Billing',
    'Service',
    'Other',
  ]

  const handleVoiceInput = (field) => {
    onFieldSelect(field)
  }

  return (
    <div className={`msg-row msg-row-${role}`}>
      <div className="msg-avatar">{role === 'bot' ? 'Fe' : '👤'}</div>
      <div className={`msg-bubble ${isError ? 'msg-error' : `msg-${role}`}`}>
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {text}
        </div>

        {/* Complaint Categories */}
        {showComplaintCategories && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {COMPLAINT_CATEGORIES.map((cat) => (
              <button
                key={cat}
                className="chip"
                onClick={() => onCategorySelect(cat)}
                disabled={loading}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* Complaint Form */}
        {showComplaintForm && selectedCategory && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.85em', color: '#666' }}>
              Category: <strong>{selectedCategory}</strong>
            </div>
            <textarea
              placeholder="Describe the issue..."
              value={complaintDetails.description}
              onChange={(e) => {
                onComplaintDetailsChange({
                  ...complaintDetails,
                  description: e.target.value,
                })
                onFieldSelect('description')
              }}
              onBlur={() => onFieldSelect(null)}
              rows={2}
              style={{
                width: '100%',
                padding: '6px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontSize: '0.85em',
                outline: selectedField === 'description' ? '2px solid var(--accent-ore)' : 'none',
              }}
            />
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                className={`btn-mic ${isListening && selectedField === 'description' ? 'listening' : ''}`}
                onClick={() => handleVoiceInput('description')}
                disabled={loading}
                title="Speak your complaint description"
              >
                🎤
              </button>
              <input
                type="text"
                placeholder="PO Number (optional)"
                value={complaintDetails.poNumber}
                onChange={(e) => {
                  onComplaintDetailsChange({
                    ...complaintDetails,
                    poNumber: e.target.value,
                  })
                  onFieldSelect('poNumber')
                }}
                onBlur={() => onFieldSelect(null)}
                style={{
                  flex: 1,
                  padding: '6px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  fontSize: '0.85em',
                  outline: selectedField === 'poNumber' ? '2px solid var(--accent-ore)' : 'none',
                }}
              />
              <button
                className={`btn-mic ${isListening && selectedField === 'poNumber' ? 'listening' : ''}`}
                onClick={() => handleVoiceInput('poNumber')}
                disabled={loading}
                title="Speak PO number"
              >
                🎤
              </button>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder="Dispatch Date (optional)"
                value={complaintDetails.dispatchDate}
                onChange={(e) => {
                  onComplaintDetailsChange({
                    ...complaintDetails,
                    dispatchDate: e.target.value,
                  })
                  onFieldSelect('dispatchDate')
                }}
                onBlur={() => onFieldSelect(null)}
                style={{
                  flex: 1,
                  padding: '6px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  fontSize: '0.85em',
                  outline: selectedField === 'dispatchDate' ? '2px solid var(--accent-ore)' : 'none',
                }}
              />
              <button
                className={`btn-mic ${isListening && selectedField === 'dispatchDate' ? 'listening' : ''}`}
                onClick={() => handleVoiceInput('dispatchDate')}
                disabled={loading}
                title="Speak dispatch date"
              >
                🎤
              </button>
            </div>
            <button
              className="btn-primary"
              onClick={() => {
                onSubmitComplaint(
                  selectedCategory,
                  complaintDetails.description,
                  complaintDetails.poNumber,
                  complaintDetails.dispatchDate
                )
              }}
              disabled={loading || !complaintDetails.description}
            >
              Submit Complaint
            </button>
          </div>
        )}

        {/* Previous Complaints Options */}
        {showPreviousComplaintsOptions && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.9em', fontWeight: '500' }}>What would you like to do?</div>
            <button
              className="chip"
              onClick={() => onSubmitComplaintId('track')}
              disabled={loading}
            >
              Track Existing Complaint
            </button>
            <button
              className="chip"
              onClick={() => onSubmitComplaintId('new')}
              disabled={loading}
            >
              File New Complaint
            </button>
            <div style={{ marginTop: '8px' }}>
              <input
                type="text"
                placeholder="Enter complaint ID to track..."
                value={complaintIdInput}
                onChange={(e) => onComplaintIdChange(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    onSubmitComplaintId('submit')
                  }
                }}
                style={{
                  width: '100%',
                  padding: '6px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  fontSize: '0.85em',
                  marginBottom: '6px',
                }}
              />
              <button
                className="btn-primary small"
                onClick={() => onSubmitComplaintId('submit')}
                disabled={loading || !complaintIdInput.trim()}
              >
                Track
              </button>
            </div>
          </div>
        )}

        {/* Order Products Selection */}
        {showOrderProducts && orderProducts.length > 0 && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.9em', fontWeight: '500' }}>Select a product:</div>
            {orderProducts.map((product) => (
              <button
                key={product.PID}
                className="chip"
                onClick={() => onSelectProduct(product)}
                disabled={loading}
              >
                {product.ProductName} - {product.Grade} ({product.AvailableQty} MT available)
              </button>
            ))}
          </div>
        )}

        {/* Order Form */}
        {showOrderForm && selectedProduct && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.85em', color: '#666' }}>
              <strong>{selectedProduct.ProductName}</strong> - {selectedProduct.Grade}
              <div style={{ fontSize: '0.9em', marginTop: '4px' }}>
                Available: {selectedProduct.AvailableQty} MT
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                className={`btn-mic ${isListening && selectedField === 'orderQuantity' ? 'listening' : ''}`}
                onClick={() => handleVoiceInput('orderQuantity')}
                disabled={loading}
                title="Speak quantity"
              >
                🎤
              </button>
              <input
                type="number"
                placeholder="Quantity (MT)"
                value={orderQuantity}
                onChange={(e) => onOrderQuantityChange(e.target.value)}
                onFocus={() => onFieldSelect('orderQuantity')}
                onBlur={() => onFieldSelect(null)}
                style={{
                  flex: 1,
                  padding: '6px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  fontSize: '0.85em',
                  outline: selectedField === 'orderQuantity' ? '2px solid var(--accent-ore)' : 'none',
                }}
              />
            </div>
            <button
              className="btn-primary"
              onClick={onSubmitOrder}
              disabled={loading || !orderQuantity}
            >
              Place Order
            </button>
          </div>
        )}

        {/* Quotation Products Selection */}
        {showQuotationProducts && quotationProducts.length > 0 && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.9em', fontWeight: '500' }}>Select a product:</div>
            {quotationProducts.map((product) => (
              <button
                key={product.pid}
                className="chip"
                onClick={() => onSelectQuotationProduct(product)}
                disabled={loading}
              >
                {product.product_name} - {product.grade}
              </button>
            ))}
          </div>
        )}

        {/* Quotation Form */}
        {showQuotationForm && selectedQuotationProduct && (
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.85em', color: '#666' }}>
              <strong>{selectedQuotationProduct.product_name}</strong> - {selectedQuotationProduct.grade}
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                className={`btn-mic ${isListening && selectedField === 'quotationQuantity' ? 'listening' : ''}`}
                onClick={() => handleVoiceInput('quotationQuantity')}
                disabled={loading}
                title="Speak quantity"
              >
                🎤
              </button>
              <input
                type="number"
                placeholder="Quantity (MT)"
                value={quotationQuantity}
                onChange={(e) => onQuotationQuantityChange(e.target.value)}
                onFocus={() => onFieldSelect('quotationQuantity')}
                onBlur={() => onFieldSelect(null)}
                style={{
                  flex: 1,
                  padding: '6px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  fontSize: '0.85em',
                  outline: selectedField === 'quotationQuantity' ? '2px solid var(--accent-ore)' : 'none',
                }}
              />
            </div>
            <button
              className="btn-primary"
              onClick={onSubmitQuotation}
              disabled={loading || !quotationQuantity}
            >
              Get Quotation
            </button>
          </div>
        )}

        {/* Company Email Contact */}
        {companyEmail && (
          <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <div style={{ fontSize: '0.85em', marginBottom: '4px' }}>
              Company Email:
            </div>
            <div style={{ fontSize: '0.9em', fontWeight: '500', wordBreak: 'break-all' }}>
              {companyEmail}
            </div>
            {customerName && (
              <div style={{ fontSize: '0.85em', marginTop: '4px', color: '#666' }}>
                Contact: {customerName}
              </div>
            )}
            <a
              href={`mailto:${companyEmail}`}
              style={{
                display: 'inline-block',
                marginTop: '8px',
                padding: '6px 12px',
                backgroundColor: 'var(--accent-ore)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                fontSize: '0.85em',
                cursor: 'pointer',
              }}
            >
              Send Email
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
