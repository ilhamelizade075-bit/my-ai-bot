import os
import base64
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from google import genai
from google.genai import types

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zaza_live_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

# Standart metn/fayl çatı üçün
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    file_data = data.get("file_data", None)
    file_type = data.get("file_type", None)

    if not user_message and not file_data:
        return jsonify({"response": "Xahiş olunur mesaj yazın və ya fayl əlavə edin."})

    contents = []
    
    if file_data and file_type:
        try:
            raw_bytes = base64.b64decode(file_data.split(",")[1] if "," in file_data else file_data)
            contents.append(
                types.Part.from_bytes(
                    data=raw_bytes,
                    mime_type=file_type
                )
            )
        except Exception as e:
            return jsonify({"response": f"Fayl emal edilərkən xəta baş verdi: {str(e)}"})

    if user_message:
        contents.append(user_message)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Xəta baş verdi: {str(e)}"})

# WebSocket - Canlı Səs Sessiyası
@socketio.on('connect')
def handle_connect():
    print("İstifadəçi canlı səs xəttinə qoşuldu.")

@socketio.on('disconnect')
def handle_disconnect():
    print("İstifadəçi səs xəttindən ayrıldı.")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
