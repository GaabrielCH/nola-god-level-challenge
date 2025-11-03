import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { BarChart3, TrendingUp, Store, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import StoreComparison from './pages/StoreComparison';
import CustomDashboard from './pages/CustomDashboard';

function App() {
  const [currentPath, setCurrentPath] = useState('/');

  useEffect(() => {
    setCurrentPath(window.location.pathname);
  }, []);

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        {/* Sidebar */}
        <aside style={{
          width: '250px',
          backgroundColor: 'var(--surface)',
          borderRight: '1px solid var(--border)',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '2rem'
        }}>
          <div>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: 'var(--primary)',
              marginBottom: '0.5rem'
            }}>
              🍔 Nola Analytics
            </h1>
            <p style={{
              fontSize: '0.875rem',
              color: 'var(--text-secondary)'
            }}>
              Restaurant Intelligence
            </p>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <NavLink to="/" icon={<BarChart3 size={20} />} active={currentPath === '/'}>
              Dashboard
            </NavLink>
            <NavLink to="/analytics" icon={<TrendingUp size={20} />} active={currentPath === '/analytics'}>
              Análises
            </NavLink>
            <NavLink to="/stores" icon={<Store size={20} />} active={currentPath === '/stores'}>
              Comparar Lojas
            </NavLink>
            <NavLink to="/custom" icon={<Settings size={20} />} active={currentPath === '/custom'}>
              Dashboard Customizado
            </NavLink>
          </nav>

          <div style={{ marginTop: 'auto', padding: '1rem', backgroundColor: 'var(--background)', borderRadius: '0.5rem' }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Nola God Level Challenge 2025
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Desenvolvido para Maria e donos de restaurantes
            </p>
          </div>
        </aside>

        {/* Main content */}
        <main style={{ flex: 1, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/stores" element={<StoreComparison />} />
            <Route path="/custom" element={<CustomDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

interface NavLinkProps {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  active?: boolean;
}

function NavLink({ to, icon, children, active }: NavLinkProps) {
  return (
    <Link
      to={to}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.75rem 1rem',
        borderRadius: '0.5rem',
        textDecoration: 'none',
        color: active ? 'var(--primary)' : 'var(--text)',
        backgroundColor: active ? 'var(--background)' : 'transparent',
        fontWeight: active ? '600' : '500',
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.backgroundColor = 'var(--background)';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.backgroundColor = 'transparent';
        }
      }}
    >
      {icon}
      {children}
    </Link>
  );
}

export default App;
