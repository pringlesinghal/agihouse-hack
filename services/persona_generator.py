from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def generate_personas(segments, client=None):
    """Generate detailed personas for each customer segment."""
    try:
        personas = {}
        
        # Split by first level brackets
        segments_list = segments.split('[')
        
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
                    personas[segment_name] = "Failed to generate persona"
                    continue

                personas[segment_name] = response.candidates[0].content.parts[0].text

            except Exception as e:
                personas[segment_name] = f"Error generating persona: {str(e)}"

        return personas, None

    except Exception as e:
        return None, f"Error generating personas: {str(e)}"
