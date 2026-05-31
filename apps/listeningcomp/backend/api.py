from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import asyncio
try:
    # If running as a package (imported as apps.listening-comp.backend.api)
    from .audio_generator import AudioGenerator
except Exception:
    # If running as a top-level module (using --app-dir or PYTHONPATH), fall back
    from audio_generator import AudioGenerator
try:
    from .question_generator import QuestionGenerator
except Exception:
    from question_generator import QuestionGenerator

app = FastAPI(title="Listening Comp API")

# Create generator instance
gen = AudioGenerator()
# Question generator instance
qgen = QuestionGenerator()

# Mount audio directory to serve generated files
audio_dir = gen.audio_dir
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

@app.post("/generate_audio")
async def generate_audio(request: Request):
    try:
        question = await request.json()
        # run blocking generation in a thread so any asyncio.run inside works
        output = await asyncio.to_thread(gen.generate_audio, question)
        # Return URL path relative to this server
        filename = Path(output).name
        return JSONResponse({"success": True, "url": f"/audio/{filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_question")
async def generate_question(request: Request):
    try:
        payload = await request.json()
        section_num = int(payload.get("section_num", 2))
        topic = payload.get("topic", "general")
        question = await asyncio.to_thread(qgen.generate_similar_question, section_num, topic)
        if not question:
            return JSONResponse({"success": False, "error": "Question generation failed"}, status_code=500)
        return JSONResponse({"success": True, "question": question})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_feedback")
async def get_feedback(request: Request):
    try:
        payload = await request.json()
        question = payload.get("question")
        selected_answer = int(payload.get("selected_answer"))
        feedback = await asyncio.to_thread(qgen.get_feedback, question, selected_answer)
        if not feedback:
            return JSONResponse({"success": False, "error": "Feedback generation failed"}, status_code=500)
        return JSONResponse({"success": True, "feedback": feedback})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def index():
    # Simple test UI served by API
    html_path = Path(__file__).resolve().parents[2] / "frontend" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<html><body><h3>No frontend found</h3></body></html>")
