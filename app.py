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
        # First call to get detailed analysis
        detailed_prompt = """Analyze the provided product information and identify the most likely customer segments that would be interested in this product. 
        
Follow these steps in your analysis:
1. Product Understanding:
   - Analyze the visual elements and features from the image
   - Consider the product description and company information
   - Identify key product attributes and value propositions

2. Market Analysis:
   - Evaluate the price point or perceived value
   - Consider the product category and use cases
   - Identify the product's unique selling points

3. Customer Segmentation:
   - List the primary customer segments (demographic, psychographic, behavioral)
   - Explain why each segment would be interested
   - Rank segments by likelihood of purchase

4. Recommendations:
   - Suggest marketing channels for reaching these segments
   - Identify potential cross-selling opportunities
   - Note any seasonal or regional considerations

Provide a detailed analysis following these steps."""

        content = [detailed_prompt]
        
        if image_data:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            content.append(image)
        
        if text_input:
            if text_input.startswith('http'):
                content.append(f"Based on the company website: {text_input}")
            else:
                content.append(f"Based on the product description: {text_input}")
        
        if not content[1:]:  # If no image or text input provided
            return {"error": "Please provide either an image or text description"}

        # Get detailed analysis
        detailed_response = model.generate_content(content)
        if not detailed_response.text:
            return {"error": "Failed to generate analysis"}

        # Second call to extract and summarize segments
        summary_prompt = """Based on the following detailed analysis, extract the top 3-5 customer segments. 
For each segment, provide:
1. A clear segment name/title
2. A concise two-line description explaining why this segment would be interested in the product.

Format the response as:
[Segment Name]
[Two-line description]

[Next Segment Name]
[Two-line description]

etc.

Here's the analysis:
""" + detailed_response.text

        summary_response = model.generate_content([summary_prompt])
        
        return {
            "segments": summary_response.text
        }

    except Exception as e:
        return {"error": f"Error generating description: {str(e)}"}

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
                text_input = response.text
            except Exception as e:
                return jsonify({'error': f'Error fetching website content: {str(e)}'}), 400

    if not image_data and not text_input:
        return jsonify({'error': 'Please provide either an image or text description'}), 400

    result = get_description(image_data, text_input)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
