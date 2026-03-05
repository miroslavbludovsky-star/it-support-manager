import { NavLink } from 'react-router-dom'

function Layout({ children }) {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h1>IT Support Manager</h1>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/tickets">Tickety</NavLink>
          <NavLink to="/emails">Emaily</NavLink>
          <NavLink to="/assistant">AI Asistent</NavLink>
          <NavLink to="/settings">Nastavení</NavLink>
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout
