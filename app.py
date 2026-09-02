import os
from flask import Flask, render_template, request, Response
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
        return Response("Please type a message.", mimetype='text/plain')

    def generate():
        try:
            # generate_content_stream cavabları parça-parça anında göndərir
            response = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=user_message,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[Xəta baş verdi: {str(e)}]"

    return Response(generate(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
