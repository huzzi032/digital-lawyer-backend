from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS
from pathlib import Path
from ocr.ocr_handler import extract_text_from_image

app = Flask(__name__)
CORS(app)

# Load OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Search Pakistani law .txt files
def search_laws(query):
    combined_text = ""
    laws_dir = Path("backend/data/laws")
    for law_file in laws_dir.glob("*.txt"):
        with open(law_file, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            if query.lower() in text.lower():
                combined_text += f"\n--- {law_file.name} ---\n"
                combined_text += text[:4000]  # Limit text for prompt length
    return combined_text if combined_text else "No relevant law found."

# Route: POST /ask (text query)
@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    law_context = search_laws(question)

    prompt = f"""
You are a Pakistani Legal Assistant AI. Use the following laws to answer the question:
----
{law_context}
----

Question: {question}
Give a legal answer with proper section references.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return jsonify({"answer": response['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route: POST /ocr (image input)
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image = request.files['image']
    text = extract_text_from_image(image)
    return jsonify({'extracted_text': text})

# ✅ Production-compatible run config
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
