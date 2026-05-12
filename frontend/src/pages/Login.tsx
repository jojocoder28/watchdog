import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AnimatedBackground from '../components/AnimatedBackground';
import { Activity, Lock, Eye, EyeOff } from 'lucide-react';
import api from '../api/client';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
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
      if (err.response?.status === 400) {
        try {
          const form = new URLSearchParams();
          form.append('email', email);
          form.append('password', password);
          const { data: reg } = await api.post('/auth/register', { email, password });
          const form2 = new URLSearchParams();
          form2.append('username', email);
          form2.append('password', password);
          const { data: login } = await api.post('/auth/login', form2, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          });
          localStorage.setItem('token', login.access_token);
          localStorage.setItem('user_email', email);
          navigate('/dashboard');
        } catch {
          setError('Invalid credentials. Please try again.');
        }
      } else {
        setError('Connection error. Is the backend running?');
      }
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
        {/* Glass card */}
        <div className="glass-card animate-in" style={{
          padding: 48,
          borderRadius: 32,
          boxShadow: '0 8px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15)',
        }}>
          {/* Logo */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 32 }}>
            <div style={{
              width: 72, height: 72, borderRadius: '50%',
              background: 'linear-gradient(135deg, #0A84FF, #BF5AF2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 40px rgba(10,132,255,0.5)',
              animation: 'pulse-glow 2s ease-in-out infinite',
              marginBottom: 20,
            }}>
              <Activity size={32} color="white" />
            </div>
            <h1 className="gradient-text" style={{ fontSize: 32, fontWeight: 800, letterSpacing: -1, marginBottom: 6 }}>
              Watchdog
            </h1>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', textAlign: 'center' }}>
              Intelligent Observability Platform
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="animate-in" style={{ animationDelay: '0.1s' }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                Email Address
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

            <div className="animate-in" style={{ animationDelay: '0.18s', position: 'relative' }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                Password
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
              style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: 15, marginTop: 6, animationDelay: '0.26s', opacity: loading ? 0.7 : 1 }}
            >
              {loading ? (
                <span style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
              ) : 'Sign In'}
            </button>
          </form>

          <div className="animate-in" style={{ animationDelay: '0.34s', marginTop: 24, textAlign: 'center' }}>
            <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.35)' }}>Don't have an operative account? </span>
            <Link to="/register" style={{ fontSize: 13, color: 'var(--accent-blue)', textDecoration: 'none', fontWeight: 600 }}>Sign Up</Link>
          </div>

          {/* Footer */}
          <div className="animate-in" style={{ animationDelay: '0.34s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 24 }}>
            <Lock size={11} color="rgba(255,255,255,0.25)" />
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.25)' }}>Secured with JWT · End-to-end encrypted</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
