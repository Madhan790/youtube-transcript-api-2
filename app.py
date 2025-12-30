from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
        print("[ERROR] Missing video ID", flush=True)
        return jsonify({"error": "Use /transcript?id=VIDEOID"}), 400

    try:
        print("[STEP 1] Initializing API client", flush=True)
        api = YouTubeTranscriptApi()

        print("[STEP 2] Fetching transcript list...", flush=True)
        transcripts = api.list(video_id)
        print(f"[LOG] Available transcripts: {transcripts._languages}", flush=True)

        print("[STEP 3] Selecting best transcript option", flush=True)
        try:
            t = transcripts.find_manually_created_transcript(transcripts._languages)
            print("[LOG] Selected: Manual transcript", flush=True)
        except:
            try:
                t = transcripts.find_generated_transcript(transcripts._languages)
                print("[LOG] Selected: Auto-generated transcript", flush=True)
            except:
                t = list(transcripts)[0]
                print("[LOG] Selected fallback transcript", flush=True)

        print("[STEP 4] Fetching transcript text...", flush=True)
        transcript = t.fetch()

        print("[STEP 5] Building JSON response", flush=True)
        result = [{"text": item.text, "start": item.start, "duration": item.duration} for item in transcript]

        print(f"[SUCCESS] Returning transcript for {video_id} | Lang: {t.language_code}", flush=True)

        return jsonify({
            "video_id": video_id,
            "language": t.language_code,
            "generated": t.is_generated,
            "transcript": result
        }), 200

    except TranscriptsDisabled:
        print("[ERROR] Transcript disabled", flush=True)
        return jsonify({"error": "No transcript available"}), 404

    except NoTranscriptFound:
        print("[ERROR] No transcript found", flush=True)
        return jsonify({"error": "Transcript not found"}), 404

    except Exception as e:
        print("[CRASH] Unexpected error:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500


# -------------------- SERVER ENTRY POINT -------------------- #
if __name__ == "__main__":
    print("[SERVER] Starting Flask on 0.0.0.0:5000", flush=True)
    app.run(host="0.0.0.0", port=5000)
