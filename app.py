import os
import base64
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    file_data = data.get("file_data", None) # Base64 formatında fayl
    file_type = data.get("file_type", None) # Mime-type (image/png, audio/mp3 və s.)

    if not user_message and not file_data:
        return jsonify({"response": "Xahiş olunur mesaj yazın və ya fayl əlavə edin."})

    contents = []
    
    # Əgər şəkil və ya fayl göndərilibsə
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
            model="gemini-3.6-flash",
            contents=contents,
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Xəta baş verdi: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
