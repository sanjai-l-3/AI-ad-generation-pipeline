from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
import os
from PIL import Image
from google import genai
from google.genai import types
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


class CharacterOutfitInfo(BaseModel):
    """Outfit information for characters"""
    outfit: str = Field(description="Name of the outfit in lowercase")
    outfit_description: str = Field(description="Detailed description of the outfit")
    image_path: Optional[str] = Field(default=None, description="Path to generated outfit image")


class FullOutfit(BaseModel):
    """Full outfit details for image generation"""
    outfit: str
    outfit_description: str
    image_path: Optional[str] = None


class OutfitGenerator:
    def __init__(self, output_dir: str = "outfit_images"):
        """
        Initialize Outfit Generator
        
        Args:
            output_dir: Directory to store generated outfit images
        """
        
        self.client = genai.Client()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_outfit_prompt(self, outfit: dict) -> str:
        """
        Create detailed prompt for outfit image generation
        
        Args:
            outfit: Dictionary with 'outfit' (name) and 'outfit_description'
        """
        outfit_name = outfit.get('outfit', 'Outfit')
        description = outfit.get('outfit_description', '')
        
        prompt = f"""
Create a highly realistic, professional photograph of a complete outfit on a white background.

OUTFIT NAME: {outfit_name}

OUTFIT DETAILS:
{description}

PHOTOGRAPHY REQUIREMENTS:
- Style: Professional fashion photography, catalog-style
- Layout: Full outfit displayed flat lay OR on invisible mannequin
- Background: Pure white, clean, no shadows
- Lighting: Even, soft studio lighting from multiple angles
- Focus: Crystal clear, every detail visible
- Perspective: Straight-on, front view
- Quality: High resolution, commercial photography standard
- Context: Ready-to-wear presentation

OUTFIT PRESENTATION:
- All clothing items arranged neatly and proportionally
- Natural fabric drape and texture visible
- Colors accurate and vibrant
- Accessories positioned appropriately
- Professional styling that shows how items work together

IMPORTANT:
- NO human model, just the outfit itself
- Clean presentation suitable for e-commerce or fashion catalog
- Show the complete outfit as described
- Maintain realistic fabric textures and colors
- Indian fashion aesthetic where applicable

Create a clean, professional outfit photograph suitable for commercial use.
"""
        return prompt.strip()
    
    def generate_image(self, prompt: str, outfit_id: str) -> Optional[str]:
        """
        Generate outfit image using Gemini
        
        Args:
            prompt: Detailed prompt for image generation
            outfit_id: Unique identifier for the outfit
            
        Returns:
            File path to generated image or None if failed
        """
        try:
            print(f"🎨 Generating outfit image for {outfit_id} using Gemini...")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt,
                config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                )
            )
            )
            
            image_saved = False
            filename = f"{outfit_id}_outfit.png"
            filepath = os.path.join(self.output_dir, filename)
            
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        image.save(filepath)
                        image_saved = True
                        print(f"✓ Saved outfit image: {filepath}")
                        break
                    elif hasattr(part, 'text') and part.text:
                        print(f"📝 Gemini response: {part.text[:100]}...")
            
            if not image_saved:
                print(f"⚠ No image data generated for {outfit_id}")
                return None
                
            return filepath
            
        except Exception as e:
            print(f"✗ Error generating outfit image for {outfit_id}: {e}")
            return None
    
    def create_placeholder_image(self, outfit_id: str, outfit_name: str) -> str:
        """Create a placeholder image when AI generation fails"""
        try:
            filename = f"{outfit_id}_outfit.png"
            filepath = os.path.join(self.output_dir, filename)
            
            img = Image.new('RGB', (600, 800), color='lightgray')
            
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                text = f"{outfit_name}\n(Outfit Placeholder)"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (600 - text_width) // 2
                y = (800 - text_height) // 2
                
                draw.text((x, y), text, fill='black', font=font)
            except:
                pass
            
            img.save(filepath)
            print(f"✓ Created placeholder image: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"✗ Error creating placeholder: {e}")
            return None
    
    def generate_outfit_image(self, outfit: FullOutfit, outfit_id: str = None) -> FullOutfit:
        """
        Generate image for a single outfit
        
        Args:
            outfit: FullOutfit object
            outfit_id: Optional custom outfit ID
            
        Returns:
            FullOutfit object with image_path populated
        """
        if not outfit_id:
            outfit_id = outfit.outfit.lower().replace(' ', '_')
        
        print(f"\nGenerating image for outfit: {outfit.outfit} ({outfit_id})")
        
        outfit_dict = outfit.model_dump()
        
        # Generate outfit image
        outfit_prompt = self.create_outfit_prompt(outfit_dict)
        print(f"Outfit prompt preview: {outfit_prompt[:150]}...")
        outfit_image_path = self.generate_image(outfit_prompt, outfit_id)
        
        if not outfit_image_path:
            print(f"Trying simpler prompt for {outfit.outfit}...")
            simple_prompt = f"Professional catalog photograph of {outfit.outfit}, flat lay on white background, realistic, high quality"
            outfit_image_path = self.generate_image(simple_prompt, outfit_id)
        
        if not outfit_image_path:
            print(f"Creating placeholder for {outfit.outfit}...")
            outfit_image_path = self.create_placeholder_image(outfit_id, outfit.outfit)
        
        # Update outfit with image path
        outfit_dict['image_path'] = outfit_image_path
        outfit_with_image = FullOutfit(**outfit_dict)
        
        return outfit_with_image
    
    def generate_images_for_all_outfits(self, outfits: List[FullOutfit]) -> List[FullOutfit]:
        """
        Generate images for all outfits
        
        Args:
            outfits: List of FullOutfit objects
            
        Returns:
            List of FullOutfit objects with image_path populated
        """
        outfits_with_images = []
        
        print(f"\n{'='*80}")
        print(f"Starting image generation for {len(outfits)} outfits...")
        print(f"{'='*80}\n")
        
        for i, outfit in enumerate(outfits, 1):
            print(f"\n--- Outfit {i}/{len(outfits)} ---")
            outfit_id = f"outfit_{i:03d}_{outfit.outfit.lower().replace(' ', '_')}"
            outfit_with_image = self.generate_outfit_image(outfit, outfit_id)
            outfits_with_images.append(outfit_with_image)
        
        print(f"\n{'='*80}")
        print(f"✓ Image generation complete for all outfits!")
        print(f"{'='*80}\n")
        
        return outfits_with_images
    
    def save_outfits_with_images(self, outfits: List[FullOutfit], filename: str):
        """
        Save outfits with image paths to JSON file
        
        Args:
            outfits: List of FullOutfit objects
            filename: Output JSON filename
        """
        outfits_dict = {
            "outfits": [outfit.model_dump() for outfit in outfits],
            "total_outfits": len(outfits)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(outfits_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Outfits with image paths saved to {filename}")
    
    def display_outfits_summary(self, outfits: List[FullOutfit]):
        """Display summary of outfits"""
        print("\n" + "="*100)
        print("OUTFITS SUMMARY")
        print("="*100 + "\n")
        
        for idx, outfit in enumerate(outfits, 1):
            print(f"\n--- Outfit {idx}: {outfit.outfit.upper()} ---")
            print(f"Description: {outfit.outfit_description[:150]}..." if len(outfit.outfit_description) > 150 else f"Description: {outfit.outfit_description}")
            if outfit.image_path:
                print(f"Image: {outfit.image_path}")
            print("-" * 100)