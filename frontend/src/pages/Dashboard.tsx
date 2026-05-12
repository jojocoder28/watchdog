import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { FileText, AlertTriangle, Bell, Server, Sparkles, TrendingUp, TrendingDown } from 'lucide-react';
import api from '../api/client';
import CountUp from '../components/CountUp';
import Typewriter from '../components/Typewriter';
import { CHART_COLORS, GRID_STYLE, AXIS_STYLE, TOOLTIP_STYLE, SEVERITY_COLORS } from '../utils/chartTheme';

// ---- Custom tooltip ----
const GlassTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ ...TOOLTIP_STYLE, minWidth: 120 }}>
      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)', marginBottom: 4 }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'white' }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};

// ---- Severity ring donut ----
const SeverityDonut = ({ data }: { data: Record<string, number> }) => {
  const entries = Object.entries(data).map(([name, value]) => ({ name, value }));
  const total = entries.reduce((s, e) => s + e.value, 0);
  return (
    <div style={{ position: 'relative', width: 180, height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={entries} dataKey="value" innerRadius={58} outerRadius={80} paddingAngle={3} startAngle={90} endAngle={-270} animationBegin={0} animationDuration={800}>
            {entries.map((e, i) => (
              <Cell key={i} fill={SEVERITY_COLORS[e.name] || CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={TOOLTIP_STYLE} />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: 28, fontWeight: 800, color: 'white' }}>{total}</span>
        <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.06em' }}>TOTAL</span>
      </div>
    </div>
  );
};

// ---- Service health ring ----
const HealthRing = ({ score, color }: { score: number; color: string }) => {
  const r = 28, cx = 36, cy = 36;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (score / 100) * circumference;
  return (
    <svg width={72} height={72} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={5} />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={5}
        strokeDasharray={circumference} strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)' }}
      />
    </svg>
  );
};

// ---- KPI Card ----
const KPICard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: number;
  gradient: string;
  glowColor: string;
  trend?: number;
  suffix?: string;
  decimals?: number;
  delay?: number;
}> = ({ icon, label, value, gradient, glowColor, trend, suffix = '', decimals = 0, delay = 0 }) => {
  const isUp = (trend ?? 0) >= 0;
  return (
    <div className="glass-card animate-in" style={{
      padding: 24, cursor: 'default', animationDelay: `${delay}s`,
      boxShadow: `0 8px 32px rgba(0,0,0,0.4), 0 0 40px ${glowColor}22, inset 0 1px 0 rgba(255,255,255,0.15)`,
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{
          width: 42, height: 42, borderRadius: 14,
          background: gradient, display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: `0 4px 16px ${glowColor}55`,
        }}>
          {icon}
        </div>
        {trend !== undefined && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: 11, fontWeight: 600, color: isUp ? '#30D158' : '#FF375F' }}>
            {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div style={{ fontSize: 40, fontWeight: 800, letterSpacing: -2, color: 'white', lineHeight: 1 }}>
        <CountUp end={value} decimals={decimals} suffix={suffix} />
      </div>
      <div className="section-label" style={{ marginTop: 6 }}>{label}</div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const { data: stats } = useQuery({ queryKey: ['logStats'], queryFn: () => api.get('/logs/stats').then(r => r.data) });
  const { data: incidents } = useQuery({ queryKey: ['incidents'], queryFn: () => api.get('/anomaly/incidents').then(r => r.data) });
  const { data: webhookStats } = useQuery({ queryKey: ['webhookStats'], queryFn: () => api.get('/webhook/stats').then(r => r.data) });
  const { data: recentLogs } = useQuery({ queryKey: ['recentLogs'], queryFn: () => api.get('/logs/?limit=5').then(r => r.data) });

  const totalLogs = stats?.total_logs ?? 0;
  const openIncidents = incidents?.filter((i: any) => i.status === 'OPEN').length ?? 0;
  const criticalIncidents = incidents?.filter((i: any) => i.severity === 'CRITICAL').length ?? 0;
  const levelData = stats?.counts_by_level ? Object.entries(stats.counts_by_level).map(([name, value]) => ({ name, value })) : [];

  const serviceNames = ['AuthService', 'PaymentService', 'DatabaseService', 'APIGateway', 'NotificationService'];
  const serviceData = serviceNames.map(svc => {
    const total = stats?.counts_by_service?.[svc] ?? Math.floor(Math.random() * 1000 + 100);
    const errors = stats?.counts_by_level?.ERROR ?? 0;
    const score = Math.max(10, Math.min(99, 100 - Math.floor((errors / Math.max(total, 1)) * 100)));
    return { name: svc.replace('Service', ''), score, status: score > 70 ? 'Healthy' : score > 40 ? 'Degraded' : 'Critical' };
  });

  // Build mock trend data from stats
  const trendData = Array.from({ length: 12 }, (_, i) => ({
    time: `${String(i * 2).padStart(2, '0')}:00`,
    errors: Math.floor(Math.random() * 80 + 10),
    warnings: Math.floor(Math.random() * 120 + 20),
  }));

  const aiSummaries = (incidents ?? []).filter((i: any) => i.ai_analysis).slice(0, 3);

  const getStatusColor = (status: string) => status === 'Healthy' ? '#30D158' : status === 'Degraded' ? '#FF9F0A' : '#FF375F';

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>

      {/* Header */}
      <div className="animate-in" style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'white', marginBottom: 4 }}>
          System <span className="gradient-text">Overview</span>
        </h1>
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Real-time observability across all services</p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
        <KPICard icon={<FileText size={20} color="white" />} label="Total Logs Ingested" value={totalLogs} gradient="linear-gradient(135deg,#0A84FF,#5AC8FA)" glowColor="#0A84FF" trend={12} delay={0} />
        <KPICard icon={<AlertTriangle size={20} color="white" />} label="Open Incidents" value={openIncidents} gradient="linear-gradient(135deg,#FF375F,#FF9F0A)" glowColor="#FF375F" trend={-3} delay={0.08} />
        <KPICard icon={<Bell size={20} color="white" />} label="Active Alerts" value={criticalIncidents} gradient="linear-gradient(135deg,#FF9F0A,#FFD60A)" glowColor="#FF9F0A" trend={5} delay={0.16} />
        <KPICard icon={<Server size={20} color="white" />} label="Services Healthy" value={serviceData.filter(s => s.status === 'Healthy').length} gradient="linear-gradient(135deg,#30D158,#5AC8FA)" glowColor="#30D158" suffix={`/${serviceData.length}`} delay={0.24} />
      </div>

      {/* Row 2: Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        {/* Area Chart */}
        <div className="glass-card animate-in" style={{ padding: 24, animationDelay: '0.1s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <div className="section-label">Error Rate Trend</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'white', marginTop: 4 }}>Last 24 Hours</div>
            </div>
            <div style={{ background: 'rgba(10,132,255,0.15)', border: '1px solid rgba(10,132,255,0.3)', borderRadius: 99, padding: '4px 12px', fontSize: 11, color: '#0A84FF', fontWeight: 600 }}>
              LIVE
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trendData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="errorGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF375F" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#FF375F" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="warnGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF9F0A" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#FF9F0A" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid {...GRID_STYLE} vertical={false} />
              <XAxis dataKey="time" tick={AXIS_STYLE} axisLine={false} tickLine={false} />
              <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} />
              <Tooltip content={<GlassTooltip />} />
              <Area type="monotone" dataKey="errors" stroke="#FF375F" strokeWidth={2} fill="url(#errorGrad)" animationDuration={800} />
              <Area type="monotone" dataKey="warnings" stroke="#FF9F0A" strokeWidth={2} fill="url(#warnGrad)" animationDuration={800} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Donut */}
        <div className="glass-card animate-in" style={{ padding: 24, animationDelay: '0.18s', display: 'flex', flexDirection: 'column' }}>
          <div className="section-label" style={{ marginBottom: 8 }}>Log Severity Distribution</div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
            {levelData.length > 0 ? (
              <SeverityDonut data={stats?.counts_by_level ?? {}} />
            ) : (
              <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>No data yet</div>
            )}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 12px', justifyContent: 'center' }}>
              {levelData.map(({ name }) => (
                <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: SEVERITY_COLORS[name] || '#666' }} />
                  <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)' }}>{name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Service Health + Incident Timeline */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        {/* Service Health */}
        <div className="glass-card animate-in" style={{ padding: 24, animationDelay: '0.2s' }}>
          <div className="section-label" style={{ marginBottom: 16 }}>Service Health</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {serviceData.map(svc => {
              const color = getStatusColor(svc.status);
              return (
                <div key={svc.name} className="glass-card" style={{
                  padding: 16, borderRadius: 16, cursor: 'default',
                  boxShadow: `0 4px 16px rgba(0,0,0,0.3), 0 0 20px ${color}15`,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.8)' }}>{svc.name}</span>
                    <span className={`badge badge-${svc.status.toLowerCase()}`} style={{ fontSize: 9 }}>{svc.status}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ position: 'relative' }}>
                      <HealthRing score={svc.score} color={color} />
                      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>{svc.score}</span>
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)' }}>Uptime</div>
                      <div style={{ fontSize: 14, fontWeight: 700, color }}>
                        <CountUp end={svc.score * 0.99} decimals={1} suffix="%" />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Incident Timeline */}
        <div className="glass-card animate-in" style={{ padding: 24, animationDelay: '0.28s', overflow: 'hidden' }}>
          <div className="section-label" style={{ marginBottom: 16 }}>Recent Incidents</div>
          {(incidents ?? []).length === 0 && (
            <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13, textAlign: 'center', padding: '24px 0' }}>No incidents detected</div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 300, overflowY: 'auto' }}>
            {(incidents ?? []).slice(0, 6).map((inc: any, idx: number) => {
              const color = SEVERITY_COLORS[inc.severity] || '#888';
              return (
                <div key={inc.id} className="animate-in" style={{
                  display: 'flex', alignItems: 'flex-start', gap: 12, animationDelay: `${idx * 0.06}s`,
                }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 2 }}>
                    <div style={{
                      width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0,
                      boxShadow: `0 0 8px ${color}`,
                      animation: inc.status === 'OPEN' ? 'pulse-dot 2s infinite' : 'none',
                    }} />
                    {idx < 5 && <div style={{ width: 1, flex: 1, background: 'rgba(255,255,255,0.08)', minHeight: 20, marginTop: 3 }} />}
                  </div>
                  <div style={{
                    flex: 1, background: 'rgba(255,255,255,0.04)', borderRadius: 12,
                    padding: '10px 12px', border: '1px solid rgba(255,255,255,0.07)',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: 'rgba(255,255,255,0.9)' }}>{inc.incident_type}</span>
                      <span className={`badge badge-${inc.severity.toLowerCase()}`}>{inc.severity}</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                      {inc.affected_service || 'System'} · {new Date(inc.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Row 4: AI Summaries */}
      {aiSummaries.length > 0 && (
        <div className="animate-in" style={{ animationDelay: '0.32s' }}>
          <div className="section-label" style={{ marginBottom: 12 }}>AI Analysis — Recent Incidents</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
            {aiSummaries.map((inc: any, i: number) => (
              <div key={inc.id} className="glass-card animate-in" style={{
                padding: 20, borderRadius: 20, animationDelay: `${0.36 + i * 0.08}s`,
                boxShadow: '0 8px 32px rgba(0,0,0,0.4), 0 0 30px rgba(191,90,242,0.1)',
                borderColor: 'rgba(191,90,242,0.2)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: 10,
                    background: 'linear-gradient(135deg,#BF5AF2,#0A84FF)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 4px 12px rgba(191,90,242,0.4)',
                  }}>
                    <Sparkles size={16} color="white" />
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>Incident #{inc.id?.slice(0, 8)}</div>
                    <div className={`badge badge-${inc.severity?.toLowerCase()}`} style={{ marginTop: 2 }}>{inc.severity}</div>
                  </div>
                </div>
                <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)', lineHeight: 1.6, marginBottom: 12 }}>
                  {i === 0 ? <Typewriter text={inc.ai_analysis?.slice(0, 150) + '...'} /> : inc.ai_analysis?.slice(0, 150) + '...'}
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, color: 'rgba(191,90,242,0.6)', fontWeight: 600 }}>
                  <Sparkles size={10} />
                  Powered by Gemini 2.5 Flash
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
