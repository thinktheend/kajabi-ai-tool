import os
from flask import Flask, request, jsonify
from openai import OpenAI
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def catch_all(path):
    # --- Handle the browser's "preflight" request ---
    if request.method == 'OPTIONS':
        # Create an empty response for the browser's security check
        response = app.make_response(('', 204))
    
    # --- Handle the actual data request ---
    elif request.method == 'POST':
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return jsonify({"error": "Server configuration error: API key missing."}), 500

            data = request.get_json()
            if not data or 'prompt' not in data:
                return jsonify({"error": "Bad request: 'prompt' field is missing."}), 400
            
            prompt = data.get("prompt")
            client = OpenAI(api_key=api_key)
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a Spanish vocabulary tool. You must always respond with a valid JSON object."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Create a success response with the AI's content
            response_data = json.loads(completion.choices[0].message.content)
            response = jsonify(response_data)
            response.status_code = 200

        except Exception as e:
            # Create an error response if something goes wrong
            response = jsonify({"error": "An internal server error occurred.", "details": str(e)})
            response.status_code = 500
    else:
        # If not POST or OPTIONS, create a "Method Not Allowed" response
        response = jsonify(error="Method Not Allowed")
        response.status_code = 405

    # ######################################################################
    # ##  THIS IS THE FIX: Add the permission headers to every response   ##
    # ######################################################################
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
    
    return response
