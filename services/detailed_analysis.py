from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from PIL import Image
from io import BytesIO

def get_detailed_analysis(image_data=None, text_input=None, client=None):
    """Generate detailed product and market analysis."""
    try:
        detailed_prompt = """Analyze the provided product information and identify the customer segments with the highest revenue potential. 
        
Follow these steps in your analysis, ensuring all numbers and statistics are grounded in real-world market data:

1. Product Understanding:
   - Analyze the visual elements, features, and quality level from the image/description
   - Identify key product attributes and value propositions
   - Research and estimate a realistic price point based on:
     * Similar products in the market
     * Quality level and features
     * Target market positioning
     * Current market pricing trends

2. Market Size Analysis:
   - Research the total addressable market (TAM) using verifiable industry data
   - Consider:
     * Published market research reports
     * Industry association statistics
     * Public company financial reports
     * Government economic data
   - Document market growth trends with specific year-over-year rates
   - Cross-reference multiple sources to validate market size estimates

3. Customer Segmentation with Revenue Potential:
   - For each potential customer segment, provide realistic estimates backed by data:
     * Average purchase value (benchmark against actual market prices)
     * Purchase frequency based on typical consumer behavior
     * Segment size validated against demographic data
     * Total potential annual revenue calculated conservatively
   - Support each estimate with:
     * Reference to similar products/markets
     * Industry benchmarks
     * Consumer spending patterns
     * Market penetration rates
   - Calculate percentage contribution to total revenue
   - Only retain segments that fall in the top 80% of cumulative revenue

4. Market Penetration Factors:
   - Research actual customer acquisition costs in similar markets
   - Analyze competitive landscape with specific examples
   - Consider realistic barriers to entry
   - Factor in market saturation levels

Guidelines for Revenue Estimates:
- Always err on the conservative side
- Cross-reference numbers with industry benchmarks
- Consider economic factors and purchasing power
- Account for seasonal variations if applicable
- Factor in market maturity and adoption rates
- Consider regional differences in pricing and demand

Provide a detailed analysis following these steps, with specific focus on realistic and well-researched revenue calculations."""

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
            return None, "Please provide either an image or text description"

        # Get detailed analysis with grounding
        detailed_response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=content,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                response_modalities=["TEXT"],
            )
        )
        
        if not detailed_response.candidates:
            return None, "Failed to generate analysis"

        return detailed_response.candidates[0].content.parts[0].text, None

    except Exception as e:
        return None, f"Error in detailed analysis: {str(e)}"
