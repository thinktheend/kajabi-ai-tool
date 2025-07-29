import os
from flask import Flask, request, jsonify
from openai import OpenAI

# This is the main Flask app object
app = Flask(__name__)

# This is the main function that Vercel will run
@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def catch_all(path):
    # --- Handle the browser's "preflight" request ---
    # This happens before the real request is sent, to check permissions.
    if request.method == 'OPTIONS':
        # Create an empty response
        response = app.make_response(('', 204))
        # Add the necessary permission headers (the "permission slip")
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # --- Handle the actual data request ---
    if request.method == 'POST':
        try:
            # Check if the API key exists in Vercel's environment variables
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                # If the key is missing, return a clear error
                print("SERVER ERROR: OPENAI_API_KEY environment variable not set.")
                return jsonify({"error": "Server configuration error: API key missing."}), 500

            # Get the prompt from the request
            data = request.get_json()
            if not data or 'prompt' not in data:
                return jsonify({"error": "Bad request: 'prompt' field is missing."}), 400
            
            prompt = data.get("prompt")
            
            # Initialize the OpenAI client with the key
            client = OpenAI(api_key=api_key)
            
            # Send the request to the AI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a Spanish vocabulary tool. You must always respond with a valid JSON object."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Send the AI's response back to Kajabi
            return completion.choices[0].message.content, 200

        except Exception as e:
            # If any other error happens (like an OpenAI billing issue), log it and return an error
            print(f"AN UNEXPECTED ERROR OCCURRED: {e}")
            return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

    # If the request is not POST or OPTIONS, it's not allowed
    return jsonify(error="Method Not Allowed"), 405
