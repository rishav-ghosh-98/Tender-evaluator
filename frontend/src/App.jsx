import { useState } from 'react'
import { evaluateTender } from './api/evaluationApi'
import BidEvaluation from './components/BidEvaluation'
import FileUpload from './components/FileUpload'
import RecommendedBid from './components/RecommendedBid'
import RankingTable from './components/RankingTable'
import TenderSummary from './components/TenderSummary'

const bidSlots = ['bid1', 'bid2', 'bid3', 'bid4']

function App() {
  const [tender, setTender] = useState(null)
  const [bids, setBids] = useState({ bid1: null, bid2: null, bid3: null, bid4: null })
  const [fileErrors, setFileErrors] = useState({})
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  function updateTender(file, validationError) {
    setTender(file)
    setFileErrors((current) => ({ ...current, tender: validationError }))
    setResults(null)
    setError('')
  }

  function updateBid(name, file, validationError) {
    setBids((current) => ({ ...current, [name]: file }))
    setFileErrors((current) => ({ ...current, [name]: validationError }))
    setResults(null)
    setError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setResults(null)

    const selectedBids = bidSlots.filter((slot) => bids[slot])
    const hasFileError = Object.values(fileErrors).some(Boolean)

    if (!tender) {
      setError('Upload the tender PDF before evaluating bids.')
      return
    }

    if (selectedBids.length === 0) {
      setError('Upload at least one vendor bid before evaluating.')
      return
    }

    if (hasFileError) {
      setError('Resolve the file validation messages before evaluating.')
      return
    }

    const formData = new FormData()
    formData.append('tender', tender)
    selectedBids.forEach((slot) => formData.append(slot, bids[slot]))

    setIsLoading(true)
    try {
      const evaluation = await evaluateTender(formData)
      setResults(evaluation)
    } catch (requestError) {
      setError(requestError.message || 'The evaluation request failed.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark">TE</span>
          <span>Tender intelligence</span>
        </div>
        <span className="connection-status"><i /> Local API · Ready</span>
      </header>

      <section className="hero">
        <div className="hero__copy">
          <span className="eyebrow">Procurement workspace / 01</span>
          <h1>Tender Bid<br /><em>Evaluation</em> System</h1>
          <p>Turn tender documents and vendor submissions into a clear, defensible award shortlist.</p>
        </div>
        <div className="hero__signal" aria-hidden="true">
          <span className="signal-line signal-line--one" />
          <span className="signal-line signal-line--two" />
          <span className="signal-label">PDF → decision</span>
        </div>
      </section>

      <form className="workspace" onSubmit={handleSubmit}>
        <section className="panel upload-panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Source documents</span>
              <h2>Build an evaluation set</h2>
            </div>
            <span className="section-index">00</span>
          </div>
          <div className="upload-grid">
            <div className="tender-upload">
              <FileUpload label="Tender document" file={tender} onChange={updateTender} required />
              {fileErrors.tender && <p className="field-error">{fileErrors.tender}</p>}
            </div>
            <div className="bids-upload">
              <div className="subheading">
                <span>Vendor bids</span>
                <small>Optional slots · minimum 1</small>
              </div>
              <div className="bid-upload-grid">
                {bidSlots.map((slot, index) => (
                  <div key={slot}>
                    <FileUpload label={`Bid ${index + 1}`} file={bids[slot]} onChange={(file, message) => updateBid(slot, file, message)} />
                    {fileErrors[slot] && <p className="field-error">{fileErrors[slot]}</p>}
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="action-row">
            <span className="action-hint">PDF files only · evaluation runs against the live local API</span>
            <button className="primary-button" type="submit" disabled={isLoading}>
              {isLoading ? <><span className="spinner" /> Evaluating...</> : <>Evaluate Bids <span>↗</span></>}
            </button>
          </div>
          {error && <div className="alert alert--error" role="alert">{error}</div>}
        </section>
      </form>

      {results && (
        <section className="results-stack">
          <TenderSummary tender={results.tender} />
          <RecommendedBid bid={results.recommended_bid} />
          <RankingTable bids={results.ranked_bids} />
          <section className="evaluation-section">
            <div className="section-heading section-heading--results">
              <div>
                <span className="eyebrow">Audit trail</span>
                <h2>Detailed bid evaluation</h2>
              </div>
              <span className="section-index">03</span>
            </div>
            <div className="evaluation-list">
              {results.bid_evaluations.map((bid, index) => <BidEvaluation bid={bid} key={`${bid.vendor_name}-${index}`} />)}
            </div>
          </section>
        </section>
      )}

      <footer className="footer">
        <span>Tender Bid Evaluation System</span>
        <span>Decision support · Human review required</span>
      </footer>
    </main>
  )
}

export default App
