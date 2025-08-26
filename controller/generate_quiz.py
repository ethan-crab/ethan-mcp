import sys
from model.models import QuizParam
from .get_link_data import process_metadata
import traceback
def generate_quiz(param: QuizParam):
    data = process_metadata(param.url, "en")
    prompt = f"""
    Generate a quiz based on the following:

    Title: {data["title"]}
    Description: {data["description"]}
    Transcript {data["transcript"]}

    Requirements:
    - {param.amt_quest} questions
    - Difficulty: {param.difficulty}
    - Quiz type: {param.test_type}
    - Provide correct answer
    - Return JSON
    """

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
