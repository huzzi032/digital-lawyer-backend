from flask import Flask, request, jsonify
import os
import requests
from flask_cors import CORS
from pathlib import Path
from ocr.ocr_handler import extract_text_from_image

app = Flask(__name__)
CORS(app)

# ✅ Get HuggingFace token from env
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ✅ Function to search .txt law files
def search_laws(query):
    combined_text = ""
    laws_dir = Path("backend/data/laws")
    for law_file in laws_dir.glob("*.txt"):
        with open(law_file, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            if query.lower() in text.lower():
                combined_text += f"\n--- {law_file.name} ---\n"
                combined_text += text[:4000]
    return combined_text if combined_text else "No relevant law found."

# ✅ Function to call Hugging Face API (Mistral)
def call_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.3
        }
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        return data[0]['generated_text'] if isinstance(data, list) else data
    else:
        return f"⚠️ HuggingFace Error {response.status_code}: {response.text}"

# ✅ Route to handle legal question
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
    answer = call_mistral(prompt)
    return jsonify({"answer": answer})

# ✅ Route to handle OCR image uploads
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image = request.files['image']
    text = extract_text_from_image(image)
    return jsonify({'extracted_text': text})

# ✅ Run with Railway's expected port (usually 8080)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
