import os
import time
import base64
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.api_core.exceptions import ServiceUnavailable, GoogleAPIError

app = Flask(__name__)

# Fetch Gemini API Key from environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # System instruction for Zaza AI Helper
    system_instruction = "You are Zaza AI Helper, a helpful and smart AI assistant."
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction
    )
else:
    model = None

# Sizin soruşduğunuz funksiyanın tam tətbiq olunmuş forması
def get_ai_response(contents):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(contents)
            return response.text, 200
        except ServiceUnavailable:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Waits 1s, 2s, etc. before retrying
                continue
            else:
                return "The system is currently experiencing high demand. Please try again in a few seconds.", 503
        except GoogleAPIError as e:
            return f"API Error encountered: {str(e)}", 500
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not model:
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
            contents.append({
                "mime_type": file_type,
                "data": raw_bytes
            })
        except Exception as e:
            print(f"File processing error: {e}")

    if user_message:
        contents.append(user_message)

    if not contents:
        return jsonify({"response": "Please provide a message or an attachment."}), 400

    # AI cavabını funksiya vasitəsilə alırıq
    ai_response_text, status_code = get_ai_response(contents)
    return jsonify({"response": ai_response_text}), status_code

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
