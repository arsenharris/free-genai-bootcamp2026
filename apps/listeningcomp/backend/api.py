from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
try:
    # If running as a package (imported as apps.listening-comp.backend.api)
    from .audio_generator import AudioGenerator
except Exception:
    # If running as a top-level module (using --app-dir or PYTHONPATH), fall back
    from audio_generator import AudioGenerator

app = FastAPI(title="Listening Comp API")

# Create generator instance
gen = AudioGenerator()

# Mount audio directory to serve generated files
audio_dir = gen.audio_dir
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

@app.post("/generate_audio")
async def generate_audio(request: Request):
    try:
        question = await request.json()
        output = gen.generate_audio(question)
        # Return URL path relative to this server
        filename = Path(output).name
        return JSONResponse({"success": True, "url": f"/audio/{filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def index():
    # Simple test UI served by API
    html_path = Path(__file__).resolve().parents[2] / "frontend" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<html><body><h3>No frontend found</h3></body></html>")
