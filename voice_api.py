# voice_api.py - Final Voice API with Debugging (Whisper + Edge TTS)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import edge_tts
import asyncio
import whisper  # ✅ Make sure this is at the top

# ✅ Init

app = Flask(__name__)
CORS(app)  # ✅ This allows Netlify to talk to Flask

app = Flask(__name__)
CORS(app)

print("🚀 VitalAssist Flask API started and ready.")

# ✅ Whisper (Transcribe)
import whisper  # ✅ Make sure this is at the top

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        print("🚀 /transcribe endpoint HIT")

        if "audio" not in request.files:
            print("❌ No audio in request")
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        print("📥 Received file:", audio_file.filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            audio_path = temp.name
            audio_file.save(audio_path)

        print("🔁 Running Whisper locally...")
        model = whisper.load_model("base")  # You can use "tiny" if base is slow
        result = model.transcribe(audio_path)

        os.remove(audio_path)
        print("✅ Transcribed:", result["text"])
        return jsonify({"text": result["text"]})

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

# ✅ Required by Render to bind to port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




