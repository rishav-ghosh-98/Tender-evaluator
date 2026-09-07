function formatPrice(price) {
  return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}

function BidEvaluation({ bid }) {
  return (
    <article className={`bid-card ${bid.overall_compliant ? 'bid-card--compliant' : 'bid-card--failed'}`}>
      <div className="bid-card__header">
        <div>
          <span className="eyebrow">Vendor evaluation</span>
          <h3>{bid.vendor_name}</h3>
        </div>
        <div className="bid-card__meta">
          <strong>{formatPrice(bid.price)}</strong>
          <span className={`status-pill ${bid.overall_compliant ? 'status-pill--success' : 'status-pill--danger'}`}>
            {bid.overall_compliant ? 'Compliant' : 'Non-compliant'}
          </span>
        </div>
      </div>

      {!bid.overall_compliant && bid.reasons.length > 0 && (
        <div className="reason-box">
          <strong>Why this bid failed</strong>
          <ul>
            {bid.reasons.map((reason, index) => <li key={index}>{reason}</li>)}
          </ul>
        </div>
      )}

      <div className="checks-table-wrap">
        <table className="checks-table">
          <thead>
            <tr>
              <th>Requirement</th>
              <th>Required value</th>
              <th>Offered value</th>
              <th>Result</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {bid.checks.map((check) => (
              <tr key={check.requirement} className={check.compliant ? 'check-row--pass' : 'check-row--fail'}>
                <td className="requirement-cell">{check.requirement}</td>
                <td>{check.required_value}</td>
                <td>{check.offered_value}</td>
                <td><span className={`status-pill ${check.compliant ? 'status-pill--success' : 'status-pill--danger'}`}>{check.compliant ? 'Pass' : 'Fail'}</span></td>
                <td>{check.reason || 'Meets requirement'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  )
}

export default BidEvaluation
