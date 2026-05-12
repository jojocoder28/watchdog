export const CHART_COLORS = ['#0A84FF', '#BF5AF2', '#FF375F', '#30D158', '#FF9F0A', '#5AC8FA', '#FFD60A'];

export const CHART_DEFAULTS = {
  animationDuration: 800,
  animationEasing: 'ease-out' as const,
};

export const GRID_STYLE = {
  stroke: 'rgba(255,255,255,0.06)',
  strokeDasharray: '4 4',
};

export const AXIS_STYLE = {
  fill: 'rgba(255,255,255,0.35)',
  fontSize: 11,
  fontFamily: 'Inter, sans-serif',
};

export const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(13, 13, 26, 0.9)',
  border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: '12px',
  backdropFilter: 'blur(20px)',
  color: 'rgba(255,255,255,0.95)',
  fontSize: 12,
  fontFamily: 'Inter, sans-serif',
  padding: '8px 12px',
  boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
};

export const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#FF375F',
  HIGH: '#FF9F0A',
  MEDIUM: '#FFD60A',
  LOW: '#30D158',
  INFO: '#0A84FF',
  WARN: '#FF9F0A',
  ERROR: '#FF375F',
  DEBUG: '#5AC8FA',
  FATAL: '#FF375F',
};

export const STATUS_COLORS: Record<string, string> = {
  OPEN: '#FF375F',
  INVESTIGATING: '#FF9F0A',
  RESOLVED: '#30D158',
  SENT: '#30D158',
  FAILED: '#FF375F',
  PENDING: '#FFD60A',
  RETRYING: '#FF9F0A',
};
