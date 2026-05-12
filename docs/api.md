# API Documentation

The Watchdog API is built with FastAPI and follows RESTful principles.

## Base URL
- Local: `http://localhost:8000`
- Production (Proxy): `/api`

## Authentication
Most endpoints require a JWT Bearer token in the `Authorization` header.
`Authorization: Bearer <token>`

---

## Auth Routes

### POST `/auth/register`
Register a new operative.
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "email": "sre@watchdog.ai",
    "password": "password123",
    "role": "SRE"
  }
  ```
- **Response**: `200 OK` (User object)

### POST `/auth/login`
Authenticate and receive a JWT.
- **Auth Required**: No
- **Request Body**: `multipart/form-data` (username/password)
- **Response**:
  ```json
  {
    "access_token": "...",
    "token_type": "bearer"
  }
  ```

---

## Log Routes

### GET `/logs/`
List logs with pagination and filters.
- **Auth Required**: Yes
- **Query Params**: `service`, `level`, `skip`, `limit`
- **Response**: `Array<LogEntry>`

### POST `/logs/upload`
Upload log files (.log, .csv, .json).
- **Auth Required**: Yes
- **Request Body**: `multipart/form-data` (file)
- **Response**: `{"message": "File processing..."}`

### GET `/logs/stats`
Get log distribution and error rates.
- **Auth Required**: Yes
- **Response**:
  ```json
  {
    "total_logs": 5000,
    "error_rate": 2.5,
    "counts_by_level": { "ERROR": 120, "INFO": 4880 },
    "counts_by_service": { "AuthService": 1000 }
  }
  ```

---

## Anomaly & Incident Routes

### POST `/anomaly/detect`
Manually trigger the anomaly detection engine.
- **Auth Required**: Yes
- **Response**: `Array<IncidentResponse>`

### GET `/anomaly/incidents`
List all detected incidents.
- **Auth Required**: Yes
- **Response**: `Array<IncidentResponse>`

### PATCH `/anomaly/incidents/{id}`
Update incident status (e.g., Mark as Resolved).
- **Auth Required**: Yes
- **Request Body**: `{"status": "RESOLVED"}`
- **Response**: `IncidentResponse`

---

## Webhook Routes

### GET `/webhook/stats`
Get delivery success rates and history.
- **Auth Required**: Yes
- **Response**:
  ```json
  {
    "success_rate": 98.2,
    "failure_count": 5,
    "avg_retry_count": 1.2
  }
  ```

---

## Error Codes

| Code | Description |
| :--- | :--- |
| `401` | Unauthorized (Missing or invalid token) |
| `403` | Forbidden (Insufficient permissions) |
| `404` | Not Found |
| `422` | Validation Error (Check request body) |
| `500` | Internal Server Error |
