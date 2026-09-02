import os
import time
from flask import Flask, render_template, request, jsonify
from google import genai

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
    if not user_message:
        return jsonify({"response": "Xahiş olunur mesaj yazın."})

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_message,
            )
            return jsonify({"response": response.text})
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(1)
                continue
            return jsonify({"response": f"Xəta baş verdi: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
