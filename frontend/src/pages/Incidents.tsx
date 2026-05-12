import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Zap, X, Sparkles, ChevronRight, CheckCircle } from 'lucide-react';
import api from '../api/client';
import Typewriter from '../components/Typewriter';
import { SEVERITY_COLORS } from '../utils/chartTheme';

const Incidents: React.FC = () => {
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<any>(null);
  const [detecting, setDetecting] = useState(false);

  const { data: incidents, isLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => api.get('/anomaly/incidents').then(r => r.data),
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/anomaly/incidents/${id}`, { status: 'RESOLVED' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setSelected(null);
    },
  });

  const escalateMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/anomaly/incidents/${id}`, { status: 'INVESTIGATING' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setSelected((prev: any) => prev ? { ...prev, status: 'INVESTIGATING' } : null);
    },
  });

  const runDetection = async () => {
    setDetecting(true);
    try { await api.post('/anomaly/detect'); queryClient.invalidateQueries({ queryKey: ['incidents'] }); }
    catch {}
    setDetecting(false);
  };

  const inc = incidents ?? [];
  const open = inc.filter((i: any) => i.status === 'OPEN').length;
  const investigating = inc.filter((i: any) => i.status === 'INVESTIGATING').length;
  const resolved = inc.filter((i: any) => i.status === 'RESOLVED').length;
  const critical = inc.filter((i: any) => i.severity === 'CRITICAL').length;

  const getStatusBadgeClass = (s: string) => ({ OPEN: 'badge-open', INVESTIGATING: 'badge-investigating', RESOLVED: 'badge-resolved' }[s] || 'badge-info');

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto', position: 'relative' }}>

      {/* Header */}
      <div className="animate-in" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'white', marginBottom: 4 }}>
            Incident <span className="gradient-text">Center</span>
          </h1>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>ML-powered anomaly detection & triage</p>
        </div>
        <button className="btn-primary" onClick={runDetection} disabled={detecting}>
          <Zap size={14} />
          {detecting ? 'Running Detection…' : 'Run Detection'}
        </button>
      </div>

      {/* Stats strip */}
      <div className="glass-card animate-in" style={{ padding: '14px 24px', borderRadius: 20, marginBottom: 20, animationDelay: '0.08s' }}>
        <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
          {[
            { label: 'Open', value: open, color: '#FF375F' },
            { label: 'Investigating', value: investigating, color: '#FF9F0A' },
            { label: 'Resolved', value: resolved, color: '#30D158' },
            { label: 'Critical', value: critical, color: '#FF375F' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
              <span style={{ fontSize: 22, fontWeight: 800, color: 'white' }}>{value}</span>
              <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card animate-in" style={{ borderRadius: 20, overflow: 'hidden', padding: 0, animationDelay: '0.16s' }}>
        {/* Header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 120px 90px 120px 100px 30px',
          padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.07)',
        }}>
          {['Incident', 'Service', 'Severity', 'Status', 'Confidence', ''].map(h => (
            <div key={h} className="section-label">{h}</div>
          ))}
        </div>

        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} style={{ height: 52, margin: '4px 8px', borderRadius: 10 }} className="shimmer-skeleton" />
          ))
        ) : inc.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 0', color: 'rgba(255,255,255,0.25)' }}>
            <Zap size={32} style={{ margin: '0 auto 12px', display: 'block', opacity: 0.2 }} />
            No incidents detected. Run detection to scan logs.
          </div>
        ) : (
          inc.map((incident: any, idx: number) => {
            const color = SEVERITY_COLORS[incident.severity] || '#888';
            const conf = incident.confidence_score ?? 0;
            return (
              <div
                key={incident.id}
                onClick={() => setSelected(incident)}
                className="animate-in"
                style={{
                  display: 'grid', gridTemplateColumns: '1fr 120px 90px 120px 100px 30px',
                  padding: '13px 16px', cursor: 'pointer',
                  borderLeft: `3px solid ${color}`,
                  background: `${color}06`,
                  borderBottom: '1px solid rgba(255,255,255,0.04)',
                  transition: 'background 0.15s ease',
                  animationDelay: `${idx * 0.04}s`,
                }}
                onMouseEnter={e => (e.currentTarget.style.background = `${color}12`)}
                onMouseLeave={e => (e.currentTarget.style.background = `${color}06`)}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'white', marginBottom: 2 }}>{incident.title}</div>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)' }}>{incident.incident_type} · {new Date(incident.created_at).toLocaleString()}</div>
                </div>
                <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)', alignSelf: 'center' }}>{incident.affected_service || '—'}</span>
                <div style={{ alignSelf: 'center' }}>
                  <span className={`badge badge-${incident.severity.toLowerCase()}`}>{incident.severity}</span>
                </div>
                <div style={{ alignSelf: 'center' }}>
                  <span className={`badge ${getStatusBadgeClass(incident.status)}`}>{incident.status}</span>
                </div>
                <div style={{ alignSelf: 'center' }}>
                  <div style={{ background: 'rgba(255,255,255,0.08)', borderRadius: 99, height: 4, overflow: 'hidden', marginBottom: 3 }}>
                    <div style={{ height: '100%', width: `${conf * 100}%`, background: color, borderRadius: 99 }} />
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)' }}>{(conf * 100).toFixed(0)}%</div>
                </div>
                <ChevronRight size={14} color="rgba(255,255,255,0.3)" style={{ alignSelf: 'center' }} />
              </div>
            );
          })
        )}
      </div>

      {/* Slide-in Drawer */}
      {selected && (
        <>
          {/* Overlay */}
          <div onClick={() => setSelected(null)} style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 40,
            backdropFilter: 'blur(4px)',
          }} />

          {/* Drawer */}
          <div style={{
            position: 'fixed', right: 0, top: 0, bottom: 0, width: 480,
            background: 'rgba(8,8,20,0.97)',
            backdropFilter: 'blur(40px)',
            WebkitBackdropFilter: 'blur(40px)',
            borderLeft: '1px solid rgba(255,255,255,0.12)',
            zIndex: 50, overflowY: 'auto',
            animation: 'slideInRight 0.35s cubic-bezier(0.175,0.885,0.32,1.275) both',
            boxShadow: '-20px 0 60px rgba(0,0,0,0.6)',
            display: 'flex', flexDirection: 'column',
          }}>
            {/* Drawer header */}
            <div style={{ padding: '24px 24px 0', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span className={`badge badge-${selected.severity?.toLowerCase()}`}>{selected.severity}</span>
                    <span className={`badge ${getStatusBadgeClass(selected.status)}`}>{selected.status}</span>
                  </div>
                  <h2 style={{ fontSize: 18, fontWeight: 700, color: 'white', lineHeight: 1.3 }}>{selected.title}</h2>
                </div>
                <button onClick={() => setSelected(null)} className="btn-ghost" style={{ padding: '6px 8px', borderRadius: 10, flexShrink: 0 }}>
                  <X size={16} />
                </button>
              </div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                {selected.incident_type} · {selected.affected_service || 'System'} · {new Date(selected.created_at).toLocaleString()}
              </div>
            </div>

            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20, flex: 1 }}>
              {/* AI Summary */}
              {selected.ai_analysis && (
                <div style={{
                  background: 'rgba(191,90,242,0.08)',
                  border: '1px solid rgba(191,90,242,0.25)',
                  borderRadius: 16, padding: 16,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: 8,
                      background: 'linear-gradient(135deg,#BF5AF2,#0A84FF)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Sparkles size={13} color="white" />
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700, color: '#BF5AF2', letterSpacing: '0.06em', textTransform: 'uppercase' }}>AI Analysis</span>
                  </div>
                  <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)', lineHeight: 1.7 }}>
                    <Typewriter text={selected.ai_analysis} speed={12} />
                  </p>
                  <div style={{ fontSize: 10, color: 'rgba(191,90,242,0.5)', marginTop: 10, fontWeight: 600 }}>
                    ✦ Powered by Gemini 2.5 Flash
                  </div>
                </div>
              )}

              {/* Details */}
              <div>
                <div className="section-label" style={{ marginBottom: 10 }}>Incident Details</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {[
                    { label: 'Incident ID', value: selected.id },
                    { label: 'Type', value: selected.incident_type },
                    { label: 'Confidence', value: `${((selected.confidence_score ?? 0) * 100).toFixed(1)}%` },
                    { label: 'Service', value: selected.affected_service || 'System-wide' },
                    { label: 'Start Time', value: selected.start_time ? new Date(selected.start_time).toLocaleString() : '—' },
                  ].map(({ label, value }) => (
                    <div key={label} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '8px 12px',
                      background: 'rgba(255,255,255,0.04)', borderRadius: 10,
                    }}>
                      <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{label}</span>
                      <span style={{ fontSize: label === 'Incident ID' ? 11 : 12, fontWeight: 600, color: 'rgba(255,255,255,0.85)', fontFamily: label === 'Incident ID' ? 'monospace' : 'inherit' }}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample logs */}
              {selected.log_sample?.length > 0 && (
                <div>
                  <div className="section-label" style={{ marginBottom: 10 }}>Attached Log IDs</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {selected.log_sample.slice(0, 5).map((logId: string) => (
                      <div key={logId} style={{ fontFamily: 'monospace', fontSize: 11, color: 'rgba(10,132,255,0.8)', background: 'rgba(10,132,255,0.07)', borderRadius: 8, padding: '6px 10px' }}>
                        {logId}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            {selected.status !== 'RESOLVED' && (
              <div style={{ padding: '16px 24px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', gap: 10 }}>
                <button className="btn-success" onClick={() => resolveMutation.mutate(selected.id)} style={{ flex: 1, justifyContent: 'center' }}>
                  <CheckCircle size={14} /> Mark Resolved
                </button>
                <button className="btn-danger" onClick={() => escalateMutation.mutate(selected.id)} style={{ flex: 1, justifyContent: 'center' }}>Escalate</button>
              </div>
            )}
          </div>
        </>
      )}

      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default Incidents;
