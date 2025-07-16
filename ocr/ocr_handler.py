import requests

# ✅ Replace with your OCR.Space API Key
OCR_API_KEY = "K86277928688957"

def extract_text_from_image(image_file):
    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "eng",
                "isOverlayRequired": False
            },
        )

        if response.status_code != 200:
            return f"⚠️ HTTP Error {response.status_code}: {response.text}"

        result = response.json()
        if result.get("IsErroredOnProcessing"):
            return f"⚠️ OCR API Error: {result.get('ErrorMessage', ['Unknown error'])[0]}"
        
        parsed_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")
        return parsed_text.strip() if parsed_text else "⚠️ No text detected."

    except Exception as e:
        return f"⚠️ Exception during OCR: {str(e)}"
