from flask import Flask, render_template, request, jsonify
from emotion_detector import EmotionDetector
from tts_engine import TTSEngine
import os
import time

app = Flask(__name__)

detector = None
tts = None

def get_detector():
    global detector
    if detector is None:
        detector = EmotionDetector()
    return detector

def get_tts():
    global tts
    if tts is None:
        tts = TTSEngine(output_dir=os.path.join("static", "audio"))
    return tts

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        detection_result = get_detector().detect_emotion(text)
        
        filename = "output.mp3"
        output_path = get_tts().generate_audio(
            text=text, 
            emotion=detection_result["emotion"], 
            confidence=detection_result["confidence"], 
            speed=detection_result["speed"],
            volume=detection_result["volume"],
            pitch=detection_result["pitch"],
            pause_ms=detection_result["pause_ms"],
            filename=filename
        )
        
        cache_buster = int(time.time())
        audio_url = f"/static/audio/{filename}?t={cache_buster}"
        
        # Package the combined result and include audio access path
        response_data = {
            **detection_result,
            "audio_url": audio_url
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import static_ffmpeg
    static_ffmpeg.add_paths()
    os.makedirs(os.path.join("static", "audio"), exist_ok=True)
    print("Loading emotion detector model... This may take a minute on the very first run.")
    get_detector()
    print("Application is starting on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
