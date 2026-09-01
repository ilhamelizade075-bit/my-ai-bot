import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Lütfən bir mesaj yazın."})

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Xəta baş verdi: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
