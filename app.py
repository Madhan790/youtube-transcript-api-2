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
        return jsonify({"error": "Please provide video id like /transcript?id=VIDEO_ID"}), 400

    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)

        # Auto choose best transcript (manual > auto > fallback)
        try:
            t = transcripts.find_manually_created_transcript(transcripts._languages)
        except:
            try:
                t = transcripts.find_generated_transcript(transcripts._languages)
            except:
                t = list(transcripts)[0]

        transcript = t.fetch()

        # Convert to JSON text list
        result = [{"text": item.text, "start": item.start, "duration": item.duration} for item in transcript]

        return jsonify({
            "video_id": video_id,
            "language": t.language_code,
            "generated": t.is_generated,
            "transcript": result
        })

    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({"error": "No transcript available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
