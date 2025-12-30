from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os

app = Flask(__name__)

@app.route("/")
def home():
    print("[LOG] / endpoint hit", flush=True)
    return {"status": "YouTube Transcript API Active 🚀"}

@app.route("/transcript")
def get_transcript():
    print("[LOG] /transcript endpoint hit", flush=True)

    video_id = request.args.get("id") or request.args.get("v")
    print(f"[LOG] Request video_id = {video_id}", flush=True)

    if not video_id:
        print("[ERROR] Missing ID", flush=True)
        return jsonify({"error": "Use /transcript?id=VIDEOID"}), 400

    try:
        print("[STEP1] Creating YouTubeTranscriptApi...", flush=True)
        api = YouTubeTranscriptApi()

        print("[STEP2] Getting transcripts list...", flush=True)
        transcripts = api.list(video_id)
        print("[LOG] Languages:", transcripts._languages, flush=True)

        print("[STEP3] Selecting language...", flush=True)
        try:
            t = transcripts.find_manually_created_transcript(transcripts._languages)
            print("[LOG] Manual used", flush=True)
        except:
            try:
                t = transcripts.find_generated_transcript(transcripts._languages)
                print("[LOG] Auto-generated used", flush=True)
            except:
                t = list(transcripts)[0]
                print("[LOG] Fallback to first transcript", flush=True)

        print("[STEP4] Fetching transcript...", flush=True)
        data = t.fetch()
        result = [{"text": x.text, "start": x.start, "duration": x.duration} for x in data]

        print("[SUCCESS] Transcript returned", flush=True)
        return jsonify({
            "video_id": video_id,
            "language": t.language_code,
            "generated": t.is_generated,
            "transcript": result
        })

    except (TranscriptsDisabled, NoTranscriptFound):
        print("[ERROR] No transcript", flush=True)
        return jsonify({"error": "No transcript available"}), 404
    except Exception as e:
        print("[CRASH]", e, flush=True)
        return jsonify({"error": str(e)}), 500


# === RUN SERVER USING RAILWAY PORT ===
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[SERVER] Running on port {port}", flush=True)
    app.run(host="0.0.0.0", port=port)
