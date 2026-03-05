function TicketTimeline({ comments = [], statusChanges = [] }) {
  const events = [
    ...comments.map(c => ({ type: 'comment', date: c.created_at, ...c })),
    ...statusChanges.map(s => ({ type: 'status', date: s.changed_at, ...s })),
  ].sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))

  if (events.length === 0) {
    return <p style={{ color: 'var(--text-muted)' }}>Žádné události</p>
  }

  return (
    <div className="timeline">
      {events.map((event, i) => (
        <div key={i} className="timeline-item">
          <div className="timeline-date">
            {event.date ? new Date(event.date).toLocaleString('cs-CZ') : '—'}
          </div>
          {event.type === 'comment' ? (
            <div>
              <strong>{event.author}</strong>
              <p style={{ marginTop: '0.25rem', whiteSpace: 'pre-wrap' }}>{event.body}</p>
            </div>
          ) : (
            <div>
              <strong>{event.changed_by}</strong> změnil <em>{event.field}</em>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {event.old_value} → {event.new_value}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default TicketTimeline
