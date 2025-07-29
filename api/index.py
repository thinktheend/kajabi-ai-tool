from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# This is the entry point for the Vercel serverless function
def handler(request):
    # Only allow POST requests
    if request.method != 'POST':
        return jsonify(error="Method Not Allowed"), 405

    try:
        # Get the prompt from the request sent by our Kajabi page
        data = request.json
        if not data or 'prompt' not in data:
            print("ERROR: Bad request, 'prompt' missing.")
            return jsonify(error="No prompt provided"), 400
        
        prompt = data.get("prompt")
        print(f"Received prompt: {prompt}") # Log that we received a prompt
        
        # Initialize OpenAI client using a secure environment variable
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Send the prompt to the AI
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a Spanish vocabulary tool. You must always respond with a valid JSON object based on the user's prompt."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Send the AI's response back to the Kajabi page
        response_content = completion.choices[0].message.content
        print("Successfully got response from AI.") # Log success
        return response_content, 200
        
    except Exception as e:
        # This is the most important log! It will show us the exact error.
        print(f"AN ERROR OCCURRED: {e}") 
        return jsonify(error=str(e)), 500
