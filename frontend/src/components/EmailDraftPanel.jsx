import { useState } from 'react'
import { api } from '../api'

function EmailDraftPanel({ emailId }) {
  const [draft, setDraft] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const result = await api.generateDraft(emailId)
      setDraft(result)
    } catch (err) {
      setDraft({ draft_body: `Chyba: ${err.message}`, prompt_used: '' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="draft-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h4>Návrh odpovědi (LLM)</h4>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
          {loading ? 'Generuji...' : draft ? 'Přegenerovat' : 'Generovat návrh'}
        </button>
      </div>
      {draft && (
        <textarea
          className="settings-textarea"
          value={draft.draft_body}
          onChange={e => setDraft({ ...draft, draft_body: e.target.value })}
          style={{ minHeight: '200px' }}
        />
      )}
      {draft && (
        <div style={{ marginTop: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={() => navigator.clipboard.writeText(draft.draft_body)}>
            Kopírovat do schránky
          </button>
        </div>
      )}
    </div>
  )
}

export default EmailDraftPanel
