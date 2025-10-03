import httpx
from model.models import Videos
import os

async def sort_videos(course_name: str, goals: str, videos: list[dict | list | tuple]):
    """Accepts payload  (course_name, goals, videos[] with transcription) and forwards it.
    - Tuples/lists are interpreted as (title, description, transcription).
    """
    api_url = os.getenv("SMART_SORT_API")

    videos_payload: list[dict] = []
    for item in videos:
        if isinstance(item, dict):
            title = item.get("title")
            description = item.get("description")
            transcription = item.get("transcription")
            videos_payload.append({
                "title": title,
                "description": description,
                "transcription": transcription,
            })
        elif isinstance(item, (list, tuple)):
            if len(item) != 3:
                raise ValueError("Tuple/list videos must have exactly 3 elements: (title, description, transcription)")
            title, description, transcription = item
            videos_payload.append({
                "title": title,
                "description": description,
                "transcription": transcription,
            })
        elif isinstance(item, Videos):
            videos_payload.append({
                "title": item.title,
                "description": item.description,
                "transcription": getattr(item, "transcript", None),
            })
        else:
            raise TypeError(f"Unsupported video item type: {type(item).__name__}")

    # Prepare request payload exactly like the curl example
    payload = {
        "course_name": course_name,
        "goals": goals,
        "videos": videos_payload,
    }

    # Call FastAPI API with error handling
    url = api_url
    try:
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(url, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                return {
                    "error": "http_status_error",
                    "status_code": e.response.status_code,
                    "response_text": e.response.text,
                    "url": url,
                    "payload_preview": {"course_name": course_name, "goals": goals, "videos_count": len(videos_payload)},
                }
    except httpx.RequestError as e:
        return {
            "error": "request_error",
            "message": str(e),
            "url": url,
        }

    # Return JSON response from API (fallback to text if not JSON)
    try:
        return response.json()
    except Exception:
        return {
            "error": "invalid_json_response",
            "status_code": response.status_code,
            "response_text": response.text,
        }
