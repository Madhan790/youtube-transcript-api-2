from flask import Flask, request, jsonify, Response
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os

app = Flask(__name__)


# ---------------- Home Root Endpoint ---------------- #
@app.route("/")
def home():
    print("[LOG] / endpoint hit", flush=True)
    return {"status": "YouTube Transcript API Active 🚀"}


# ---------------- Transcript Endpoint ---------------- #
@app.route("/transcript")
def get_transcript():
    print("[LOG] /transcript endpoint hit", flush=True)

    video_id = request.args.get("id") or request.args.get("v")
    print(f"[LOG] Request video_id = {video_id}", flush=True)

    if not video_id:
        print("[ERROR] Missing ID", flush=True)
        return jsonify({"error": "Use /transcript?id=VIDEOID"}), 400

    try:
        print("[STEP1] Creating API client", flush=True)
        api = YouTubeTranscriptApi()

        print("[STEP2] Fetching transcript list...", flush=True)
        transcripts = api.list(video_id)

        available_langs = [t.language_code for t in transcripts]
        print("[LOG] Available languages:", available_langs, flush=True)

        print("[STEP3] Selecting language...", flush=True)
        t = None

        # Try manual first
        for tc in transcripts:
            if not tc.is_generated:
                t = tc
                print("[LOG] Manual transcript selected", flush=True)
                break

        # If none manual → auto
        if t is None:
            for tc in transcripts:
                if tc.is_generated:
                    t = tc
                    print("[LOG] Auto-generated transcript selected", flush=True)
                    break

        # Fallback first one
        if t is None:
            t = list(transcripts)[0]
            print("[LOG] Fallback transcript selected", flush=True)

        print("[STEP4] Fetching full transcript...", flush=True)
        data = t.fetch()

        result = [{"text": x.text, "start": x.start, "duration": x.duration} for x in data]

        print("[SUCCESS] Transcript ready", flush=True)
        return Response(
    json.dumps({
        "video_id": video_id,
        "language": t.language_code,
        "generated": t.is_generated,
        "transcript": result
    }, ensure_ascii=False),               # <-- FIX
    mimetype="application/json"
), 200

    except (TranscriptsDisabled, NoTranscriptFound):
        print("[ERROR] Transcript not available", flush=True)
        return jsonify({"error": "No transcript available"}), 404

    except Exception as e:
        print("[CRASH ERROR]", e, flush=True)
        return jsonify({"error": str(e)}), 500


# ----------------- RAILWAY ENTRY ----------------- #
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[SERVER] Running on port {port}", flush=True)
    app.run(host="0.0.0.0", port=port)
