export interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  service_name: string;
  level: string;
  message: string;
  metadata_json: any;
  host: string;
  environment: string;
}

export interface Incident {
  id: string;
  title: string;
  incident_type: string;
  status: string;
  severity: string;
  confidence_score: number | null;
  affected_service: string | null;
  start_time: string | null;
  log_sample: string[] | null;
  ai_analysis: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface Alert {
  id: string;
  incident_id: string;
  log_id: string | null;
  rule_triggered: string;
  created_at: string;
}

export interface WebhookHistory {
  id: string;
  alert_id: string;
  target_type: string;
  endpoint_url: string | null;
  payload_json: any;
  status: string;
  attempt_count: number;
  last_attempt_at: string | null;
  response_code: number | null;
  response_body: string | null;
  created_at: string;
}

export interface LogStats {
  by_level: Record<string, number>;
  by_service: Record<string, number>;
  error_rate: number;
}

export interface WebhookStats {
  success_rate: number;
  failure_count: number;
  avg_retry_count: number;
}
