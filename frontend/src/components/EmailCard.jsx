function EmailCard({ email, onSelect }) {
  const categoryLabels = {
    internal: 'Interní',
    external: 'Externí',
    jira: 'JIRA',
  }
  const categoryClass = {
    internal: 'badge-info',
    external: 'badge-warning',
    jira: 'badge-default',
  }

  return (
    <div className="card" onClick={() => onSelect?.(email)} style={{ cursor: 'pointer' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <div>
          <strong style={{ fontSize: '0.9rem' }}>{email.sender_name || email.sender_email}</strong>
          {!email.is_read && <span className="badge badge-danger" style={{ marginLeft: '0.5rem' }}>Nový</span>}
        </div>
        <span className={`badge ${categoryClass[email.category] || 'badge-default'}`}>
          {categoryLabels[email.category] || email.category}
        </span>
      </div>
      <p style={{ fontWeight: 500, fontSize: '0.9rem' }}>{email.subject}</p>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        <span>{email.received_at ? new Date(email.received_at).toLocaleString('cs-CZ') : ''}</span>
        {email.needs_response && <span style={{ color: 'var(--danger)' }}>Čeká na odpověď</span>}
      </div>
    </div>
  )
}

export default EmailCard
