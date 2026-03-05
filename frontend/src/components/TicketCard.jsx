import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge'

function TicketCard({ ticket }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <Link to={`/tickets/${ticket.id}`} style={{ fontWeight: 600, color: 'var(--primary)', textDecoration: 'none' }}>
          {ticket.jira_key}
        </Link>
        <StatusBadge status={ticket.status} />
      </div>
      <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>{ticket.summary}</p>
      <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        <span>{ticket.project_name}</span>
        <span>{ticket.assignee}</span>
        {ticket.waiting_on && <span style={{ color: 'var(--warning)' }}>Čeká na: {ticket.waiting_on}</span>}
      </div>
    </div>
  )
}

export default TicketCard
