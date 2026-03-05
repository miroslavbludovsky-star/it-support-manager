function FilterBar({ filters, onChange }) {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="filter-bar">
      <input
        type="text"
        placeholder="Hledat (klíč, název)..."
        value={filters.search || ''}
        onChange={e => handleChange('search', e.target.value)}
      />
      <select value={filters.status || ''} onChange={e => handleChange('status', e.target.value)}>
        <option value="">Všechny stavy</option>
        <option value="V řešení">V řešení</option>
        <option value="Upřesnit">Upřesnit</option>
        <option value="Vyřešeno">Vyřešeno</option>
        <option value="Nový">Nový</option>
      </select>
      <select value={filters.priority || ''} onChange={e => handleChange('priority', e.target.value)}>
        <option value="">Všechny priority</option>
        <option value="Blocker">Blocker</option>
        <option value="Critical">Critical</option>
        <option value="Major">Major</option>
        <option value="Normal">Normal</option>
        <option value="Minor">Minor</option>
      </select>
    </div>
  )
}

export default FilterBar
