import uvicorn
from app.main import app

print("Starting uvicorn server on http://127.0.0.1:8000...", flush=True)
uvicorn.run(app, host="127.0.0.1", port=8000)
