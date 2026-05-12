# Setup Guide

Follow these steps to set up Watchdog on your local machine for development or production evaluation.

## 1. Environment Configuration

### Getting a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Create a new API Key.
3. Note: The platform uses `gemini-2.0-flash-exp` (or latest stable) for high-speed analysis.

### Configuring `.env`
Copy the example environment file to the root:
```bash
cp .env.example .env
```
Key variables:
- `GEMINI_API_KEY`: Your key from AI Studio.
- `DATABASE_URL`: `sqlite:///./dataset/dev.db` (for local) or `sqlite:///./data/watchdog.db` (for Docker).
- `ENVIRONMENT`: Set to `development` to enable wildcard CORS and detailed logging.

---

## 2. Local Setup (Standard)

### Windows
1. **Backend**:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
2. **Frontend**:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

### Mac / Linux
1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 3. Data Seeding
To populate the dashboard with realistic data immediately:
1. Ensure the backend is running.
2. Run the synthetic generator via the API:
   - Go to `http://localhost:8000/docs`
   - Use `POST /logs/generate?count=5000`
3. Or use the provided `Makefile`:
   ```bash
   make seed
   ```

---

## 4. Running Tests
The project uses `pytest` for backend verification.
```bash
cd backend
pytest
```
To run with coverage:
```bash
pytest --cov=.
```

---

## 5. Common Issues & Fixes

**Issue: `ImportError: email-validator is not installed`**
- **Fix**: Run `pip install "pydantic[email]"`.

**Issue: `sqlite3.OperationalError: no such column`**
- **Fix**: The schema is out of sync. Delete `dataset/dev.db` and restart the backend; SQLAlchemy will recreate the tables correctly.

**Issue: `CORS blocked`**
- **Fix**: Ensure `ENVIRONMENT=development` in your `.env` file or ensure the origin `http://localhost:5173` is explicitly allowed in `main.py`.
