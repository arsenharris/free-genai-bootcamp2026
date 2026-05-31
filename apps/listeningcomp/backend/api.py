from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import asyncio
try:
    # If running as a package, e.g. uvicorn backend.api:app
    from .audio_generator import AudioGenerator
except ImportError:
    if __package__:
        raise
    # If running as a top-level module (using --app-dir or PYTHONPATH), fall back
    from audio_generator import AudioGenerator
try:
    from .question_generator import QuestionGenerator
except ImportError:
    if __package__:
        raise
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
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse(
        """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Listening Comp</title>
            <style>
                body { font-family: system-ui, sans-serif; max-width: 720px; margin: 48px auto; padding: 0 20px; line-height: 1.5; }
                button, input, select { font: inherit; padding: 8px 10px; }
                label { display: block; margin-top: 14px; font-weight: 600; }
                pre { white-space: pre-wrap; background: #f5f5f5; padding: 14px; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>Listening Comp API</h1>
            <p>The backend is running. Generate a question to test the local API.</p>
            <label>
                Section
                <select id="section">
                    <option value="2">2</option>
                    <option value="3">3</option>
                </select>
            </label>
            <label>
                Topic
                <input id="topic" value="restaurant">
            </label>
            <p><button id="generate">Generate question</button></p>
            <pre id="output">Ready.</pre>
            <script>
                const output = document.querySelector("#output");
                document.querySelector("#generate").addEventListener("click", async () => {
                    output.textContent = "Generating...";
                    try {
                        const response = await fetch("/generate_question", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                section_num: Number(document.querySelector("#section").value),
                                topic: document.querySelector("#topic").value
                            })
                        });
                        const data = await response.json();
                        output.textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        output.textContent = error.message;
                    }
                });
            </script>
        </body>
        </html>
        """
    )
