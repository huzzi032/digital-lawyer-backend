from flask import Flask, request, jsonify
import os
import requests
from flask_cors import CORS
from pathlib import Path
from ocr.ocr_handler import extract_text_from_image

app = Flask(__name__)
CORS(app)

# ✅ Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Search Pakistani law .txt files
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

# ✅ Function to call Groq API using LLaMA3
def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama3-8b-8192",  # ✅ Updated model
        "temperature": 0.3
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Groq Error {response.status_code}: {response.text}"

# ✅ Route to ask legal questions
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
    answer = call_groq(prompt)
    return jsonify({"answer": answer})

# ✅ OCR image processing route
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image = request.files['image']
    text = extract_text_from_image(image)
    return jsonify({'extracted_text': text})

# ✅ Run app on Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
