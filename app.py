import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Render mühitindən API Key-i oxuyur
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Zəhmət olmasa mesaj yazın."})

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Xəta baş verdi: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 
