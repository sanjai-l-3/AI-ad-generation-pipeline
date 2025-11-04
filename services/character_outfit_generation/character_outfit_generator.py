

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from PIL import Image
from google import genai
from google.genai import types
from io import BytesIO
from dotenv import load_dotenv
import json


load_dotenv()


class CharacterOutfitImage(BaseModel):
    """Character with specific outfit image"""
    character_name: str = Field(description="Character name (lowercase)")
    outfit_name: str = Field(description="Outfit name (lowercase)")
    combined_id: str = Field(description="Unique ID: character_outfit")
    image_path: Optional[str] = None


class CharacterOutfitGenerator:
    """Generate character images wearing specific outfits"""
    
    def __init__(self, output_dir: str = "character_outfit_images"):
        
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_character_outfit_prompt(
        self,
        character_image_path: str,
        outfit_description: str,
        character_name: str,
        outfit_name: str
    ) -> str:
        """
        Create prompt for generating character in specific outfit
        
        Args:
            character_image_path: Path to base character reference image
            outfit_description: Detailed outfit description
            character_name: Character name
            outfit_name: Outfit name
        """
        prompt = f"""
Generate a full-body image of {character_name} wearing the specified outfit on a clean white background.

CRITICAL REQUIREMENTS:

1. **Character Consistency** (MOST IMPORTANT):
   - Use the reference image to maintain EXACT facial features
   - Keep the same face, skin tone, hair style, and hair color
   - Maintain the same body type and proportions
   - Keep facial structure, eyes, nose, mouth, and all features identical
   - DO NOT change the person's appearance - only change the outfit

2. **Outfit Details**:
{outfit_description}

3. **Pose and Framing**:
   - Full body view (head to toe visible)
   - Standing straight, front-facing
   - Arms naturally at sides or slightly away from body
   - Neutral, pleasant expression
   - Direct eye contact with camera
   - Professional portrait pose

4. **Background**:
   - Pure white background (#FFFFFF)
   - No shadows, no gradients
   - Clean and simple
   - Professional studio photography style

5. **Lighting**:
   - Soft, even studio lighting
   - No harsh shadows
   - Well-lit to show outfit details clearly
   - Natural skin tones

6. **Photography Style**:
   - High resolution, professional quality
   - Sharp focus on entire body and outfit
   - Suitable for e-commerce or catalog use
   - Realistic, not illustrated or cartoon-like

IMPORTANT: The face and body must match the reference image EXACTLY. Only the clothing should change.

Create a professional full-body portrait of {character_name} in the outfit described above.
"""
        return prompt.strip()
    
    def generate_character_in_outfit(
        self,
        character_image_path: str,
        character_info: Dict[str, Any],
        outfit_info: Dict[str, Any]
    ) -> Optional[CharacterOutfitImage]:
        """
        Generate character wearing specific outfit
        
        Args:
            character_image_path: Path to character reference image
            character_info: Character information dict
            outfit_info: Outfit information dict
            
        Returns:
            CharacterOutfitImage with generated image path
        """
        character_name = character_info.get('name', 'character').lower()
        outfit_name = outfit_info.get('outfit', 'outfit').lower()
        outfit_description = outfit_info.get('outfit_description', '')
        
        combined_id = f"{character_name}_{outfit_name}"
        
        print(f"\n🎨 Generating {character_name} in {outfit_name}")
        print(f"   Character ref: {character_image_path}")
        
        try:
            # Load character reference image
            if not os.path.exists(character_image_path):
                print(f"   ❌ Character image not found: {character_image_path}")
                return None
            
            char_image = Image.open(character_image_path)
            
            # Create prompt
            prompt = self.create_character_outfit_prompt(
                character_image_path=character_image_path,
                outfit_description=outfit_description,
                character_name=character_name,
                outfit_name=outfit_name
            )
            
            print(f"   📝 Prompt: {prompt[:100]}...")
            
            # Generate image with character reference
            contents = [prompt, char_image]
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
                config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                )
                )
            )
            
            # Save generated image
            filename = f"{combined_id}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image_saved = False
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        image.save(filepath)
                        image_saved = True
                        print(f"   ✅ Saved: {filepath}")
                        break
            
            if not image_saved:
                print(f"   ❌ No image generated")
                return None
            
            return CharacterOutfitImage(
                character_name=character_name,
                outfit_name=outfit_name,
                combined_id=combined_id,
                image_path=filepath
            )
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def generate_all_character_outfits(
        self,
        characters_info: List[Dict[str, Any]],
        outfits_info: List[Dict[str, Any]],
        shots_info: List[Dict[str, Any]]
    ) -> List[CharacterOutfitImage]:
        """
        Generate all unique character-outfit combinations needed
        
        Args:
            characters_info: List of character information
            outfits_info: List of outfit information
            shots_info: List of shot information
            
        Returns:
            List of CharacterOutfitImage objects
        """
        print("\n" + "="*100)
        print("GENERATING CHARACTER-OUTFIT COMBINATIONS")
        print("="*100 + "\n")
        
        # Collect unique character-outfit pairs from all shots
        required_combinations = set()
        
        for shot in shots_info:
            outfit_mappings = shot.get('outfit_character_mapping', [])
            for mapping in outfit_mappings:
                char_name = mapping.get('character_name', '').lower()
                outfit_name = mapping.get('outfit_name', '').lower()
                if char_name and outfit_name:
                    required_combinations.add((char_name, outfit_name))
        
        print(f"📋 Found {len(required_combinations)} unique character-outfit combinations\n")
        
        # Create lookups
        char_lookup = {char['name'].lower(): char for char in characters_info}
        outfit_lookup = {outfit['outfit'].lower(): outfit for outfit in outfits_info}
        
        generated_images = []
        
        for char_name, outfit_name in sorted(required_combinations):
            print(f"{'─'*80}")
            
            # Get character info
            char_info = char_lookup.get(char_name)
            if not char_info:
                print(f"⚠️  Character '{char_name}' not found")
                continue
            
            # Get outfit info
            outfit_info = outfit_lookup.get(outfit_name)
            if not outfit_info:
                print(f"⚠️  Outfit '{outfit_name}' not found")
                continue
            
            # Get character image path
            char_image_path = char_info.get('image_path')
            if not char_image_path:
                print(f"⚠️  No image path for character '{char_name}'")
                continue
            
            # Generate character in outfit
            result = self.generate_character_in_outfit(
                character_image_path=char_image_path,
                character_info=char_info,
                outfit_info=outfit_info
            )
            
            if result:
                generated_images.append(result)
        
        print("\n" + "="*100)
        print(f"✅ Generated {len(generated_images)}/{len(required_combinations)} character-outfit images")
        print("="*100 + "\n")
        
        return generated_images
    
    def save_character_outfit_mapping(
        self,
        character_outfits: List[CharacterOutfitImage],
        filename: str,
        output_dir: str = "projects_data"
    ):
        """Save character-outfit mapping to JSON"""
        mapping_dict = {
            "character_outfits": [co.model_dump() for co in character_outfits],
            "total_combinations": len(character_outfits)
        }
        
        file_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Character-outfit mapping saved to {file_path}")
        return file_path