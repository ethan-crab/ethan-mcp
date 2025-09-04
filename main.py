from controller.generate_quiz import process_metadata
import uvicorn
from model.models import QuizParamNew
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import os
import json
import re
from typing import Any, Dict
from typing import Optional

# Load env for local/dev
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Optional Gemini setup
_GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai  # type: ignore
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _GEMINI_AVAILABLE = True
except Exception:
    _GEMINI_AVAILABLE = False

# Attach MCP
mcp = FastMCP(name="Quiz Gen")

# Create tool
@mcp.tool(name="generate_quiz_mcp")
async def processdata(title: str, description: str, transcript: Optional[str] = None, amt_quest: int = 5, difficulty: str = "easy", test_type: str = "multiple choice"):
        """Generate a quiz using Gemini if available; otherwise return instructions payload."""

        instruction = (
            "You are a quiz generator. "
            f"Use the given title, description, and transcript to generate a quiz. "
            f"Create exactly {amt_quest} questions. "
            f"Difficulty = {difficulty}. "
            f"Type = {test_type}. "
            "For each question, include an 'explanation' array with four strings, each explaining why the corresponding option is correct or incorrect. The 'explanation' array must be index-aligned with 'options'. "
            "Return the output strictly as a JSON object with the following format:\n\n"
            "{\n"
            '  "questions": [\n'
            "    {\n"
            '      "question": string,\n'
            '      "options": [string, string, string, string],\n'
            '      "explanation": [string, string, string, string],\n'
            '      "answer": string\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Do not include any extra text outside of the JSON."
        )

        if not _GEMINI_AVAILABLE:
            return {
                "title": title,
                "description": description,
                "transcript": transcript,
                "amt_quest": amt_quest,
                "difficulty": difficulty,
                "test_type": test_type,
                "instruction": instruction,
                "note": "Gemini SDK not available or GEMINI_API_KEY not set; returning instructions payload.",
            }

        # Build prompt for Gemini
        prompt = (
            f"Title: {title}\n\n"
            f"Description: {description}\n\n"
            f"Transcript: {transcript or 'N/A'}\n\n"
            f"{instruction}"
        )

        def _extract_json(text: str) -> Dict[str, Any]:
            try:
                return json.loads(text)
            except Exception:
                pass
            # Try to extract JSON code block
            match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if match:
                candidate = match.group(1).strip()
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            # Fallback: first brace to last brace
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except Exception:
                    pass
            raise ValueError("Failed to parse JSON from model output")

        # Call Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        output_text = getattr(response, "text", None) or (response.candidates[0].content.parts[0].text if getattr(response, "candidates", None) else "")
        quiz_json: Dict[str, Any]
        try:
            quiz_json = _extract_json(output_text)
        except Exception:
            # Return raw text when parsing fails
            return {
                "title": title,
                "description": description,
                "transcript": transcript,
                "amt_quest": amt_quest,
                "difficulty": difficulty,
                "test_type": test_type,
                "raw_output": output_text,
                "error": "Could not parse JSON from Gemini output",
            }

        return {
            "title": title,
            "description": description,
            "transcript": transcript,
            "amt_quest": amt_quest,
            "difficulty": difficulty,
            "test_type": test_type,
            "quiz": quiz_json,
            "prompt": instruction,
            "model": "gemini-1.5-flash",
        }

# main.py
def main():
    print("Generate Quiz Starting...")
    
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