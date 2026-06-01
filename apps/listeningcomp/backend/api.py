from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import asyncio
import json
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

workspace_root = Path(__file__).resolve().parents[3]
visual_novel_public_dir = workspace_root / "apps" / "visual-novel" / "public"
visual_novel_scenes_dir = visual_novel_public_dir / "data" / "scenes"
visual_novel_mappings_path = visual_novel_public_dir / "data" / "mappings.json"
visual_novel_story_dir = workspace_root / "apps" / "visual-novel" / "story"

if visual_novel_public_dir.exists():
    app.mount(
        "/visual-novel-assets",
        StaticFiles(directory=visual_novel_public_dir),
        name="visual-novel-assets",
    )

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


@app.get("/api/visual-novel/scenes/{scene_id}")
async def get_visual_novel_scene(scene_id: str):
    scene_path = visual_novel_scenes_dir / f"{scene_id}.json"
    if not scene_path.exists():
        raise HTTPException(status_code=404, detail=f"Scene '{scene_id}' not found")

    try:
        scene = json.loads(scene_path.read_text(encoding="utf-8"))
        story_path = visual_novel_story_dir / f"{scene_id}.json"
        if story_path.exists():
            story_scene = json.loads(story_path.read_text(encoding="utf-8"))
            if "languageLearning" in story_scene:
                scene["languageLearning"] = story_scene["languageLearning"]
            if "nextScene" in story_scene:
                scene["nextScene"] = story_scene["nextScene"]

        return JSONResponse({
            "success": True,
            "scene": scene,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visual-novel/mappings")
async def get_visual_novel_mappings():
    if not visual_novel_mappings_path.exists():
        return JSONResponse({"success": True, "mappings": {"characterNames": {}}})

    try:
        return JSONResponse({
            "success": True,
            "mappings": json.loads(visual_novel_mappings_path.read_text(encoding="utf-8")),
        })
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
                body { font-family: system-ui, sans-serif; max-width: 780px; margin: 42px auto; padding: 0 20px; line-height: 1.5; color: #202124; }
                h1 { margin-bottom: 8px; }
                .controls { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 24px 0 18px; }
                button, select { font: inherit; padding: 10px 12px; border: 1px solid #b8bcc2; border-radius: 6px; background: white; }
                button { cursor: pointer; background: #1f6feb; color: white; border-color: #1f6feb; }
                label { display: grid; gap: 6px; font-weight: 650; }
                .hint { color: #5f6368; font-size: 0.94rem; margin: 0; }
                .question { margin-top: 22px; padding-top: 18px; border-top: 1px solid #dfe3e8; }
                .options { display: grid; gap: 8px; margin-top: 12px; }
                .options button { text-align: left; background: #fff; color: #202124; border-color: #c8ccd2; }
                pre { white-space: pre-wrap; background: #f5f7f9; padding: 14px; border-radius: 8px; overflow-wrap: anywhere; }
                @media (max-width: 640px) { .controls { grid-template-columns: 1fr; } }
            </style>
        </head>
        <body>
            <h1>Listening Practice</h1>
            <p class="hint">Pick a topic and question style, then generate a Spanish listening question.</p>
            <div class="controls">
                <label>
                    Topic
                    <select id="topic">
                        <option value="restaurant">Restaurant</option>
                        <option value="cafe">Cafe</option>
                        <option value="airport">Airport</option>
                        <option value="hotel">Hotel</option>
                        <option value="shopping">Shopping</option>
                        <option value="travel">Travel</option>
                        <option value="school">School</option>
                        <option value="directions">Directions</option>
                    </select>
                </label>
                <label>
                    Question style
                    <select id="section">
                        <option value="2">Dialogue comprehension</option>
                        <option value="3">Situation question</option>
                    </select>
                </label>
            </div>
            <p class="hint">
                Dialogue comprehension uses an introduction plus conversation. Situation question is a shorter prompt.
            </p>
            <p><button id="generate">Generate question</button></p>
            <section id="question" class="question" hidden>
                <p id="intro"></p>
                <p id="conversation"></p>
                <h2 id="prompt"></h2>
                <div id="options" class="options"></div>
            </section>
            <pre id="output">Ready.</pre>
            <script>
                const output = document.querySelector("#output");
                const questionBlock = document.querySelector("#question");
                const intro = document.querySelector("#intro");
                const conversation = document.querySelector("#conversation");
                const prompt = document.querySelector("#prompt");
                const options = document.querySelector("#options");
                let currentQuestion = null;

                function renderQuestion(question) {
                    currentQuestion = question;
                    intro.textContent = question.Introduction || question.Situation || "";
                    conversation.textContent = question.Conversation || "";
                    prompt.textContent = question.Question || "";
                    options.innerHTML = "";
                    (question.Options || []).forEach((option, index) => {
                        const button = document.createElement("button");
                        button.type = "button";
                        button.textContent = `${index + 1}. ${option}`;
                        button.addEventListener("click", () => checkAnswer(index + 1));
                        options.appendChild(button);
                    });
                    questionBlock.hidden = false;
                    output.textContent = JSON.stringify(question, null, 2);
                }

                async function checkAnswer(selectedAnswer) {
                    if (!currentQuestion) return;
                    output.textContent = "Checking answer...";
                    try {
                        const response = await fetch("/get_feedback", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                question: currentQuestion,
                                selected_answer: selectedAnswer
                            })
                        });
                        const data = await response.json();
                        output.textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        output.textContent = error.message;
                    }
                }

                document.querySelector("#generate").addEventListener("click", async () => {
                    output.textContent = "Generating...";
                    questionBlock.hidden = true;
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
                        if (!data.success) {
                            output.textContent = data.error || "Question generation failed";
                            return;
                        }
                        renderQuestion(data.question);
                    } catch (error) {
                        output.textContent = error.message;
                    }
                });
            </script>
        </body>
        </html>
        """
    )
