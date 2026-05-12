import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import AnimatedBackground from './AnimatedBackground';
import {
  LayoutDashboard, FileText, AlertTriangle, Bell, Settings,
  LogOut, ChevronRight, Activity, Menu, X,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/logs',      icon: FileText,         label: 'Log Explorer' },
  { to: '/incidents', icon: AlertTriangle,     label: 'Incidents' },
  { to: '/alerts',    icon: Bell,              label: 'Alert History' },
  { to: '/settings',  icon: Settings,          label: 'Settings' },
];

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const user = localStorage.getItem('user_email') || 'sre@watchdog.io';
  const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_email');
    navigate('/');
  };

  const SidebarContent = () => (
    <>
      {/* Logo */}
      <div style={{ padding: '8px 12px 24px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 12,
            background: 'linear-gradient(135deg, #0A84FF, #BF5AF2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px rgba(10,132,255,0.4)',
            flexShrink: 0,
          }}>
            <Activity size={18} color="white" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'rgba(255,255,255,0.95)' }}>Watchdog</div>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.05em' }}>OBSERVABILITY</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '16px 8px', display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div className="section-label" style={{ padding: '4px 12px 8px' }}>Navigation</div>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 16px',
              borderRadius: 14,
              textDecoration: 'none',
              fontSize: 14,
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.5)',
              background: isActive ? 'rgba(10,132,255,0.15)' : 'transparent',
              borderLeft: isActive ? '3px solid #0A84FF' : '3px solid transparent',
              transition: 'all 0.2s ease',
            })}
          >
            {({ isActive }) => (
              <>
                <Icon size={17} color={isActive ? '#0A84FF' : 'rgba(255,255,255,0.4)'} />
                <span style={{ flex: 1 }}>{label}</span>
                {isActive && <ChevronRight size={13} color="#0A84FF" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom user section */}
      <div style={{ padding: '12px 8px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
          borderRadius: 14, cursor: 'default',
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'linear-gradient(135deg, #0A84FF, #BF5AF2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 13, fontWeight: 700, color: 'white', flexShrink: 0,
          }}>
            {user.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.9)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user}</div>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 4,
              background: 'rgba(48,209,88,0.15)', border: '1px solid rgba(48,209,88,0.3)',
              borderRadius: 99, padding: '1px 7px', fontSize: 9, fontWeight: 700,
              color: '#30D158', letterSpacing: '0.06em',
            }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#30D158', animation: 'pulse-dot 2s infinite' }} />
              PROD
            </div>
          </div>
          <button onClick={handleLogout} className="btn-ghost" style={{ padding: '6px 8px', borderRadius: 10, cursor: 'pointer' }}>
            <LogOut size={14} color="rgba(255,255,255,0.4)" />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#000', position: 'relative', overflow: 'hidden' }}>
      <AnimatedBackground />

      {/* Desktop Sidebar */}
      <aside className="sidebar" style={{
        width: 240, flexShrink: 0, display: 'flex', flexDirection: 'column',
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(30px)',
        WebkitBackdropFilter: 'blur(30px)',
        borderRight: '1px solid rgba(255,255,255,0.08)',
        position: 'relative', zIndex: 10,
      }}>
        <SidebarContent />
      </aside>

      {/* Mobile overlay sidebar */}
      {mobileOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex' }}>
          <div onClick={() => setMobileOpen(false)} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)' }} />
          <aside style={{
            width: 260, flexShrink: 0, display: 'flex', flexDirection: 'column',
            background: 'rgba(10,10,20,0.95)', backdropFilter: 'blur(30px)',
            borderRight: '1px solid rgba(255,255,255,0.08)',
            position: 'relative', zIndex: 51, animation: 'slideUp 0.3s ease',
          }}>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1, overflow: 'hidden' }}>
        {/* Top Bar */}
        <header style={{
          height: 64, flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 24px',
          background: 'rgba(0,0,0,0.5)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              onClick={() => setMobileOpen(true)}
              style={{ display: 'none', background: 'none', border: 'none', color: 'white', padding: 4 }}
              className="mobile-menu-btn"
            >
              <Menu size={20} />
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* Live badge */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'rgba(48,209,88,0.1)', border: '1px solid rgba(48,209,88,0.25)',
              borderRadius: 99, padding: '5px 12px',
            }}>
              <span style={{
                width: 7, height: 7, borderRadius: '50%', background: '#30D158',
                animation: 'pulse-dot 2s infinite',
              }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: '#30D158', letterSpacing: '0.06em' }}>LIVE</span>
            </div>

            <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>Last sync {now}</span>
          </div>
        </header>

        {/* Page Content */}
        <main style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom nav */}
      <nav className="mobile-nav" style={{
        display: 'none', position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
        background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(20px)',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        padding: '8px 0 max(8px, env(safe-area-inset-bottom))',
        justifyContent: 'space-around',
      }}>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} style={({ isActive }) => ({
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            textDecoration: 'none', padding: '4px 12px',
            color: isActive ? '#0A84FF' : 'rgba(255,255,255,0.4)',
          })}>
            <Icon size={20} />
            <span style={{ fontSize: 10, fontWeight: 500 }}>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Layout;
