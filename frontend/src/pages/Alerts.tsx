import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Send, Mail, MessageSquare, Hash } from 'lucide-react';
import api from '../api/client';
import CountUp from '../components/CountUp';

const CHANNEL_ICONS: Record<string, React.ReactNode> = {
  slack: <Hash size={13} />,
  discord: <MessageSquare size={13} />,
  email: <Mail size={13} />,
};

const CHANNEL_COLORS: Record<string, string> = {
  slack: '#4A154B',
  discord: '#5865F2',
  email: '#0A84FF',
};

// Success rate gauge
const SuccessGauge = ({ rate }: { rate: number }) => {
  const r = 52, cx = 64, cy = 64;
  const circumference = Math.PI * r; // half circle
  const offset = circumference - (rate / 100) * circumference;
  const color = rate > 80 ? '#30D158' : rate > 50 ? '#FF9F0A' : '#FF375F';
  return (
    <svg width={128} height={80} viewBox="0 0 128 80">
      <path d={`M 12 64 A 52 52 0 0 1 116 64`} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={8} strokeLinecap="round" />
      <path d={`M 12 64 A 52 52 0 0 1 116 64`} fill="none" stroke={color} strokeWidth={8} strokeLinecap="round"
        strokeDasharray={circumference} strokeDashoffset={offset}
        style={{ transition: 'stroke-dashoffset 1.2s ease', filter: `drop-shadow(0 0 6px ${color})` }}
      />
      <text x="64" y="58" textAnchor="middle" fill="white" fontSize="22" fontWeight="800" fontFamily="Inter">
        {rate.toFixed(0)}%
      </text>
      <text x="64" y="74" textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="10" fontFamily="Inter">
        SUCCESS
      </text>
    </svg>
  );
};

