import { useState } from 'react'
import { api } from '../api'

function AssistantChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const result = await api.chat(input)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.answer,
        relatedTickets: result.related_tickets,
      }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Chyba: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem' }}>
            <p>Zeptejte se na cokoliv o vašich ticketech.</p>
            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
              Např.: "Jaké tickety máme pro Mladou Boleslav?" nebo "Řešili jsme problém s certifikáty?"
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            {msg.relatedTickets && msg.relatedTickets.length > 0 && (
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: msg.role === 'user' ? 'rgba(255,255,255,0.7)' : 'var(--text-muted)' }}>
                Související: {msg.relatedTickets.join(', ')}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="loading">Přemýšlím...</div>}
      </div>
      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Zeptejte se na tickety, projekty, historii..."
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={handleSend} disabled={loading}>
          Odeslat
        </button>
      </div>
    </div>
  )
}

export default AssistantChat
