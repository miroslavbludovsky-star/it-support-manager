import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

function RelatedTickets({ ticketId }) {
  const [related, setRelated] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!ticketId) return
    api.getRelatedTickets(ticketId)
      .then(setRelated)
      .catch(() => setRelated([]))
      .finally(() => setLoading(false))
  }, [ticketId])

  if (loading) return <div className="loading">Hledám podobné tickety...</div>
  if (related.length === 0) return <p style={{ color: 'var(--text-muted)' }}>Žádné podobné tickety</p>

  return (
    <div>
      <h4 style={{ marginBottom: '0.75rem' }}>Podobné tickety</h4>
      {related.map((r, i) => (
        <div key={i} className="card" style={{ padding: '0.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Link to={`/tickets/${r.jira_key}`} style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>
              {r.jira_key}
            </Link>
            <span className="badge badge-default">{Math.round(r.similarity * 100)}%</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{r.summary}</p>
        </div>
      ))}
    </div>
  )
}

export default RelatedTickets
