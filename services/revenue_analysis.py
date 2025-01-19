from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def get_revenue_segments(detailed_analysis, client=None):
    """Extract high-revenue customer segments from detailed analysis."""
    try:
        summary_prompt = """Extract and analyze the customer segments that contribute to the top 80% of total revenue potential.

For each segment, provide realistic and well-researched metrics:

1. Segment Name/Title (be specific about the demographic)

2. Revenue Metrics (all numbers must be justified):
   - Average Purchase Value:
     * Base this on actual market prices
     * Consider regional variations
     * Account for typical discounts/promotions
   
   - Annual Purchase Frequency:
     * Use realistic consumer behavior patterns
     * Consider product lifecycle
     * Account for seasonal variations
   
   - Segment Size:
     * Base on demographic data
     * Consider market penetration rates
     * Account for geographic limitations
   
   - Total Annual Revenue Potential:
     * Calculate conservatively
     * Show clear multiplication steps
     * Round down for safety

3. Value Proposition:
   - Clear rationale for revenue estimates
   - Specific pain points addressed
   - Competitive advantages
   - Market positioning

Format each segment EXACTLY as follows, with NO introductory text:
[Segment Name - Primary Demographic]
Revenue Potential: $X million/year (show calculation)
- Avg Purchase: $X (reference similar products)
- Frequency: X purchases/year (justify with behavior patterns)
- Segment Size: X customers (cite demographic data)
[Three-line description including:
 - Value proposition
 - Revenue justification
 - Market positioning]

[Next Segment]
...etc.

Important:
- Order segments by revenue potential (highest to lowest)
- Only include segments that together make up 80% of total revenue
- Do NOT include any introductory text or summary before the segments
- Start DIRECTLY with the first segment in [brackets]
- Ensure all numbers are realistic and conservative

Here's the analysis:
""" + detailed_analysis

        # Get summary with grounding
        summary_response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[summary_prompt],
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                response_modalities=["TEXT"],
            )
        )
        
        if not summary_response.candidates:
            return None, "Failed to generate revenue segments"

        # Get grounding metadata for debugging (optional)
        grounding_data = None
        try:
            grounding_data = summary_response.candidates[0].grounding_metadata.search_entry_point.rendered_content
        except:
            pass

        return {
            "segments": summary_response.candidates[0].content.parts[0].text,
            "grounding_data": grounding_data
        }, None

    except Exception as e:
        return None, f"Error in revenue analysis: {str(e)}"
