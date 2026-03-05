import { useEffect, useState } from 'react'
import { api } from '../api'
import TicketCard from '../components/TicketCard'
import FilterBar from '../components/FilterBar'

function TicketsPage() {
  const [tickets, setTickets] = useState([])
  const [filters, setFilters] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (filters.search) params.search = filters.search
    if (filters.status) params.status = filters.status
    if (filters.priority) params.priority = filters.priority

    api.getTickets(params)
      .then(setTickets)
      .catch(() => setTickets([]))
      .finally(() => setLoading(false))
  }, [filters])

  return (
    <div>
      <div className="page-header">
        <h2>Tickety</h2>
      </div>
      <FilterBar filters={filters} onChange={setFilters} />
      {loading ? (
        <div className="loading">Načítám tickety...</div>
      ) : tickets.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>Žádné tickety nenalezeny.</p>
      ) : (
        <div className="card-grid">
          {tickets.map(t => <TicketCard key={t.id} ticket={t} />)}
        </div>
      )}
    </div>
  )
}

export default TicketsPage
