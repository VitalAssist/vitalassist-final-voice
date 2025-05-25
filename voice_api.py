# voice_api.py - Final Voice API with Debugging (Whisper + Edge TTS)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import openai
import edge_tts
import asyncio

# ✅ Init
app = Flask(__name__)
CORS(app)

print("🚀 VitalAssist Flask API started and ready.")

# ✅ Whisper (Transcribe)
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        print("🎤 /transcribe endpoint called")

        if "audio" not in request.files:
            print("❌ No audio received in request.files")
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        print("📥 Received:", audio_file.filename, "| Type:", audio_file.content_type)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            audio_path = temp.name
            audio_file.save(audio_path)

        print("📤 Audio saved to:", audio_path)

        # Whisper
        with open(audio_path, "rb") as af:
            print("🔁 Sending to OpenAI Whisper...")
            transcript = openai.Audio.transcribe("whisper-1", af)

        os.remove(audio_path)
        print("✅ Whisper result:", transcript["text"])

        return jsonify({"text": transcript["text"]})

    except Exception as e:
        print("🔥 Whisper ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Edge TTS (Speak)
@app.route("/speak", methods=["POST"])
def synthesize():
    try:
        data = request.json
        text = data.get("text", "").strip()
        lang = data.get("lang", "en")

        print(f"🔊 TTS requested: '{text}' in language: {lang}")

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

        output_path = os.path.join(tempfile.gettempdir(), "output.mp3")

        async def generate():
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(output_path)

        asyncio.run(generate())

        return send_file(output_path, mimetype="audio/mpeg")

    except Exception as e:
        print("🔥 TTS ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Optional root route for testing
@app.route("/")
def home():
    return "✅ VitalAssist Voice Server is Online."
    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ✅ Required by Render
    app.run(host="0.0.0.0", port=port)



