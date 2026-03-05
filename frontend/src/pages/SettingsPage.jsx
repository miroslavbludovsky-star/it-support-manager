import { useEffect, useState } from 'react'
import { api } from '../api'

function SettingsPage() {
  const [settings, setSettings] = useState({})
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getSettings()
      .then(list => {
        const obj = {}
        list.forEach(s => { obj[s.key] = s.value })
        setSettings(obj)
      })
      .catch(() => {})
  }, [])

  const handleSave = async (key, value) => {
    setSaving(true)
    try {
      await api.updateSetting(key, value)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      alert(`Chyba: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Nastavení</h2>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>LLM System Prompt</h3>
        <textarea
          className="settings-textarea"
          value={settings.llm_prompt || ''}
          onChange={e => setSettings({ ...settings, llm_prompt: e.target.value })}
        />
        <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="btn btn-primary" onClick={() => handleSave('llm_prompt', settings.llm_prompt)} disabled={saving}>
            {saving ? 'Ukládám...' : 'Uložit prompt'}
          </button>
          {saved && <span style={{ color: 'var(--success)', fontSize: '0.85rem' }}>Uloženo</span>}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Konfigurace</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.25rem' }}>
              JIRA sender email
            </label>
            <input
              type="text"
              value={settings.jira_sender || ''}
              onChange={e => setSettings({ ...settings, jira_sender: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid var(--border)', borderRadius: '0.375rem' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.25rem' }}>
              Interval synchronizace (min)
            </label>
            <input
              type="number"
              value={settings.sync_interval || '5'}
              onChange={e => setSettings({ ...settings, sync_interval: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid var(--border)', borderRadius: '0.375rem' }}
            />
          </div>
        </div>
        <div style={{ marginTop: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={() => {
            handleSave('jira_sender', settings.jira_sender)
            handleSave('sync_interval', settings.sync_interval)
          }}>
            Uložit konfiguraci
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
