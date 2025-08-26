from controller.get_link_data import get_yt_link
from controller.generate_quiz import process_metadata
from router import init_routes
import uvicorn
from model.models import QuizParam
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Quiz Generator")

# Your normal FastAPI routes
init_routes(app)

# Attach MCP
mcp = FastMCP("Quiz Gen")

# Create tool
@mcp.tool(name="generate_quiz_mcp")
async def placehold(param: QuizParam):
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
# Mount MCP
#mcp.mount_sse(mount_path="/mcp")

# main.py
def main():
    print("Say Hello MCP Server starting...")
    
    # Setup Starlette app with CORS for cross-origin requests
    app = mcp.streamable_http_app()
    
    # IMPORTANT: add CORS middleware for browser based clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
        max_age=86400,
    )

    # Get port from environment variable (Smithery sets this to 8081)
    port = int(os.environ.get("PORT", 8080))
    print(f"Listening on port {port}")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")

if __name__ == "__main__":
    main()