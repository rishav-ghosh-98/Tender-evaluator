function TenderSummary({ tender }) {
  const details = [
    ['Tender Number', tender.tender_number],
    ['Item Description', tender.item_description],
    ['Quantity', tender.quantity],
    ['Warranty', tender.warranty_period],
    ['Delivery Completion', tender.delivery_completion_date],
    ['Evaluation Criteria', tender.evaluation_criteria],
  ]

  return (
    <section className="panel tender-summary">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Tender brief</span>
          <h2>Tender summary</h2>
        </div>
        <span className="section-index">01</span>
      </div>
      <div className="summary-grid">
        {details.map(([label, value]) => (
          <div className="summary-item" key={label}>
            <span>{label}</span>
            <strong>{value || 'Not specified'}</strong>
          </div>
        ))}
      </div>
    </section>
  )
}

export default TenderSummary
