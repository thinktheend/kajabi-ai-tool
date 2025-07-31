import os
from flask import Flask, request, jsonify
from openai import OpenAI
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        response = app.make_response(('', 204))
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
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a Spanish vocabulary tool. You must always respond with a valid JSON object. Do not add any extra commentary."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_data = json.loads(completion.choices[0].message.content)
            response = jsonify(response_data)
            response.status_code = 200

        except Exception as e:
            response = jsonify({"error": "An internal server error occurred.", "details": str(e)})
            response.status_code = 500
    else:
        response = jsonify(error="Method Not Allowed")
        response.status_code = 405

    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
    
    return response
