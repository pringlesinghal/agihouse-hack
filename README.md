# Image Description Web App

This is a simple web application that uses Google's Gemini 2 model to generate descriptions for images. Users can either upload an image file or provide an image URL.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
   - Get your API key from Google AI Studio (https://makersuite.google.com/app/apikey)
   - Copy the `.env.example` file to `.env`
   - Replace `your_api_key_here` with your actual Google API key

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to `http://localhost:5000`

## Features

- Upload images from your local device
- Analyze images from URLs
- Real-time image preview
- Detailed image descriptions using Gemini 2
- Modern, responsive UI using Tailwind CSS

## Requirements

- Python 3.7+
- Flask
- Google Generative AI Python SDK
- Internet connection for API calls
