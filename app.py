from flask import Flask, request, jsonify, Response
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os, json

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
    print(f"[LOG] Video ID received = {video_id}", flush=True)

    if not video_id:
        print("[ERROR] Missing video id", flush=True)
        return jsonify({"error": "Use /transcript?id=VIDEO_ID"}), 400

    try:
        print("[STEP1] Creating API client", flush=True)
        api = YouTubeTranscriptApi()

        print("[STEP2] Fetching transcript list", flush=True)
        transcripts = api.list(video_id)

        available_langs = [t.language_code for t in transcripts]
        print("[LOG] Available CC languages:", available_langs, flush=True)

        # ------------- Language selection logic ------------- #
        t = None

        # 1. Prefer Manual first
        for tc in transcripts:
            if not tc.is_generated:
                t = tc
                print("[LOG] Manual transcript selected", flush=True)
                break

        # 2. If no manual → Auto CC
        if t is None:
            for tc in transcripts:
                if tc.is_generated:
                    t = tc
                    print("[LOG] Auto-generated transcript selected", flush=True)
                    break

        # 3. Final fallback (first available)
        if t is None:
            t = list(transcripts)[0]
            print("[LOG] Fallback transcript used", flush=True)

        print("[STEP3] Fetching transcript text", flush=True)
        data = t.fetch()

        # Prepare output in UTF-8 readable format
        result = [{"text": x.text, "start": x.start, "duration": x.duration} for x in data]

        print("[SUCCESS] Returning transcript", flush=True)

        return Response(
            json.dumps({
                "video_id": video_id,
                "language": t.language_code,
                "generated": t.is_generated,
                "transcript": result
            }, ensure_ascii=False, indent=2),   # 👈 Tamil readable fix
            mimetype="application/json"
        )

    except (TranscriptsDisabled, NoTranscriptFound):
        print("[ERROR] No transcript exists for this video", flush=True)
        return jsonify({"error": "Transcript not available"}), 404

    except Exception as e:
        print("[CRASH ERROR]", e, flush=True)
        return jsonify({"error": str(e)}), 500


# ----------------- Railway Entry ----------------- #
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[SERVER] Running at port {port}", flush=True)
    app.run(host="0.0.0.0", port=port)
