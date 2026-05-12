import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AnimatedBackground from '../components/AnimatedBackground';
import { Activity, Lock, Eye, EyeOff, UserPlus } from 'lucide-react';
import api from '../api/client';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('SRE');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // Register
      await api.post('/auth/register', { email, password, role });
      
      // Auto-login after registration
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);
      
      const { data } = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user_email', email);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#000', position: 'relative', overflow: 'hidden',
    }}>
      <AnimatedBackground />

      <div style={{ position: 'relative', zIndex: 1, width: '100%', maxWidth: 420, padding: '0 20px' }}>
        <div className="glass-card animate-in" style={{
          padding: 48,
          borderRadius: 32,
          boxShadow: '0 8px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15)',
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 32 }}>
            <div style={{
              width: 72, height: 72, borderRadius: '50%',
              background: 'linear-gradient(135deg, #30D158, #5AC8FA)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 40px rgba(48,209,88,0.3)',
              animation: 'pulse-glow 2s ease-in-out infinite',
              marginBottom: 20,
            }}>
              <UserPlus size={32} color="white" />
            </div>
            <h1 className="gradient-text" style={{ fontSize: 32, fontWeight: 800, letterSpacing: -1, marginBottom: 6 }}>
              Join Watchdog
            </h1>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', textAlign: 'center' }}>
              Create your SRE operative account
            </p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="animate-in" style={{ animationDelay: '0.1s' }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                Operative Email
              </label>
              <input
                className="glass-input"
                type="email"
                placeholder="sre@company.io"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="animate-in" style={{ animationDelay: '0.18s' }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                Security Role
              </label>
              <select
                className="glass-input"
                value={role}
                onChange={e => setRole(e.target.value)}
                style={{ appearance: 'none', cursor: 'pointer' }}
              >
                <option value="SRE">Site Reliability Engineer (SRE)</option>
                <option value="DevOps">DevOps Engineer</option>
                <option value="Lead">Platform Lead / Architect</option>
              </select>
            </div>

            <div className="animate-in" style={{ animationDelay: '0.26s', position: 'relative' }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                Security Password
              </label>
              <input
                className="glass-input"
                type={showPass ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                style={{ paddingRight: 48 }}
              />
              <button
                type="button"
                onClick={() => setShowPass(s => !s)}
                style={{
                  position: 'absolute', right: 14, bottom: 14, background: 'none', border: 'none',
                  color: 'rgba(255,255,255,0.35)', cursor: 'pointer', padding: 0,
                }}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            {error && (
              <div style={{
                background: 'rgba(255,55,95,0.12)', border: '1px solid rgba(255,55,95,0.3)',
                borderRadius: 12, padding: '10px 14px', fontSize: 13, color: '#FF375F',
              }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn-primary animate-in"
              disabled={loading}
              style={{ 
                width: '100%', justifyContent: 'center', padding: '14px', fontSize: 15, marginTop: 6, 
                animationDelay: '0.34s', opacity: loading ? 0.7 : 1,
                background: 'var(--gradient-success)',
                boxShadow: '0 4px 20px rgba(48,209,88,0.3)'
              }}
            >
              {loading ? (
                <span style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
              ) : 'Initialize Account'}
            </button>
          </form>

          <div className="animate-in" style={{ animationDelay: '0.42s', marginTop: 24, textAlign: 'center' }}>
            <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.35)' }}>Already have an operative account? </span>
            <Link to="/" style={{ fontSize: 13, color: 'var(--accent-blue)', textDecoration: 'none', fontWeight: 600 }}>Sign In</Link>
          </div>

          <div className="animate-in" style={{ animationDelay: '0.5s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 24 }}>
            <Lock size={11} color="rgba(255,255,255,0.25)" />
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.25)' }}>Secured with JWT · ISO 27001 Compliant</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
