from controller.generate_quiz import process_metadata
from router import init_routes
import uvicorn
from model.models import QuizParamNew
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import os

# Attach MCP
mcp = FastMCP(name="Quiz Gen")

# Create tool
@mcp.tool(name="generate_quiz_mcp")
async def processdata(param: QuizParamNew):
        """ Process provided title, description, and transcript and generate a quiz based on it"""
        #data = await process_metadata(param.url, "en")
        # Return structured metadata + quiz parameters for Claude to process
        return {
            "title": param.title,
            "description": param.description,
            "transcript": param.transcript,
            "amt_quest": param.amt_quest,
            "difficulty": param.difficulty,
            "test_type": param.test_type,
            "instruction": (
                "You are a quiz generator. "
                "Use the given title, description, and transcript to generate a quiz. "
                f"Create exactly {param.amt_quest} questions. "
                f"Difficulty = {param.difficulty}. "
                f"Type = {param.test_type}. "
                "Return the output strictly as a JSON object with the following format:\n\n"
                "{\n"
                '  "questions": [\n'
                "    {\n"
                '      "question": string,\n'
                '      "options": [string, string, string, string],\n'
                '      "answer": string\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Do not include any explanation, notes, or extra text outside of the JSON."
            )
        }

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