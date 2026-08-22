export default function ProductCard({ product, onAskSpec }) {
  return (
    <div className="product-card">
      <div className="product-card-head">
        <span className="product-id">{product.PID}</span>
        <span className={`pill ${product.PStatus === 'Active' ? 'pill-active' : 'pill-inactive'}`}>
          {product.PStatus || 'Unknown'}
        </span>
      </div>
      <h3>{product.ProductName}</h3>
      <p className="muted">{product.CategoryName || 'Uncategorized'}</p>
      <button className="btn-link" onClick={onAskSpec}>View specifications in chat →</button>
    </div>
  )
}
