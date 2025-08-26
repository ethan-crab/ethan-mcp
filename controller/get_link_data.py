from yt_dlp import YoutubeDL
import requests

def get_yt_link(link: str):
    try:
        metadata = process_metadata(link, "en")
        return metadata
    except Exception as e:
        print(f"Error fetching data {e}")
        return "error"
    

async def process_metadata(link: str, lang: str = "en") -> dict:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,   # fallback to auto-generated subs
        "subtitleslangs": [lang],
        }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    title = info.get("title")
    description = info.get("description")

    # Try official subtitles first, then auto-generated
    subs = info.get("subtitles") or info.get("automatic_captions")
    transcript_text = None

    if subs and lang in subs:
        sub_url = subs[lang][0]["url"]
        ext = subs[lang][0]["ext"]

        # Download the subtitle file
        resp = requests.get(sub_url)
        if resp.ok:
            transcript_text = resp.text
        else:
            transcript_text = f"Failed to fetch subtitles (HTTP {resp.status_code})"
    else:
        transcript_text = "No transcript available."

    return {
        "title": title,
        "description": description,
        "transcript": transcript_text
    }