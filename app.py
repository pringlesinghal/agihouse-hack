import os
from flask import Flask, request, render_template, jsonify
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

app = Flask(__name__)

def get_description(image_data=None, text_input=None):
    try:
        prompt = ["Analyze the following information about a product and company."]
        content = []
        
        if image_data:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            content.append(image)
            prompt[0] += " Based on the product image"
        
        if text_input:
            content.append(text_input)
            if text_input.startswith('http'):
                prompt[0] += " and the company's website"
            else:
                prompt[0] += " and the provided product/company description"
        
        if not content:
            return "Please provide either an image or text description"
            
        prompt[0] += ", provide a comprehensive analysis of the product and company. Include details about the product's features, target market, and company's value proposition."
        content = prompt + content
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating description: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    image_data = None
    text_input = None

    # Handle image input
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            image_data = file.read()
    elif 'image_url' in request.form and request.form['image_url'].strip():
        try:
            response = requests.get(request.form['image_url'])
            image_data = response.content
        except Exception as e:
            return jsonify({'error': f'Error fetching image: {str(e)}'}), 400

    # Handle text input
    if 'text_input' in request.form and request.form['text_input'].strip():
        text_input = request.form['text_input'].strip()
        text_input_type = request.form.get('text_input_type', 'text')
        
        if text_input_type == 'url':
            try:
                response = requests.get(text_input)
                if response.status_code != 200:
                    return jsonify({'error': f'Error fetching website content: HTTP {response.status_code}'}), 400
                # Extract text content from HTML (you might want to use BeautifulSoup for better extraction)
                text_input = response.text
            except Exception as e:
                return jsonify({'error': f'Error fetching website content: {str(e)}'}), 400

    if not image_data and not text_input:
        return jsonify({'error': 'Please provide either an image or text description'}), 400

    description = get_description(image_data, text_input)
    return jsonify({'description': description})

if __name__ == '__main__':
    app.run(debug=True)
