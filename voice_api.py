# voice_api.py - VitalAssist Cloud Voice Server (Whisper + Edge TTS)
from flask import Flask, request, jsonify, send_file
import whisper
import tempfile
import os
import edge_tts
import asyncio

app = Flask(__name__)
model = whisper.load_model("base")  # Fast for web

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        audio_path = temp.name
        audio_file.save(audio_path)

    result = model.transcribe(audio_path)
    os.remove(audio_path)
    return jsonify({"text": result["text"]})

@app.route("/speak", methods=["POST"])
def synthesize():
    data = request.json
    text = data.get("text", "")
    lang = data.get("lang", "en")
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
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    asyncio.run(generate())

    return send_file(output_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
