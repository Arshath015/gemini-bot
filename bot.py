from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from datetime import datetime
import time
import os
from threading import Thread

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCIltxS9C-feeMo63TUy6CPaCZtCEn4aPo')
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Chat history storage
chat_history = {}

def get_chat_history(session_id):
    if session_id not in chat_history:
        chat_history[session_id] = model.start_chat(history=[])
    return chat_history[session_id]

def periodic_updates():
    """Periodically clean up old chat sessions"""
    while True:
        time.sleep(3600)  # Run every hour
        now = time.time()
        # Cleanup logic can be added here if needed

# Start the periodic update thread
update_thread = Thread(target=periodic_updates)
update_thread.daemon = True
update_thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data['message']
        
        # Get or create chat session
        chat_session = get_chat_history(session_id)
        
        # Send message to Gemini
        response = chat_session.send_message(message)
        
        # Format response
        bot_response = {
            'text': response.text,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(bot_response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
