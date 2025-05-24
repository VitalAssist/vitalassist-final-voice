from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import uuid
import os

app = Flask(__name__)
VOICE = "en-US-JennyNeural"

@app.route("/")
def home():
    return "VitalAssist Python Voice Server is live."

@app.route("/api/voice", methods=["POST"])
def voice():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    output_path = f"temp_{uuid.uuid4().hex}.mp3"

    async def generate():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)

    asyncio.run(generate())

    return send_file(output_path, mimetype="audio/mpeg", as_attachment=False, download_name="response.mp3")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)