@app.route("/transcript")
def get_transcript():
    print("[LOG] /transcript endpoint hit", flush=True)

    video_id = request.args.get("id") or request.args.get("v")
    print(f"[LOG] Request video_id = {video_id}", flush=True)

    if not video_id:
        print("[ERROR] Missing ID", flush=True)
        return jsonify({"error": "Use /transcript?id=VIDEO_ID"}), 400

    try:
        print("[STEP1] Creating API client", flush=True)
        api = YouTubeTranscriptApi()

        print("[STEP2] Fetching transcript list...", flush=True)
        transcripts = api.list(video_id)

        # Available languages list
        available_langs = [t.language_code for t in transcripts]
        print("[LOG] Available:", available_langs, flush=True)

        print("[STEP3] Selecting language priority...", flush=True)
        t = None

        # Try manual first
        for tc in transcripts:
            if not tc.is_generated:
                t = tc
                print("[LOG] Selected: manual transcript", flush=True)
                break

        # If none manual → try generated
        if t is None:
            for tc in transcripts:
                if tc.is_generated:
                    t = tc
                    print("[LOG] Selected: auto-generated transcript", flush=True)
                    break

        # final fallback
        if t is None:
            t = list(transcripts)[0]
            print("[LOG] Selected fallback transcript", flush=True)

        print("[STEP4] Fetching transcript text...", flush=True)
        data = t.fetch()

        result = [{"text": x.text, "start": x.start, "duration": x.duration} for x in data]

        print("[SUCCESS] Transcript ready", flush=True)

        return jsonify({
            "video_id": video_id,
            "language": t.language_code,
            "generated": t.is_generated,
            "transcript": result
        }), 200

    except (TranscriptsDisabled, NoTranscriptFound):
        print("[ERROR] No transcript available", flush=True)
        return jsonify({"error": "Transcript not available"}), 404

    except Exception as e:
        print("[CRASH]", e, flush=True)
        return jsonify({"error": str(e)}), 500
