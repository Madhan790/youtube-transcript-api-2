from flask import Flask, request, jsonify, Response
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os, json

API_KEY = "x9J2f8S2pA9W-qZvB"

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "YouTube Transcript API Active 🚀", "auth": "required"}

@app.route("/transcript")
def get_transcript():
    # -------- API KEY CHECK -------- #
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    video_id = request.args.get("id") or request.args.get("v")

    if not video_id:
        return jsonify({"success": False, "error": "Use /transcript?id=VIDEO_ID"}), 400

    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)

        # ---- Choose best transcript ---- #
        t = None
        # Manual first
        for tc in transcripts:
            if not tc.is_generated:
                t = tc; break
        # Auto CC next
        if t is None:
            for tc in transcripts:
                if tc.is_generated:
                    t = tc; break
        # Fallback
        if t is None:
            t = list(transcripts)[0]

        data = t.fetch()

        subtitles = [{"text": x.text, "start": x.start, "duration": x.duration} for x in data]

        response_json = {
            "success": True,
            "mode": "YTA",                        # <--- identifier of source
            "count": len(subtitles),
            "lang": t.language_code,
            "format": "manual" if not t.is_generated else "auto",
            "subtitles": subtitles
        }

        return Response(json.dumps(response_json, ensure_ascii=False, indent=2),
                        mimetype="application/json")

    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({"success": False, "error": "Transcript not available"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port)
