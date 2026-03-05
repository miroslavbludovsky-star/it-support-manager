import { useEffect, useState } from 'react'
import { api } from '../api'
import EmailCard from '../components/EmailCard'
import EmailDraftPanel from '../components/EmailDraftPanel'

function EmailsPage() {
  const [emails, setEmails] = useState([])
  const [selectedEmail, setSelectedEmail] = useState(null)
  const [tab, setTab] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const params = {}
    if (tab === 'internal') params.category = 'internal'
    if (tab === 'external') params.category = 'external'
    if (tab === 'needs_response') params.needs_response = true

    setLoading(true)
    api.getEmails(params)
      .then(setEmails)
      .catch(() => setEmails([]))
      .finally(() => setLoading(false))
  }, [tab])

  const handleSelectEmail = async (email) => {
    try {
      const detail = await api.getEmail(email.id)
      setSelectedEmail(detail)
    } catch {
      setSelectedEmail(email)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Emaily</h2>
      </div>

      <div className="tabs">
        {[
          ['all', 'Všechny'],
          ['internal', 'Interní'],
          ['external', 'Externí'],
          ['needs_response', 'Čeká na odpověď'],
        ].map(([key, label]) => (
          <div key={key} className={`tab ${tab === key ? 'active' : ''}`} onClick={() => setTab(key)}>
            {label}
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selectedEmail ? '1fr 1fr' : '1fr', gap: '1rem' }}>
        <div>
          {loading ? (
            <div className="loading">Načítám emaily...</div>
          ) : emails.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>Žádné emaily.</p>
          ) : (
            emails.map(e => <EmailCard key={e.id} email={e} onSelect={handleSelectEmail} />)
          )}
        </div>

        {selectedEmail && (
          <div>
            <div className="card">
              <h3>{selectedEmail.subject}</h3>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                Od: {selectedEmail.sender_name} &lt;{selectedEmail.sender_email}&gt;
                <br />
                {selectedEmail.received_at && new Date(selectedEmail.received_at).toLocaleString('cs-CZ')}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                {selectedEmail.body_text}
              </div>
            </div>
            <EmailDraftPanel emailId={selectedEmail.id} />
          </div>
        )}
      </div>
    </div>
  )
}

export default EmailsPage
