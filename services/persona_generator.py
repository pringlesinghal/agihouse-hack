from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def generate_personas(segments, product_details, client=None):
    """Generate detailed personas for each customer segment."""
    try:
        personas = {}
        
        # Split by first level brackets
        segments_list = segments.split('[')
        
        # Extract product description from the product details
        product_description = product_details.get('description', "the product")
        
        for segment in segments_list[1::2]:  # Skip empty first split
            try:
                # Get segment name from first bracket
                segment_name = segment.split(']')[0].strip()
                
                # Find the value proposition (text between the last set of square brackets)
                value_prop_start = segment.rfind('[')
                value_prop_end = segment.rfind(']')
                
                if value_prop_start != -1 and value_prop_end != -1:
                    value_proposition = segment[value_prop_start+1:value_prop_end].strip()
                else:
                    value_proposition = ""
                
                persona_prompt = f"""Create a concise but detailed persona for this customer segment:

Segment: {segment_name}
Value Proposition & Characteristics: {value_proposition}

Generate a rich persona that can be used as a prompt for an LLM to accurately simulate this customer segment. Include:

1. Personal Background:
   - Name, age, occupation aligned with segment demographics
   - Income level and financial priorities
   - Lifestyle and daily routine
   - Location and living situation

2. Psychological Profile:
   - Core values and beliefs
   - Key motivations and aspirations
   - Main pain points and challenges
   - Decision-making style
   - Technology adoption level

3. Shopping Behavior:
   - Research and evaluation process
   - Key decision factors when buying
   - Price sensitivity
   - Brand preferences and loyalty
   - Response to marketing

4. Product Expectations:
   - Must-have features
   - Quality expectations
   - Price-to-value relationship
   - Service expectations

Format the response as a second-person narrative that can be used as an LLM prompt, starting with:
"You are [name], a [age]-year-old [occupation]..."

Make the persona concise but authentic, focusing on the most important characteristics that define their buying behavior."""

                # Generate persona with grounding
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[persona_prompt],
                    config=GenerateContentConfig(
                        tools=[Tool(google_search=GoogleSearch())],
                        response_modalities=["TEXT"],
                    )
                )
                
                if not response.candidates:
                    personas[segment_name] = {
                        'persona': "Failed to generate persona",
                        'video_prompt': "Failed to generate video prompt"
                    }
                    continue

                personas[segment_name] = response.candidates[0].content.parts[0].text

                # Generate video ad prompt based on the persona and segment context
                video_prompt = f"""Create a concise 8-second video advertisement prompt targeting this customer segment. The prompt should start with:

"This is an advertisement for {product_description}"

Target Segment: {segment_name}
Key Value Proposition: {value_proposition}

Based on the customer profile:
{personas[segment_name]}

Generate a focused video prompt with:

1. Scene Sequence (8 seconds total):
   - Opening (2s): Set the scene and hook
   - Middle (4s): Show key benefit/feature
   - Closing (2s): Call to action

2. Style Elements:
   - Visual: Key imagery, colors, and mood for this demographic
   - Audio: Music style and voice tone
   - Product Integration: How to showcase the main benefit

Keep the prompt concise and impactful, focusing on the most important elements that will resonate with this customer segment."""

                # Generate video prompt with grounding
                video_response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[video_prompt],
                    config=GenerateContentConfig(
                        tools=[Tool(google_search=GoogleSearch())],
                        response_modalities=["TEXT"],
                    )
                )
                
                if video_response.candidates:
                    personas[segment_name] = {
                        'persona': personas[segment_name],
                        'video_prompt': video_response.candidates[0].content.parts[0].text
                    }
                else:
                    personas[segment_name] = {
                        'persona': personas[segment_name],
                        'video_prompt': "Failed to generate video prompt"
                    }

            except Exception as e:
                personas[segment_name] = {
                    'persona': f"Error generating persona: {str(e)}",
                    'video_prompt': "Error generating video prompt"
                }

        return personas, None

    except Exception as e:
        return None, f"Error generating personas: {str(e)}"
