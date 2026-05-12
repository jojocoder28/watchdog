# Interview Pitch: Watchdog

## Elevator Pitch
Watchdog is an "Intelligent Observability" platform designed for the modern SRE. While traditional tools like Grafana or Datadog provide great charts, Watchdog focuses on reducing "alert fatigue" by combining machine learning anomaly detection with Generative AI analysis. It doesn't just tell you that your error rate is up; it analyzes the log context, identifies the specific service failure pattern, and provides a Gemini-powered summary of the root cause—all within a high-fidelity, Apple-inspired interface that prioritizes clarity and speed during high-pressure incidents.

## 5 Key Technical Decisions

1. **Hybrid Anomaly Detection**: We chose to combine statistical Z-Score analysis for immediate threshold spikes with Scikit-Learn’s `Isolation Forest` for detecting "needle-in-a-haystack" structural anomalies that rules would miss.
2. **Asynchronous Ingestion**: Logs are processed in background tasks using FastAPI’s `BackgroundTasks`, ensuring that large file uploads (CSV/JSON) never block the UI or main API thread.
3. **Pydantic v2 & SQLAlchemy 2.0**: Leveraged the latest Python type-safety standards for robust data validation and an async-compatible ORM layer, ensuring a modern, maintainable codebase.
4. **Vite + Tailwind v4 + Framer Motion**: Chose this stack to achieve "Apple-grade" aesthetics (glassmorphism, 60fps animations) without sacrificing developer experience or build performance.
5. **Docker Multi-Stage Builds**: Used multi-stage builds to produce a production-ready Nginx image that serves the React frontend while proxying API requests, minimizing the final image size and attack surface.

## Challenges & Solutions
- **Challenge**: Mapping erratic synthetic logs to structured incidents.
- **Solution**: Implemented a "sliding window" deduplication logic in the `AnomalyEngine` to prevent multiple incident triggers for the same underlying event.
- **Challenge**: Pydantic validation errors for non-standard log levels.
- **Solution**: Standardized the `LogLevel` enum and implemented a fallback mapping in the ingestion layer to handle `CRITICAL` vs `FATAL` nomenclature differences.

## Production Roadmap
1. **Vector Search**: Move from keyword/regex log analysis to Vector Embeddings (using pgvector) to find semantically similar incidents from the past.
2. **Redis Integration**: Replace background tasks with a proper task queue (Celery/RQ) for high-volume distributed processing.
3. **Live WebSockets**: Implement Pusher or Socket.io for real-time dashboard updates without polling.
4. **Auth0/SSO**: Move from local JWT to enterprise SSO for secure organizational access.

## Extension Ideas
If I had more time, I would implement "Predictive Alerting"—using historical data to predict a failure 5-10 minutes before it happens based on rising memory pressure or latency trends, giving SREs the ultimate "proactive" tool.
