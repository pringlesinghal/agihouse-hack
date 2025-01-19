# AI-Powered Advertisement Generator for SMBs

Small and Medium Businesses lack the resources to create high quality advertisements that are engaging and tailored to their target audiences. This easy-to-use web app allows business owners to add a small text description of their product along with an optional image, after which the app performs customer segment discovery, identifies the most important elements in advertisement to appeal to these customers, and then uses Veo for AI-powered text to video generation to create the advertisement.

## Key Features

- **Customer Segment Analysis**: Automatically identifies and analyzes different customer segments for your product
- **Persona Generation**: Creates detailed customer personas for each identified segment
- **Video Ad Prompt Generation**: Generates tailored 8-second video advertisement prompts for each customer segment
- **Multi-Input Support**: 
  - Text descriptions of products/services
  - Image upload capability
  - URL input for both images and website content
- **Modern, Responsive UI**: Clean interface built with Tailwind CSS

## How It Works

1. **Input Your Product Details**:
   - Enter a text description of your product/service
   - Optionally upload a product image or provide URLs

2. **Automated Analysis**:
   - The app analyzes your input using Google's Gemini 2 model
   - Identifies distinct customer segments
   - Generates detailed customer personas

3. **Advertisement Generation**:
   - Creates targeted video prompts for each customer segment
   - Optimized for 8-second video advertisements
   - Includes specific visual and audio recommendations
   - Structured with clear opening, benefit showcase, and call to action

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys:
   - Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Copy `.env.example` to `.env`
   - Add your API key to the `.env` file

3. Run the application:
```bash
python app.py
```

4. Access the web interface at `http://localhost:5000`

## Technical Requirements

- Python 3.7+
- Flask web framework
- Google Generative AI Python SDK
- Internet connection for API access
- Modern web browser

## System Components

- **Detailed Analysis Service**: Processes input and extracts key product features
- **Revenue Analysis Service**: Identifies and segments potential customer bases
- **Persona Generator**: Creates detailed customer personas and video ad prompts
- **Cache Service**: Optimizes performance by caching analysis results

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Add your chosen license here]
