function formatPrice(price) {
  return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}

function RankingTable({ bids }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Price order</span>
          <h2>Compliant ranking</h2>
        </div>
        <span className="section-index">02</span>
      </div>
      {bids.length > 0 ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Vendor</th>
                <th>Price</th>
                <th>Compliance</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((bid, index) => (
                <tr key={`${bid.vendor_name}-${index}`}>
                  <td><span className="rank-number">L{index + 1}</span></td>
                  <td className="vendor-cell">{bid.vendor_name}</td>
                  <td>{formatPrice(bid.price)}</td>
                  <td><span className="status-pill status-pill--success">Compliant</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="empty-copy">No compliant bids to rank.</p>
      )}
    </section>
  )
}

export default RankingTable
