from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from controller.get_link_data import get_yt_link
from controller.generate_quiz import process_metadata
from router import init_routes
import uvicorn
from model.models import QuizParam
import traceback
import sys

app = FastAPI(title="Quiz Generator")

# Your normal FastAPI routes
#init_routes(app)

@app.post("/generatequiz", operation_id="makequiz")
async def generate_quiz_desktop(param: QuizParam):
    try:
        data = await process_metadata(param.url, "en")

        # Return structured metadata + quiz parameters for Claude to process
        return {
            "title": data["title"],
            "description": data["description"],
            "transcript": data["transcript"],
            "amt_quest": param.amt_quest,
            "difficulty": param.difficulty,
            "test_type": param.test_type,
            "instruction": (
                "Generate a quiz based on the given title, description, and transcript. "
                f"Make {param.amt_quest} questions, difficulty = {param.difficulty}, "
                f"type = {param.test_type}, return JSON with questions and correct answers."
            )
        }
    except Exception as e:
        traceback.print_exc(file=sys.stderr)  # logs full stacktrace
        raise

# Mount MCP
fmcp = FastApiMCP(app)
fmcp.mount(mount_path="/mcp")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)