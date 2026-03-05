import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'
import TicketTimeline from '../components/TicketTimeline'
import RelatedTickets from '../components/RelatedTickets'

function TicketDetailPage() {
  const { id } = useParams()
  const [ticket, setTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [waitingOn, setWaitingOn] = useState('')

  useEffect(() => {
    const fetchTicket = isNaN(id)
      ? api.getTicketByKey(id)
      : api.getTicket(id)

    fetchTicket
      .then(t => { setTicket(t); setWaitingOn(t.waiting_on || '') })
      .catch(() => setTicket(null))
      .finally(() => setLoading(false))
  }, [id])

  const handleWaitingOnSave = async () => {
    if (!ticket) return
    const updated = await api.updateTicket(ticket.id, { waiting_on: waitingOn || null, waiting_on_manual: true })
    setTicket(updated)
  }

  if (loading) return <div className="loading">Načítám ticket...</div>
  if (!ticket) return <p>Ticket nenalezen.</p>

  return (
    <div>
      <div className="page-header">
        <h2>{ticket.jira_key}: {ticket.summary}</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <div>
          <div className="card">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.9rem' }}>
              <div><strong>Stav:</strong> <StatusBadge status={ticket.status} /></div>
              <div><strong>Priorita:</strong> {ticket.priority}</div>
              <div><strong>Typ:</strong> {ticket.issue_type}</div>
              <div><strong>Rozhodnutí:</strong> {ticket.resolution || '—'}</div>
              <div><strong>Přiřazený:</strong> {ticket.assignee}</div>
              <div><strong>Zadavatel:</strong> {ticket.reporter}</div>
              <div><strong>Projekt:</strong> {ticket.project_name}</div>
              <div><strong>Komponenty:</strong> {ticket.components || '—'}</div>
              <div><strong>Zbývající odhad:</strong> {ticket.remaining_estimate || '—'}</div>
              <div><strong>Odpracováno:</strong> {ticket.time_spent || '—'}</div>
              {ticket.attachments && <div style={{ gridColumn: '1 / -1' }}><strong>Přílohy:</strong> {ticket.attachments}</div>}
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '0.5rem' }}>Čeká na</h3>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <input
                type="text"
                value={waitingOn}
                onChange={e => setWaitingOn(e.target.value)}
                placeholder="Kdo řeší / na koho se čeká"
                style={{ flex: 1, padding: '0.5rem', border: '1px solid var(--border)', borderRadius: '0.375rem' }}
              />
              <button className="btn btn-primary" onClick={handleWaitingOnSave}>Uložit</button>
            </div>
            {ticket.waiting_on_manual && <span className="badge badge-warning" style={{ marginTop: '0.5rem' }}>Ručně nastaveno</span>}
          </div>

          {ticket.description && (
            <div className="card">
              <h3 style={{ marginBottom: '0.5rem' }}>Popis</h3>
              <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{ticket.description}</p>
            </div>
          )}

          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Historie</h3>
            <TicketTimeline comments={ticket.comments} statusChanges={ticket.status_changes} />
          </div>
        </div>

        <div>
          <div className="card">
            <RelatedTickets ticketId={ticket.id} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default TicketDetailPage
