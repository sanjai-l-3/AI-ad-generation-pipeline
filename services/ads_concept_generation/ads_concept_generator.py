from typing import List, Optional, Dict, Any
from utils.llm import get_llm_model
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv


load_dotenv()

llm_client = get_llm_model("gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


class AdConcept(BaseModel):
    """Individual Ad Concept with all required fields"""
    title: str = Field(description="Catchy title for the ad concept")
    one_line_summary: str = Field(description="Brief one-line summary of the ad concept")
    story: str = Field(description="Detailed narrative of the ad in paragraph form")
    visual_flow:str = Field(
        description="Dictionary containing visual sequences like Opening, Sequence, Location scenes, Close-up, etc."
    )
    tagline: str = Field(description="Memorable tagline for the ad")
    key_message: str = Field(description="Core message the ad conveys")
    key_features: List[str] = Field(description="List of product features highlighted in the ad")
    tone: str = Field(description="Tone of the ad (e.g., inspirational, humorous, emotional)")


class AdConceptsResponse(BaseModel):
    """Collection of ad concepts"""
    concepts: List[AdConcept] = Field(description="List of generated ad concepts")


class AdConceptGenerator:
    def __init__(self):
        self.llm = llm_client
        
    def create_ad_concepts_system_prompt(self, brand_info: Dict[str, Any]) -> str:
        """Create system prompt for generating ad concepts"""
        return f"""You are an expert creative director specializing in advertisement concept creation.

Your task is to generate compelling ad concepts based on brand information provided.

Each ad concept MUST include:
1. **Title**: A catchy, memorable title
2. **One-Line Summary**: Brief encapsulation of the concept
3. **Story**: Detailed narrative in paragraph form (5-6 sentences) breifly describing the overall ads concept
4. **Visual Flow**: Key visual sequences broken down as:
   - Opening: Initial scene/shot
   - Sequence: Main action sequences
   - Additional scenes: Location-specific shots
   - Close-up: Important detail shots

5. **Tagline**: Memorable brand tagline
6. **Key Message**: Core message/value proposition
7. **Key Features**: Product features to highlight (list)
8. **Tone**: Overall tone of the ad


Guidelines for Concept Creation

    -Think AI-first: Scenes should be visually descriptive, easy to generate, and not overcrowded. 
    -Create a minimal script do not involve complex actions ,some thing like in hotel room avoid complex location
    -Concepts must feel:
    -Authentic to brand voice & values
    -Emotionally relatable
    -Visually engaging
    -Clear in messaging
    -Every Ad you generate should have only 1 or 2 characters not more than that this is Important
    -Do NOT mention any celebrities.
    -Keep characters relatable (e.g., “young player”, “friend”, “student”, “traveler”, etc.)
    -Vary each concept with different themes, moods, and story angles.
    -Use theme based ad only if Brand ask

Example of Theme-Based Ad Concepts this is for IPL (Do NOT copy, use only for structural reference)

CONCEPT EXAMPLE: "The Stadium Sunburn Story"
One-Line Summary: Two friends at a cricket match—one forgot sunscreen and suffers, the other protected and enjoying.
Visual Flow:
Opening – Two friends excited, entering the stadium
Main Sequence – One applies sunscreen, the other doesn’t
Additional Scene – Sun becomes harsh, one struggles, the other stays comfortable
Close-Up – Subtle glow and product texture
Tagline – “Stay ready. Stay protected.”
and other Information

Example of Other ads:


Create concepts that are:
- Visually compelling and easy to execute
- Authentic to the brand's voice and values
- Emotionally resonant with the target audience
- Clear in their messaging
- Diverse in approach (different angles, tones, scenarios)

Brand Information:
{json.dumps(brand_info, indent=2)}

Generate creative, diverse concepts that showcase different angles and emotional appeals while staying true to the brand."""

    def generate_ad_concepts(
        self, 
        brand_info: Dict[str, Any], 
        num_concepts: int = 5,
        duration:int=15
    ) -> List[AdConcept]:
        """
        Generate multiple ad concepts based on brand information
        
        Args:
            brand_info: Dictionary containing brand details like:
                - brand_name: str
                - product_name: str
                - product_description: str
                - target_audience: str
                - key_features: List[str]
                - brand_values: List[str]
                - tone_preferences: str
                - campaign_objective: str
                - celebrity_endorser: Optional[str]
                - reference_style: Optional[str]
            num_concepts: Number of ad concepts to generate (default 5)
            
        Returns:
            List of AdConcept objects
        """
        system_prompt = self.create_ad_concepts_system_prompt(brand_info)
        
        user_prompt = f"""Generate {num_concepts} diverse ad concepts for this brand with duration of {duration} sec.

Each concept should take a different creative approach adpting to brand and the sector

Ensure each concept is complete with all required fields and ready for production consideration.

Return the response in valid JSON format matching the AdConceptsResponse schema."""

        try:
            messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
            ]
            self.llm=self.llm.with_structured_output(AdConceptsResponse)
            ad_concepts_response = self.llm.invoke(messages)

            
            print(f"✓ Successfully generated {len(ad_concepts_response.concepts)} ad concepts")
            return ad_concepts_response.concepts
            
        except Exception as e:
            print(f"Error generating ad concepts: {str(e)}")
            raise

    def save_ad_concepts(
        self, 
        ad_concepts: List[AdConcept], 
        output_file: str, 
        output_dir: str = "projects_data"
    ):
        """Save ad concepts to JSON file"""
        concepts_dict = {
            "ad_concepts": [concept.model_dump() for concept in ad_concepts],
            "total_concepts": len(ad_concepts)
        }
        
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(concepts_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Ad concepts saved to {file_path}")
        return file_path

    def load_ad_concepts(self, file_path: str) -> List[AdConcept]:
        """Load ad concepts from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [AdConcept(**concept) for concept in data['ad_concepts']]

    def display_concepts_summary(self, ad_concepts: List[AdConcept]):
        """Display a summary of generated concepts"""
        print("\n" + "="*80)
        print("GENERATED AD CONCEPTS SUMMARY")
        print("="*80 + "\n")
        
        for idx, concept in enumerate(ad_concepts, 1):
            print(f"\n--- Concept {idx}: {concept.title} ---")
            print(f"Summary: {concept.one_line_summary}")
            print(f"Tone: {concept.tone}")
            print(f"Key Message: {concept.key_message}")
            print(f"Tagline: {concept.tagline}")
            print(f"Story of the Ad {concept.story}")
            print(f"Visual Flow {concept.visual_flow}")
            print("-" * 80)



# if __name__ == "__main__":
#     # Example brand information
#     brand_info = {
#         "brand_name": "Deconstruct",
#         "product_name": "Gel Sunscreen SPF 55",
#         "product_description": "Lightweight, matte finish sunscreen with high SPF protection",
#         "target_audience": "Active individuals, sports enthusiasts, ages 25-45",
#         "key_features": [
#             "SPF 55 protection",
#             "Matte finish - no white cast",
#             "Sweat-resistant",
#             "Non-greasy formula",
#             "Suitable for all skin types"
#         ],
#         "brand_values": ["Performance", "Quality", "Trust", "Innovation"],
#         "tone_preferences": "Confident, aspirational, authentic",
#         "campaign_objective": "Increase brand awareness and position as premium sunscreen choice",
#         "celebrity_endorser": "MS Dhoni",
#         "reference_style": "Documentary-style, authentic moments"
#     }
    
#     # Initialize generator
#     generator = AdConceptGenerator()
    
#     # Generate concepts
#     concepts = generator.generate_ad_concepts(brand_info, num_concepts=4, duration=15)
    
#     # Display summary
#     generator.display_concepts_summary(concepts)
    
#     # Save to file
#     generator.save_ad_concepts(concepts, "ad_concepts_deconstruct.json")