import os
import time
import base64
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Fetch Gemini API Key from environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    # Initialize the official Google GenAI client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Azərbaycan dilində cavab verməsi üçün sistem təlimatı
    system_instruction = "Sen Zaza AI Helper adlı köməkçisən. İstifadəçilərə həmişə səmimi, ağıllı və Azərbaycan dilində cavab ver."
    
    # Configuration for Gemini Model
    config = types.GenerateContentConfig(
        system_instruction=system_instruction
    )
else:
    client = None

def get_ai_response(contents):
    max_retries = 5  # Cəhd sayını 5-ə qaldırdıq
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=contents,
                config=config
            )
            return response.text, 200
        except Exception as e:
            err_str = str(e)
            # 503 və ya UNAVAILABLE olduqda daha səbrlə gözləyirik (2s, 3s, 4s...)
            if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                time.sleep(2 + attempt)
                continue
            else:
                return f"Server hazırda məşğuldur, zəhmət olmasa bir neçə saniyə sonra yenidən cəhd edin. (Xəta: {err_str})", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"response": "API Key is not configured. Please check your GEMINI_API_KEY environment variable."}), 500

    data = request.json or {}
    user_message = data.get('message', '')
    file_data = data.get('file_data')
    file_type = data.get('file_type')

    contents = []

    # Process attachment if present
    if file_data and file_type:
        try:
            if ',' in file_data:
                file_data = file_data.split(',')[1]
            
            raw_bytes = base64.b64decode(file_data)
            contents.append(
                types.Part.from_bytes(
                    data=raw_bytes,
                    mime_type=file_type
                )
            )
        except Exception as e:
            print(f"File processing error: {e}")

    if user_message:
        contents.append(user_message)

    if not contents:
        return jsonify({"response": "Please provide a message or an attachment."}), 400

    ai_response_text, status_code = get_ai_response(contents)
    return jsonify({"response": ai_response_text}), status_code

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
