from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "YouTube Transcript API Active 🚀"}

@app.route("/transcript")
def get_transcript():
    video_id = request.args.get("id") or request.args.get("v")
    if not video_id:
        return jsonify({"error": "Provide video id like /transcript?id=VIDEO_ID"}), 400

    try:
        print(f"[LOG] Fetching transcript for: {video_id}", flush=True)

        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)

        try:
            t = transcripts.find_manually_created_transcript(transcripts._languages)
        except:
            try:
                t = transcripts.find_generated_transcript(transcripts._languages)
            except:
                t = list(transcripts)[0]

        transcript = t.fetch()
        result = [{"text": item.text, "start": item.start, "duration": item.duration} for item in transcript]

        print(f"[LOG] Returning transcript for {video_id}, Language: {t.language_code}", flush=True)

        return jsonify({
            "video_id": video_id,
            "language": t.language_code,
            "generated": t.is_generated,
            "transcript": result
        }), 200

    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({"error": "No transcript available"}), 404
    except Exception as e:
        print("[ERROR]", e, flush=True)   # <- IMPORTANT LOG
        return jsonify({"error": str(e)}), 500


# -------------------- SERVER START (IMPORTANT) -------------------- #
if __name__ == "__main__":
    print("[SERVER] Flask running on port 5000...", flush=True)
    app.run(host="0.0.0.0", port=5000)
