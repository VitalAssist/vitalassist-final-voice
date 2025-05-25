# voice_api.py - Render-Optimized: Edge TTS + OpenAI Whisper
from flask import Flask, request, jsonify, send_file
import tempfile
import os
import edge_tts
import asyncio
import openai
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # 🆕
import tempfile, os, asyncio, edge_tts, openai

app = Flask(__name__)
CORS(app)  # ✅ Allow all cross-origin calls

openai.api_key = os.getenv("OPENAI_API_KEY")  # Set this in Render > Environment

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            audio_path = temp.name
            audio_file.save(audio_path)

        with open(audio_path, "rb") as af:
            transcript = openai.Audio.transcribe("whisper-1", af)

        os.remove(audio_path)
        return jsonify({"text": transcript["text"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)

    asyncio.run(generate())

    return send_file(output_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
