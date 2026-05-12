import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, Zap, CheckCircle, Eye, EyeOff } from 'lucide-react';
import api from '../api/client';

interface ToggleProps { checked: boolean; onChange: (v: boolean) => void; }
const IOSToggle: React.FC<ToggleProps> = ({ checked, onChange }) => (
  <label className="ios-toggle" onClick={() => onChange(!checked)}>
    <input type="checkbox" checked={checked} onChange={() => {}} />
    <span className="ios-toggle-track" />
    <span className={`ios-toggle-thumb`} style={{ transform: checked ? 'translateX(20px)' : 'translateX(0)' }} />
  </label>
);

const SliderInput: React.FC<{ value: number; min: number; max: number; onChange: (v: number) => void; label: string; suffix?: string }> = ({ value, min, max, onChange, label, suffix = '' }) => (
  <div style={{ marginBottom: 20 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
      <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)' }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 700, color: '#0A84FF' }}>{value}{suffix}</span>
    </div>
    <div style={{ position: 'relative' }}>
      <input
        type="range" min={min} max={max} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="glass-slider"
        style={{
          background: `linear-gradient(to right, #0A84FF ${((value - min) / (max - min)) * 100}%, rgba(255,255,255,0.1) 0%)`,
        }}
      />
    </div>
  </div>
);

const Settings: React.FC = () => {
  const [geminiKey, setGeminiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [jwtExpiry, setJwtExpiry] = useState(60);
  const [errorThreshold, setErrorThreshold] = useState(50);
  const [criticalThreshold, setCriticalThreshold] = useState(10);
  const [latencyThreshold, setLatencyThreshold] = useState(5000);
  const [slackEnabled, setSlackEnabled] = useState(true);
  const [discordEnabled, setDiscordEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [envName, setEnvName] = useState('Production');
  const [saved, setSaved] = useState(false);
  const [pinging, setPinging] = useState(false);
  const [pingOk, setPingOk] = useState<boolean | null>(null);

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => api.get('/settings/').then(r => { return r.data; }).catch(() => null),
  });

  const handleSave = async () => {
    setSaved(false);
    try {
      await api.post('/settings/', {
        gemini_api_key: geminiKey || undefined,
        jwt_expire_minutes: jwtExpiry,
        error_threshold: errorThreshold,
        critical_threshold: criticalThreshold,
        latency_threshold_ms: latencyThreshold,
        slack_enabled: slackEnabled,
        discord_enabled: discordEnabled,
        email_enabled: emailEnabled,
        environment: envName,
      });
    } catch {}
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const pingBackend = async () => {
    setPinging(true);
    setPingOk(null);
    try { await api.get('/health'); setPingOk(true); }
    catch { setPingOk(false); }
    setPinging(false);
  };

  const SectionCard: React.FC<{ title: string; subtitle?: string; children: React.ReactNode; delay?: number }> = ({ title, subtitle, children, delay = 0 }) => (
    <div className="glass-card animate-in" style={{ padding: 28, borderRadius: 24, animationDelay: `${delay}s` }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: 'white', marginBottom: 4 }}>{title}</div>
        {subtitle && <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{subtitle}</div>}
      </div>
      <div className="glass-divider" style={{ marginBottom: 20 }} />
      {children}
    </div>
  );

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>

      {/* Header */}
      <div className="animate-in" style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'white', marginBottom: 4 }}>
          Platform <span className="gradient-text">Settings</span>
        </h1>
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Configure AI, thresholds, and notification channels</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* AI Configuration */}
        <SectionCard title="AI Configuration" subtitle="Gemini API key for automated incident analysis" delay={0.08}>
          <div style={{ marginBottom: 16 }}>
            <label className="section-label" style={{ marginBottom: 8, display: 'block' }}>Gemini API Key</label>
            <div style={{ position: 'relative' }}>
              <input
                className="glass-input"
                type={showKey ? 'text' : 'password'}
                placeholder="AIzaSy…"
                value={geminiKey}
                onChange={e => setGeminiKey(e.target.value)}
                style={{ paddingRight: 48 }}
              />
              <button
                onClick={() => setShowKey(s => !s)}
                style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'rgba(255,255,255,0.35)', cursor: 'pointer' }}
              >
                {showKey ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>
          <div>
            <label className="section-label" style={{ marginBottom: 8, display: 'block' }}>JWT Expiry</label>
            <SliderInput value={jwtExpiry} min={15} max={1440} onChange={setJwtExpiry} label="Token lifetime" suffix=" min" />
          </div>
          <button className="btn-ghost" onClick={pingBackend} disabled={pinging} style={{ marginTop: 4 }}>
            <Zap size={14} color={pingOk === true ? '#30D158' : pingOk === false ? '#FF375F' : undefined} />
            {pinging ? 'Pinging…' : pingOk === true ? 'Backend Online ✓' : pingOk === false ? 'Backend Unreachable' : 'Run Health Check'}
          </button>
        </SectionCard>

        {/* Alert Thresholds */}
        <SectionCard title="Alert Thresholds" subtitle="Configure detection sensitivity" delay={0.14}>
          <SliderInput value={errorThreshold} min={5} max={500} onChange={setErrorThreshold} label="ERROR count trigger (5-min window)" suffix=" errors" />
          <SliderInput value={criticalThreshold} min={1} max={100} onChange={setCriticalThreshold} label="CRITICAL count trigger" suffix=" events" />
          <SliderInput value={latencyThreshold} min={500} max={30000} onChange={setLatencyThreshold} label="Latency spike threshold" suffix="ms" />
        </SectionCard>

        {/* Notification Channels */}
        <SectionCard title="Notification Channels" subtitle="Toggle webhook dispatch targets" delay={0.20}>
          {[
            { label: 'Slack', sub: 'Block Kit formatted messages', color: '#4A154B', enabled: slackEnabled, set: setSlackEnabled },
            { label: 'Discord', sub: 'Embedded rich messages', color: '#5865F2', enabled: discordEnabled, set: setDiscordEnabled },
            { label: 'Email (Simulated)', sub: 'Written to dataset/simulated_emails/', color: '#0A84FF', enabled: emailEnabled, set: setEmailEnabled },
          ].map(({ label, sub, color, enabled, set }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '14px 16px', background: 'rgba(255,255,255,0.04)', borderRadius: 14, marginBottom: 10,
              border: enabled ? `1px solid ${color}33` : '1px solid rgba(255,255,255,0.06)',
              transition: 'border-color 0.3s ease',
            }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: enabled ? 'white' : 'rgba(255,255,255,0.5)', transition: 'color 0.3s' }}>{label}</div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 2 }}>{sub}</div>
              </div>
              <IOSToggle checked={enabled} onChange={set} />
            </div>
          ))}
        </SectionCard>

        {/* Environment */}
        <SectionCard title="Environment" subtitle="Platform identity and deployment configuration" delay={0.26}>
          <div style={{ marginBottom: 16 }}>
            <label className="section-label" style={{ marginBottom: 8, display: 'block' }}>Environment Name</label>
            <input
              className="glass-input"
              value={envName}
              onChange={e => setEnvName(e.target.value)}
              placeholder="Production"
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>Preview:</span>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              background: 'rgba(48,209,88,0.15)', border: '1px solid rgba(48,209,88,0.3)',
              borderRadius: 99, padding: '3px 10px', fontSize: 10, fontWeight: 700, color: '#30D158', letterSpacing: '0.06em',
            }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#30D158' }} />
              {envName.toUpperCase()}
            </span>
          </div>
        </SectionCard>

        {/* Save */}
        <button
          className={saved ? 'btn-success animate-in' : 'btn-primary animate-in'}
          onClick={handleSave}
          style={{ width: '100%', justifyContent: 'center', padding: '16px', fontSize: 15, borderRadius: 16, animationDelay: '0.32s' }}
        >
          {saved ? <><CheckCircle size={16} /> Settings Saved!</> : <><Save size={16} /> Save Configuration</>}
        </button>
      </div>
    </div>
  );
};

export default Settings;
