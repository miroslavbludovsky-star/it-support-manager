function StatusBadge({ status }) {
  const statusMap = {
    'Vyřešeno': 'badge-success',
    'V řešení': 'badge-info',
    'Upřesnit': 'badge-warning',
    'Nový': 'badge-default',
  }
  const cls = statusMap[status] || 'badge-default'
  return <span className={`badge ${cls}`}>{status}</span>
}

export default StatusBadge