const Alerts: React.FC = () => {
  const queryClient = useQueryClient();
  const [testing, setTesting] = useState(false);
  const [testPulse, setTestPulse] = useState(false);

  const { data: history, isLoading } = useQuery({
    queryKey: ['webhookHistory'],
    queryFn: () => api.get('/webhook/history').then(r => r.data),
  });

  const { data: stats } = useQuery({
    queryKey: ['webhookStats'],
    queryFn: () => api.get('/webhook/stats').then(r => r.data),
  });

  const retryMutation = useMutation({
    mutationFn: (id: string) => api.post(`/webhook/retry/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['webhookHistory'] }),
  });

  const testWebhook = async () => {
    setTesting(true);
    setTestPulse(true);
    try { await api.post('/webhook/test'); queryClient.invalidateQueries({ queryKey: ['webhookHistory'] }); }
    catch {}
    setTesting(false);
    setTimeout(() => setTestPulse(false), 1000);
  };

  const hist = history ?? [];
  const sent = hist.filter((h: any) => h.status === 'SENT').length;
  const failed = hist.filter((h: any) => h.status === 'FAILED').length;
  const retrying = hist.filter((h: any) => h.status === 'RETRYING').length;
  const successRate = stats?.success_rate ?? (hist.length > 0 ? (sent / hist.length) * 100 : 0);

  const getStatusClass = (s: string) => ({ SENT: 'badge-sent', FAILED: 'badge-failed', PENDING: 'badge-pending', RETRYING: 'badge-retrying' }[s] || 'badge-info');

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>

      {/* Header */}
      <div className="animate-in" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'white', marginBottom: 4 }}>
            Alert <span className="gradient-text">History</span>
          </h1>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Webhook dispatch log and delivery status</p>
        </div>
        <button
          className="btn-primary"
          onClick={testWebhook}
          disabled={testing}
          style={{ position: 'relative', overflow: 'visible' }}
        >
          {testPulse && (
            <span style={{
              position: 'absolute', inset: -4, borderRadius: 99,
              border: '2px solid #0A84FF',
              animation: 'pulse-ring 0.8s ease-out',
            }} />
          )}
          <Send size={14} />
          {testing ? 'Dispatching…' : 'Test Webhook'}
        </button>
      </div>

      {/* Stats bar */}
      <div className="animate-in" style={{ animationDelay: '0.08s' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr 1fr 1fr', gap: 16, marginBottom: 20 }}>
          {/* Gauge */}
          <div className="glass-card" style={{ padding: 20, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <SuccessGauge rate={successRate} />
          </div>
          {/* KPI chips */}
          {[
            { label: 'Total Dispatched', value: hist.length, color: '#0A84FF' },
            { label: 'Failed', value: failed, color: '#FF375F' },
            { label: 'Retrying', value: retrying, color: '#FF9F0A' },
          ].map(({ label, value, color }) => (
            <div key={label} className="glass-card" style={{
              padding: 20,
              boxShadow: `0 8px 32px rgba(0,0,0,0.4), 0 0 30px ${color}15`,
            }}>
              <div style={{ fontSize: 36, fontWeight: 800, color: 'white', letterSpacing: -1 }}>
                <CountUp end={value} />
              </div>
              <div className="section-label" style={{ marginTop: 6 }}>{label}</div>
              <div style={{ marginTop: 10, height: 3, borderRadius: 99, background: 'rgba(255,255,255,0.06)' }}>
                <div style={{ height: '100%', width: `${hist.length > 0 ? (value / hist.length) * 100 : 0}%`, background: color, borderRadius: 99, transition: 'width 1s ease' }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card animate-in" style={{ borderRadius: 20, overflow: 'hidden', padding: 0, animationDelay: '0.16s' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: '100px 80px 1fr 90px 70px 80px 80px',
          padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.07)',
        }}>
          {['Time', 'Channel', 'Endpoint', 'Status', 'Attempts', 'Code', 'Action'].map(h => (
            <div key={h} className="section-label">{h}</div>
          ))}
        </div>

        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} style={{ height: 48, margin: '4px 8px', borderRadius: 10 }} className="shimmer-skeleton" />
          ))
        ) : hist.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 0', color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>
            <Send size={32} style={{ margin: '0 auto 12px', display: 'block', opacity: 0.2 }} />
            No webhook history. Trigger a test alert.
          </div>
        ) : (
          hist.map((wh: any, idx: number) => {
            const channel = wh.target_type?.toLowerCase();
            const bgColor = CHANNEL_COLORS[channel] || '#0A84FF';
            return (
              <div key={wh.id} className="animate-in" style={{
                display: 'grid', gridTemplateColumns: '100px 80px 1fr 90px 70px 80px 80px',
                padding: '12px 16px',
                borderBottom: '1px solid rgba(255,255,255,0.04)',
                transition: 'background 0.15s ease',
                animationDelay: `${idx * 0.03}s`,
              }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', fontFamily: 'monospace', alignSelf: 'center' }}>
                  {new Date(wh.created_at).toLocaleTimeString()}
                </span>
                <div style={{ alignSelf: 'center' }}>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: 4,
                    background: `${bgColor}22`, border: `1px solid ${bgColor}44`,
                    borderRadius: 99, padding: '2px 8px', fontSize: 11, fontWeight: 700,
                    color: bgColor, textTransform: 'capitalize',
                  }}>
                    {CHANNEL_ICONS[channel]}
                    {wh.target_type}
                  </span>
                </div>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', alignSelf: 'center' }}>
                  {wh.endpoint_url || '—'}
                </span>
                <div style={{ alignSelf: 'center' }}>
                  <span className={`badge ${getStatusClass(wh.status)}`}>{wh.status}</span>
                </div>
                <span style={{ fontSize: 13, fontWeight: 700, color: 'rgba(255,255,255,0.7)', alignSelf: 'center' }}>{wh.attempt_count}</span>
                <span style={{ fontSize: 12, color: wh.response_code === 200 ? '#30D158' : '#FF375F', fontFamily: 'monospace', alignSelf: 'center', fontWeight: 600 }}>
                  {wh.response_code || '—'}
                </span>
                <div style={{ alignSelf: 'center' }}>
                  {wh.status === 'FAILED' && (
                    <button
                      className="btn-ghost"
                      onClick={() => retryMutation.mutate(wh.id)}
                      disabled={retryMutation.isPending}
                      style={{ padding: '4px 10px', fontSize: 11, borderRadius: 8 }}
                    >
                      <RefreshCw size={11} />
                      Retry
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Alerts;
