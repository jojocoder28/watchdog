import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Upload, Sparkles, Filter, ChevronLeft, ChevronRight, X, Upload as UploadIcon } from 'lucide-react';
import api from '../api/client';
import { SEVERITY_COLORS } from '../utils/chartTheme';

const LEVEL_LABELS: Record<string, string> = {
  ERROR: 'ERROR', CRITICAL: 'CRITICAL', WARN: 'WARN', INFO: 'INFO', DEBUG: 'DEBUG', FATAL: 'FATAL',
};

const LevelBadge = ({ level }: { level: string }) => {
  const map: Record<string, string> = {
    ERROR: 'badge-high', CRITICAL: 'badge-critical', FATAL: 'badge-critical',
    WARN: 'badge-high', INFO: 'badge-info', DEBUG: 'badge-low',
  };
  return <span className={`badge ${map[level] || 'badge-info'}`}>{level}</span>;
};

const Logs: React.FC = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [service, setService] = useState('');
  const [level, setLevel] = useState('');
  const [page, setPage] = useState(0);
  const [showUpload, setShowUpload] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);
  const limit = 20;

  const params = new URLSearchParams();
  if (service) params.append('service', service);
  if (level) params.append('level', level);
  params.append('skip', String(page * limit));
  params.append('limit', String(limit));

  const { data: logs, isLoading } = useQuery({
    queryKey: ['logs', service, level, page],
    queryFn: () => api.get(`/logs/?${params}`).then(r => r.data),
  });

  const { data: stats } = useQuery({
    queryKey: ['logStats'],
    queryFn: () => api.get('/logs/stats').then(r => r.data),
  });

  const generateMutation = useMutation({
    mutationFn: (count: number) => api.post(`/logs/generate?count=${count}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['logs'] }),
  });

  const handleFile = async (file: File) => {
    if (!file) return;
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['log', 'csv', 'json'].includes(ext ?? '')) {
      alert('Only .log, .csv, .json files are supported.');
      return;
    }
    setUploading(true);
    setUploadProgress(0);
    const form = new FormData();
    form.append('file', file);
    try {
      await api.post('/logs/upload', form, {
        onUploadProgress: e => setUploadProgress(Math.round((e.loaded / (e.total ?? 1)) * 100)),
      });
      queryClient.invalidateQueries({ queryKey: ['logs'] });
      setShowUpload(false);
    } catch {}
    setUploading(false);
    setUploadProgress(0);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const filteredLogs = (logs ?? []).filter((l: any) =>
    !search || l.message?.toLowerCase().includes(search.toLowerCase()) || l.service_name?.toLowerCase().includes(search.toLowerCase())
  );

  const services = ['AuthService', 'PaymentService', 'DatabaseService', 'APIGateway', 'NotificationService'];

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>

      {/* Header */}
      <div className="animate-in" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'white', marginBottom: 4 }}>
            Log <span className="gradient-text">Explorer</span>
          </h1>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>
            {stats?.total_logs?.toLocaleString() ?? '—'} total entries ingested
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn-ghost" onClick={() => setShowUpload(s => !s)}>
            <Upload size={14} /> Upload
          </button>
          <button
            className="btn-primary"
            onClick={() => generateMutation.mutate(1000)}
            disabled={generateMutation.isPending}
          >
            <Sparkles size={14} />
            {generateMutation.isPending ? 'Generating…' : 'Generate 1K Logs'}
          </button>
        </div>
      </div>

      {/* Upload zone */}
      {showUpload && (
        <div className="glass-card animate-in" style={{ padding: 24, marginBottom: 20, borderRadius: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontWeight: 600, color: 'white' }}>Upload Log File</span>
            <button onClick={() => setShowUpload(false)} className="btn-ghost" style={{ padding: '4px 8px' }}><X size={14} /></button>
          </div>
          <div
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            style={{
              border: `2px dashed ${dragOver ? '#0A84FF' : 'rgba(10,132,255,0.35)'}`,
              borderRadius: 20,
              background: dragOver ? 'rgba(10,132,255,0.1)' : 'rgba(10,132,255,0.04)',
              padding: '48px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              transform: dragOver ? 'scale(1.01)' : 'scale(1)',
            }}
          >
            <UploadIcon size={40} color={dragOver ? '#0A84FF' : 'rgba(255,255,255,0.2)'} style={{ marginBottom: 12, display: 'block', margin: '0 auto 12px' }} />
            <div style={{ fontWeight: 600, color: 'rgba(255,255,255,0.8)', marginBottom: 6 }}>Drop file or click to browse</div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>Supports .log, .csv, .json</div>
          </div>
          <input ref={fileRef} type="file" accept=".log,.csv,.json" style={{ display: 'none' }} onChange={e => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }} />
          {uploading && (
            <div style={{ marginTop: 16 }}>
              <div style={{ background: 'rgba(255,255,255,0.08)', borderRadius: 99, overflow: 'hidden', height: 6 }}>
                <div style={{ height: '100%', width: `${uploadProgress}%`, background: 'linear-gradient(90deg,#0A84FF,#5AC8FA)', borderRadius: 99, transition: 'width 0.3s ease', position: 'relative' }}>
                  <div className="shimmer-skeleton" style={{ position: 'absolute', inset: 0, borderRadius: 99 }} />
                </div>
              </div>
              <div style={{ textAlign: 'center', fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 8 }}>{uploadProgress}% uploaded</div>
            </div>
          )}
        </div>
      )}

      {/* Toolbar */}
      <div className="glass-card animate-in" style={{ padding: 14, borderRadius: 20, marginBottom: 20, animationDelay: '0.08s' }}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search */}
          <div style={{ flex: 1, minWidth: 200, position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.3)' }} />
            <input
              className="glass-input"
              placeholder="Search messages, services…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ paddingLeft: 38, borderRadius: 12 }}
            />
          </div>
          {/* Service filter */}
          <div style={{ position: 'relative' }}>
            <Filter size={12} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.3)', pointerEvents: 'none' }} />
            <select className="glass-select" value={service} onChange={e => { setService(e.target.value); setPage(0); }} style={{ paddingLeft: 32 }}>
              <option value="">All Services</option>
              {services.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          {/* Level filter */}
          <select className="glass-select" value={level} onChange={e => { setLevel(e.target.value); setPage(0); }}>
            <option value="">All Levels</option>
            {Object.keys(LEVEL_LABELS).map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card animate-in" style={{ borderRadius: 20, overflow: 'hidden', padding: 0, animationDelay: '0.16s' }}>
        {/* Header row */}
        <div style={{
          display: 'grid', gridTemplateColumns: '150px 140px 80px 1fr 80px',
          padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.07)',
        }}>
          {['Timestamp', 'Service', 'Level', 'Message', 'Latency'].map(h => (
            <div key={h} className="section-label">{h}</div>
          ))}
        </div>

        {/* Rows */}
        {isLoading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} style={{ height: 44, margin: '4px 8px', borderRadius: 10 }} className="shimmer-skeleton" />
          ))
        ) : filteredLogs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>No logs found</div>
        ) : (
          filteredLogs.map((log: any) => {
            const color = SEVERITY_COLORS[log.level] || '#888';
            return (
              <div key={log.id}
                style={{
                  display: 'grid', gridTemplateColumns: '150px 140px 80px 1fr 80px',
                  padding: '10px 16px', cursor: 'pointer',
                  borderLeft: `3px solid ${color}`,
                  background: `${color}08`,
                  borderBottom: '1px solid rgba(255,255,255,0.04)',
                  transition: 'background 0.15s ease',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = `${color}15`)}
                onMouseLeave={e => (e.currentTarget.style.background = `${color}08`)}
              >
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', fontFamily: 'monospace' }}>
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', fontWeight: 500 }}>{log.service_name}</span>
                <LevelBadge level={log.level} />
                <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.message}</span>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', fontFamily: 'monospace' }}>
                  {log.metadata_json?.latency_ms ? `${log.metadata_json.latency_ms}ms` : '—'}
                </span>
              </div>
            );
          })
        )}

        {/* Pagination */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.07)' }}>
          <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>
            Page {page + 1} · {filteredLogs.length} entries
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn-ghost" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} style={{ padding: '6px 12px', opacity: page === 0 ? 0.4 : 1 }}>
              <ChevronLeft size={14} />
            </button>
            <button className="btn-primary" style={{ padding: '6px 16px' }}>{page + 1}</button>
            <button className="btn-ghost" onClick={() => setPage(p => p + 1)} disabled={filteredLogs.length < limit} style={{ padding: '6px 12px', opacity: filteredLogs.length < limit ? 0.4 : 1 }}>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Logs;
