function RecommendedBid({ bid }) {
  if (!bid) {
    return (
      <section className="panel recommendation recommendation--empty">
        <span className="eyebrow">Decision signal</span>
        <h2>No compliant bid</h2>
        <p>The submitted bids did not produce an eligible recommendation.</p>
      </section>
    )
  }

  return (
    <section className="panel recommendation">
      <div className="recommendation__mark">L1</div>
      <div className="recommendation__content">
        <span className="eyebrow">Recommended bid</span>
        <h2>{bid.vendor_name}</h2>
        <p>Lowest price among all compliant bids.</p>
      </div>
      <div className="recommendation__price">
        <span>Bid price</span>
        <strong>₹{bid.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
        <span className="status-pill status-pill--success">Compliant</span>
      </div>
    </section>
  )
}

export default RecommendedBid
