import os
from flask import Flask, request, render_template, jsonify
from PIL import Image
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Google Gemini API
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
model_id = "gemini-2.0-flash-exp"

# Configure Google Search tool
google_search_tool = Tool(
    google_search=GoogleSearch()
)

app = Flask(__name__)

def get_description(image_data=None, text_input=None):
    try:
        # First call to get detailed analysis
        detailed_prompt = """Analyze the provided product information and identify the customer segments with the highest revenue potential. 
        
Follow these steps in your analysis:
1. Product Understanding:
   - Analyze the visual elements, features, and quality level from the image/description
   - Identify key product attributes and value propositions
   - Estimate the likely price point or price range for this product

2. Market Size Analysis:
   - Evaluate the total addressable market (TAM) for this product category
   - Consider market trends and growth potential
   - Identify key purchasing factors and frequency

3. Customer Segmentation with Revenue Potential:
   - For each potential customer segment, estimate:
     * Average purchase value
     * Purchase frequency (per year)
     * Segment size (approximate number of customers)
     * Total potential annual revenue (purchase value × frequency × size)
   - Calculate the percentage contribution to total revenue for each segment
   - Only retain segments that fall in the top 80% of cumulative revenue

4. Market Penetration Factors:
   - Assess ease of reaching each segment
   - Consider customer acquisition costs
   - Evaluate competitive pressure in each segment

Provide a detailed analysis following these steps, with specific focus on revenue calculations."""

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

        # Get detailed analysis with grounding
        detailed_response = client.models.generate_content(
            model=model_id,
            contents=content,
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        
        if not detailed_response.candidates:
            return {"error": "Failed to generate analysis"}

        detailed_text = detailed_response.candidates[0].content.parts[0].text

        # Second call to extract and summarize top revenue segments
        summary_prompt = """Based on the detailed analysis, extract only the customer segments that contribute to the top 80% of total revenue potential.

For each segment, provide:
1. Segment Name/Title
2. Revenue Metrics:
   - Average purchase value
   - Annual purchase frequency
   - Estimated segment size
   - Total annual revenue potential
3. Brief description of why this segment is valuable

Format the response as:
[Segment Name]
Revenue Potential: $X million/year
- Avg Purchase: $X
- Frequency: X purchases/year
- Segment Size: X customers
[Two-line description of value proposition for this segment]

[Next Segment Name]
...etc.

Order segments by revenue potential (highest to lowest). Only include segments that together make up 80% of total revenue.

Here's the analysis:
""" + detailed_text

        # Get summary with grounding
        summary_response = client.models.generate_content(
            model=model_id,
            contents=[summary_prompt],
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        
        if not summary_response.candidates:
            return {"error": "Failed to generate summary"}

        summary_text = summary_response.candidates[0].content.parts[0].text
        
        # Get grounding metadata for debugging (optional)
        grounding_data = None
        try:
            grounding_data = summary_response.candidates[0].grounding_metadata.search_entry_point.rendered_content
        except:
            pass

        return {
            "segments": summary_text,
            "grounding_data": grounding_data
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
