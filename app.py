import os
from flask import Flask, request, render_template, jsonify
from PIL import Image
from google import genai
from google.genai.types import Tool
from dotenv import load_dotenv
import requests
from services.detailed_analysis import get_detailed_analysis
from services.revenue_analysis import get_revenue_segments
from services.persona_generator import generate_personas
from services.cache_service import CacheService

# Load environment variables
load_dotenv()

# Configure Google Gemini API
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize cache service
cache_service = CacheService()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Handle analysis requests for both image and text inputs."""
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

    try:
        # Combine inputs for query hash
        query_input = {
            'image': bool(image_data),
            'text': text_input
        }

        # Step 1: Get detailed analysis
        detailed_analysis, error = get_detailed_analysis(
            image_data=image_data,
            text_input=text_input,
            client=client
        )
        
        if error:
            return jsonify({'error': error})

        # Step 2: Get revenue segments
        segments_result, error = get_revenue_segments(detailed_analysis, client)
        
        if error:
            return jsonify({'error': error})

        # Step 3: Generate personas for each segment
        personas, error = generate_personas(segments_result['segments'], client)
        
        if error:
            return jsonify({'error': error})

        # Step 4: Cache the results
        cached_data = cache_service.cache_analysis(
            query_input=query_input,
            segments_data=segments_result,
            personas=personas
        )

        # Return results with segment keys
        result = {
            'segments': segments_result['segments'],
            'personas': personas,
            'segment_keys': {name: data['segment_key'] for name, data in cached_data.items()},
            'grounding_data': segments_result.get('grounding_data')
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/persona/<segment_key>', methods=['GET'])
def get_persona(segment_key):
    """Retrieve a cached persona by segment key."""
    persona_data = cache_service.get_cached_persona(segment_key)
    if persona_data:
        return jsonify(persona_data)
    return jsonify({'error': 'Persona not found'}), 404

@app.route('/personas', methods=['GET'])
def get_all_personas():
    """Retrieve all cached personas."""
    personas = cache_service.get_all_personas()
    return jsonify(personas)

if __name__ == '__main__':
    app.run(debug=True)
