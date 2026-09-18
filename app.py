import os
import base64
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Fetch Gemini API Key from environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    # Initialize the new Google GenAI client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # System instruction for Zaza AI Helper
    system_instruction = "You are Zaza AI Helper, a helpful and smart AI assistant."
    
    # Updated config for the new SDK
    config = types.GenerateContentConfig(
        system_instruction=system_instruction
    )
else:
    client = None

def get_ai_response(contents):
    try:
        # Using gemini-2.5-flash model with the new SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=config
        )
        return response.text, 200
    except Exception as e:
        return f"API Error encountered: {str(e)}", 500

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
