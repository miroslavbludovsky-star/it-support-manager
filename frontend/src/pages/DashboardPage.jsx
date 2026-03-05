import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'

function DashboardPage() {
  const [data, setData] = useState(null)
  const [syncStatus, setSyncStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getDashboard(), api.getSyncStatus()])
      .then(([dashboard, sync]) => { setData(dashboard); setSyncStatus(sync) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleSync = async () => {
    setSyncStatus({ status: 'running' })
    try {
      const result = await api.triggerSync()
      setSyncStatus({ status: 'completed', last_run: new Date().toISOString() })
      // Reload dashboard
      const dashboard = await api.getDashboard()
      setData(dashboard)
    } catch (err) {
      setSyncStatus({ status: 'error', error: err.message })
    }
  }

  if (loading) return <div className="loading">Načítám dashboard...</div>

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Dashboard</h2>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {syncStatus && (
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Sync: {syncStatus.status} {syncStatus.last_run ? `(${new Date(syncStatus.last_run).toLocaleString('cs-CZ')})` : ''}
            </span>
          )}
          <button className="btn btn-secondary" onClick={handleSync}>Sync emailů</button>
        </div>
      </div>

      {data && (
        <>
          <div className="card-grid" style={{ marginBottom: '1.5rem' }}>
            <div className="card stat-card">
              <div className="stat-value">{data.total_tickets}</div>
              <div className="stat-label">Celkem ticketů</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value" style={{ color: 'var(--info)' }}>{data.open_tickets}</div>
              <div className="stat-label">Otevřených</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value" style={{ color: 'var(--success)' }}>{data.resolved_tickets}</div>
              <div className="stat-label">Vyřešených</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value" style={{ color: 'var(--danger)' }}>{data.unread_emails}</div>
              <div className="stat-label">Nepřečtených emailů</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value" style={{ color: 'var(--warning)' }}>{data.emails_needing_response}</div>
              <div className="stat-label">Čeká na odpověď</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Tickety dle projektu</h3>
              {Object.entries(data.tickets_by_project).map(([name, count]) => (
                <div key={name} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ fontSize: '0.9rem' }}>{name}</span>
                  <strong>{count}</strong>
                </div>
              ))}
            </div>

            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Poslední tickety</h3>
              {data.recent_tickets.map((t, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.4rem 0', borderBottom: '1px solid var(--border)' }}>
                  <div>
                    <Link to={`/tickets/${t.jira_key}`} style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 500, fontSize: '0.85rem' }}>
                      {t.jira_key}
                    </Link>
                    <span style={{ marginLeft: '0.5rem', fontSize: '0.85rem' }}>{t.summary?.slice(0, 50)}</span>
                  </div>
                  <StatusBadge status={t.status} />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default DashboardPage
