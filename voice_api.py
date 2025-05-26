# voice_api.py — Clean version with Whisper Tiny + Edge TTS for Render
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import edge_tts
import asyncio
import whisper

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("🚀 VitalAssist Flask API started and ready.")

# 🔊 Local Whisper (tiny) transcription
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        print("🎤 /transcribe endpoint HIT")

        if "audio" not in request.files:
            print("❌ No audio file in request")
            return jsonify({"error": "No audio uploaded"}), 400

        audio_file = request.files["audio"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            audio_path = temp.name
            audio_file.save(audio_path)

        print("🧠 Loading Whisper tiny model...")
        model = whisper.load_model("tiny")  # ✅ lightweight for Render
        print("📂 Running transcription...")
result = model.transcribe(audio_path)
print("✅ Whisper returned:", result)


        os.remove(audio_path)
        print("✅ Transcription:", result["text"])
        return jsonify({"text": result["text"]})

    except Exception as e:
        print("🔥 Whisper ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# 🗣️ TTS with Edge
@app.route("/speak", methods=["POST"])
def synthesize():
    try:
        data = request.json
        text = data.get("text", "").strip()
        lang = data.get("lang", "en")

        print(f"🔊 TTS: '{text}' in lang: {lang}")

        if not text:
            raise ValueError("No text provided for TTS.")

        voice_map = {
            "en": "en-US-JennyNeural",
            "ar": "ar-EG-SalmaNeural",
            "fa": "fa-IR-DilaraNeural",
            "hi": "hi-IN-SwaraNeural",
            "ku": "en-US-JennyNeural",
        }
        voice = voice_map.get(lang, "en-US-JennyNeural")
        output_path = os.path.join(tempfile.gettempdir(), "tts_output.mp3")

        async def generate():
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(output_path)

        asyncio.run(generate())
        return send_file(output_path, mimetype="audio/mpeg")

    except Exception as e:
        print("🔥 TTS ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Health check
@app.route("/")
def home():
    return "✅ VitalAssist Voice Server is Online."

# ✅ Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
