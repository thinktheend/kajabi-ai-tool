import os
from flask import Flask, request, jsonify
from openai import OpenAI
import json # Import the json library

# This is the main Flask app object
app = Flask(__name__)

# This is the main function that Vercel will run
@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def catch_all(path):
    # Handle the browser's "preflight" request
    if request.method == 'OPTIONS':
        response = app.make_response(('', 204))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Handle the actual data request
    if request.method == 'POST':
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                print("SERVER ERROR: OPENAI_API_KEY environment variable not set.")
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
            
            response_content = completion.choices[0].message.content
            
            # ####################################################################
            # ##  THIS IS THE NEW DIAGNOSTIC LINE TO LOG THE AI'S EXACT REPLY   ##
            # ####################################################################
            print(f"RAW AI RESPONSE: {response_content}")

            # Send the AI's response back to Kajabi
            # We also add a json.loads() here to ensure it's valid JSON before sending
            return jsonify(json.loads(response_content)), 200

        except Exception as e:
            print(f"AN UNEXPECTED ERROR OCCURRED: {e}")
            return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

    return jsonify(error="Method Not Allowed"), 405
