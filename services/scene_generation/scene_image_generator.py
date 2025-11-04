from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types
from io import BytesIO
import time


load_dotenv()


class SceneImageGenerator:
    def __init__(self, output_dir: str = "scene_images"):
        """
        Initialize Scene Image Generator
        
        Args:
            output_dir: Directory to store generated scene images
        """
        self.client = genai.Client()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.generation_progress = {
            "total_shots": 0,
            "generated_images": {},
            "failed_generations": []
        }
    
    def load_reference_images(
        self, 
        character_refs: List[Dict], 
        location_ref: Optional[Dict],
        product_ref: Optional[Dict] = None
    ) -> tuple:
        """
        Load reference images for characters, location, and product
        
        Args:
            character_refs: List of character reference dicts with 'name' and 'image_path'
            location_ref: Location reference dict with 'name' and 'image_path'
            product_ref: Product reference dict with 'name' and 'image_path'
            
        Returns:
            Tuple of (prepared_char_refs, prepared_location_ref, prepared_product_ref)
        """
        prepared_char_refs = []
        prepared_location_ref = None
        prepared_product_ref = None
        
        # Load character images
        for char_ref in character_refs:
            char_name = char_ref.get('name', 'unknown')
            char_image_path = char_ref.get('image_path')
            
            if char_image_path and os.path.exists(char_image_path):
                try:
                    loaded_image = Image.open(char_image_path)
                    prepared_char_refs.append({
                        'character_name': char_name,
                        'loaded_image': loaded_image,
                        'image_path': char_image_path
                    })
                    print(f"  ✓ Loaded character image: {char_name}")
                except Exception as e:
                    print(f"  ✗ Failed to load character image {char_name}: {e}")
            else:
                print(f"  ⚠ Character image not found: {char_name}")
        
        # Load location image
        if location_ref:
            loc_name = location_ref.get('name', 'unknown')
            loc_image_path = location_ref.get('image_path')
            
            if loc_image_path and os.path.exists(loc_image_path):
                try:
                    loaded_image = Image.open(loc_image_path)
                    prepared_location_ref = {
                        'location_name': loc_name,
                        'loaded_image': loaded_image,
                        'image_path': loc_image_path
                    }
                    print(f"  ✓ Loaded location image: {loc_name}")
                except Exception as e:
                    print(f"  ✗ Failed to load location image {loc_name}: {e}")
            else:
                print(f"  ⚠ Location image not found: {loc_name}")
        
        # Load product image
        if product_ref:
            prod_name = product_ref.get('name', 'product')
            prod_image_path = product_ref.get('image_path')
            
            if prod_image_path and os.path.exists(prod_image_path):
                try:
                    loaded_image = Image.open(prod_image_path)
                    prepared_product_ref = {
                        'product_name': prod_name,
                        'loaded_image': loaded_image,
                        'image_path': prod_image_path
                    }
                    print(f"  ✓ Loaded product image: {prod_name}")
                except Exception as e:
                    print(f"  ✗ Failed to load product image {prod_name}: {e}")
            else:
                print(f"  ⚠ Product image not found: {prod_name}")
        
        return prepared_char_refs, prepared_location_ref, prepared_product_ref
    
    def generate_scene_image(
    self,
    shot: Dict[str, Any],
    image_prompt: str,
    character_outfit_refs: List[Dict],  # NEW: Character-outfit combination images
    location_ref: Optional[Dict],
    product_ref: Optional[Dict],
    aspect_ratio: str = "16:9",
    project_id: str = "project"
) -> Optional[str]:
        """Generate scene image with character-outfit combination references"""
        
        shot_no = shot.get('shot_no', 'unknown')
        
        print(f"\n{'─'*80}")
        print(f"🎨 Generating scene image for Shot {shot_no}")
        print(f"{'─'*80}")
        
        try:
            # Load reference images
            print("📂 Loading reference images...")
            
            # NEW: Load character-outfit images
            prepared_char_outfit_refs = []
            if character_outfit_refs:
                for co_ref in character_outfit_refs:
                    co_image_path = co_ref.get('image_path')
                    combined_id = co_ref.get('combined_id')
                    
                    if co_image_path and os.path.exists(co_image_path):
                        try:
                            loaded_image = Image.open(co_image_path)
                            prepared_char_outfit_refs.append({
                                'combined_id': combined_id,
                                'character_name': co_ref.get('character_name'),
                                'outfit_name': co_ref.get('outfit_name'),
                                'loaded_image': loaded_image,
                                'image_path': co_image_path
                            })
                            print(f"  ✅ Loaded character-outfit: {combined_id}")
                        except Exception as e:
                            print(f"  ❌ Failed to load: {combined_id} - {e}")
            
            # Load location reference
            prepared_location_ref = None
            if location_ref:
                loc_image_path = location_ref.get('image_path')
                if loc_image_path and os.path.exists(loc_image_path):
                    try:
                        loaded_image = Image.open(loc_image_path)
                        prepared_location_ref = {
                            'location_name': location_ref.get('name'),
                            'loaded_image': loaded_image
                        }
                        print(f"  ✅ Loaded location: {location_ref.get('name')}")
                    except Exception as e:
                        print(f"  ❌ Failed to load location: {e}")
            
            # Load product reference
            prepared_product_ref = None
            if product_ref:
                prod_image_path = product_ref.get('image_path')
                if prod_image_path and os.path.exists(prod_image_path):
                    try:
                        loaded_image = Image.open(prod_image_path)
                        prepared_product_ref = {
                            'product_name': product_ref.get('name'),
                            'loaded_image': loaded_image
                        }
                        print(f"  ✅ Loaded product: {product_ref.get('name')}")
                    except Exception as e:
                        print(f"  ❌ Failed to load product: {e}")
            
            # Create enhanced prompt
            enhanced_prompt = self.create_enhanced_prompt_with_char_outfit(
                base_prompt=image_prompt,
                aspect_ratio=aspect_ratio,
                character_outfit_refs=prepared_char_outfit_refs,  # NEW
                location_ref=prepared_location_ref,
                product_ref=prepared_product_ref
            )
            
            # Prepare content for Gemini
            contents = [enhanced_prompt]
            
            # Add character-outfit reference images
            for co_ref in prepared_char_outfit_refs:
                if co_ref.get('loaded_image'):
                    contents.append(co_ref['loaded_image'])
                    print(f"  👤 Added reference: {co_ref['combined_id']}")
            
            # Add location reference
            if prepared_location_ref and prepared_location_ref.get('loaded_image'):
                contents.append(prepared_location_ref['loaded_image'])
                print(f"  🏢 Added location reference")
            
            # Add product reference
            if prepared_product_ref and prepared_product_ref.get('loaded_image'):
                contents.append(prepared_product_ref['loaded_image'])
                print(f"  📦 Added product reference")
            
            print(f"\n🎨 Generating with {len(contents)} items (1 prompt + {len(contents)-1} references)")
            
            # Generate image
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
            filename = f"{project_id}_shot_{shot_no:03d}_scene.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image_saved = False
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        image.save(filepath)
                        image_saved = True
                        print(f"✅ Saved scene image: {filepath}")
                        break
            
            if not image_saved:
                print(f"❌ No image data generated")
                return None
            
            # Update progress
            self.generation_progress["generated_images"][f"shot_{shot_no}"] = {
                "filepath": filepath,
                "shot_no": shot_no,
                "status": "success"
            }
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.generation_progress["failed_generations"].append({
                "shot_no": shot_no,
                "error": str(e)
            })
            return None

    def generate_single_scene_image_with_prompt(
        self,
        shot: Dict[str, Any],
        custom_prompt: str,
        character_outfit_refs: List[Dict],
        location_ref: Optional[Dict],
        product_ref: Optional[Dict],
        aspect_ratio: str = "16:9",
        project_id: str = "project"
    ) -> Optional[str]:
        """
        Generate a single scene image with custom prompt
        
        Args:
            shot: Shot dictionary
            custom_prompt: Custom prompt to use instead of default
            character_outfit_refs: Character-outfit combination references
            location_ref: Location reference
            product_ref: Product reference
            aspect_ratio: Aspect ratio for the image
            project_id: Project ID
            
        Returns:
            File path to generated image or None if failed
        """
        # Use the standard generate_scene_image but with custom prompt
        return self.generate_scene_image(
            shot=shot,
            image_prompt=custom_prompt,  # Use custom prompt instead of shot's prompt
            character_outfit_refs=character_outfit_refs,
            location_ref=location_ref,
            product_ref=product_ref,
            aspect_ratio=aspect_ratio,
            project_id=project_id
        )

    def create_enhanced_prompt_with_char_outfit(
    self,
    base_prompt: str,
    aspect_ratio: str,
    character_outfit_refs: List[Dict],
    location_ref: Optional[Dict],
    product_ref: Optional[Dict]
) -> str:
        """Create enhanced prompt with character-outfit references"""
        
        enhanced_prompt = f"""
    ASPECT RATIO: {aspect_ratio}

    REFERENCE IMAGES PROVIDED:
    """
        
        # Character-outfit references
        if character_outfit_refs:
            enhanced_prompt += f"\nCHARACTER-OUTFIT REFERENCES ({len(character_outfit_refs)} provided):\n"
            for idx, co_ref in enumerate(character_outfit_refs, 1):
                char_name = co_ref.get('character_name', 'Character')
                outfit_name = co_ref.get('outfit_name', 'outfit')
                enhanced_prompt += f"- Reference {idx}: {char_name} wearing {outfit_name}\n"
                enhanced_prompt += f"  **Use this image to maintain EXACT facial features and outfit consistency**\n"
                enhanced_prompt += f"  Keep face, skin tone, hair, body type, AND outfit identical to this reference\n"
        
        # Location reference
        if location_ref:
            loc_name = location_ref.get('location_name', 'Location')
            enhanced_prompt += f"\nLOCATION REFERENCE: {loc_name}\n"
            enhanced_prompt += f"- Match the environment, atmosphere, and spatial layout from this reference\n"
        
        # Product reference
        if product_ref:
            prod_name = product_ref.get('product_name', 'Product')
            enhanced_prompt += f"\nPRODUCT REFERENCE: {prod_name}\n"
            enhanced_prompt += f"- Match product appearance and packaging from this reference\n"
        
        enhanced_prompt += f"""

    SCENE DESCRIPTION:
    {base_prompt}

    CRITICAL INSTRUCTIONS:
    1. **Character Consistency**: Use the character-outfit reference images to maintain EXACT facial features and outfit
    - Face, skin tone, hair style must match the reference EXACTLY
    - Outfit must match the reference EXACTLY (already worn in reference)
    - Do NOT change anything about the character's appearance
    
    2. **Location**: Match the environment from location reference image

    3. **Product**: If present, match from product reference image

    4. **Composition**: Integrate all elements naturally into the scene described

    5. **Aspect Ratio**: Maintain {aspect_ratio}

    6. **Quality**: Cinematic, commercial-grade photography

    MOST IMPORTANT: Characters must look IDENTICAL to their reference images (face AND outfit already correct in reference).
    """
        
        return enhanced_prompt

    def validate_shot_mapping(
    self,
    shot: Dict[str, Any],
    char_lookup: Dict[str, Any],
    loc_lookup: Dict[str, Any],
    outfit_lookup: Dict[str, Any]
) -> Dict[str, List[str]]:
        """
        Validate that all references in the shot can be found in lookups
        
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        
        shot_no = shot.get('shot_no', 'unknown')
        
        # Validate characters
        for char_name in shot.get('characters_involved', []):
            if char_name.lower() not in char_lookup:
                errors.append(f"Shot {shot_no}: Character '{char_name}' not found in character lookup")
        
        # Validate location
        if hasattr(shot, 'location_name') and shot.get('location_name'):
            if shot['location_name'].lower() not in loc_lookup:
                errors.append(f"Shot {shot_no}: Location '{shot['location_name']}' not found in location lookup")
        else:
            warnings.append(f"Shot {shot_no}: No location_name field, will use fuzzy matching")
        
        # Validate outfit mappings
        if shot.get('outfit_character_mapping'):
            for mapping in shot['outfit_character_mapping']:
                char_name = mapping.get('character_name', '').lower()
                outfit_name = mapping.get('outfit_name', '').lower()
                
                # Check character exists
                if char_name not in [c.lower() for c in shot.get('characters_involved', [])]:
                    errors.append(f"Shot {shot_no}: Outfit mapping for '{char_name}' but character not in shot")
                
                # Check outfit exists
                if outfit_name not in outfit_lookup:
                    errors.append(f"Shot {shot_no}: Outfit '{outfit_name}' not found in outfit lookup")
        else:
            if shot.get('characters_involved'):
                warnings.append(f"Shot {shot_no}: Has characters but no outfit mappings")
        
        return {"errors": errors, "warnings": warnings}
    
    def generate_all_scene_images(
    self,
    scene_description: 'SceneDescription',
    characters_info: List[Dict[str, Any]],
    locations_info: List[Dict[str, Any]],
    character_outfit_images: List[Dict[str, Any]],  # NEW: Instead of separate outfits
    product_info: Optional[Dict[str, Any]] = None,
    aspect_ratio: str = "16:9",
    project_id: str = "project",
    delay_between_shots: float = 2.0,
    validate_before_generation: bool = True
) -> Dict[str, Any]:
        """Generate scene images using character-outfit combination images"""
        
        print("\n" + "="*100)
        print(f"GENERATING SCENE IMAGES - {scene_description.ad_title}")
        print(f"Aspect Ratio: {aspect_ratio}")
        print("="*100 + "\n")
        
        self.generation_progress["total_shots"] = len(scene_description.shots)
        
        # Create location lookup
        loc_lookup = {loc['name'].lower(): loc for loc in locations_info}
        print(f"📋 Location lookup created: {list(loc_lookup.keys())}")
        
        # NEW: Create character-outfit lookup (combined_id: image_path)
        char_outfit_lookup = {
            co['combined_id']: co for co in character_outfit_images
        }
        print(f"📋 Character-outfit lookup created: {list(char_outfit_lookup.keys())}")
        
        for idx, shot in enumerate(scene_description.shots, 1):
            print(f"\n{'='*100}")
            print(f"[{idx}/{len(scene_description.shots)}] Processing Shot {shot.shot_no}")
            print(f"{'='*100}")
            
            # Get location reference
            location_ref = None
            if hasattr(shot, 'location_name') and shot.location_name:
                location_name_lower = shot.location_name.lower()
                if location_name_lower in loc_lookup:
                    location_ref = loc_lookup[location_name_lower]
                    print(f"  ✅ Location reference: {shot.location_name}")
            
            # NEW: Get character-outfit references for this shot
            character_outfit_refs = []
            
            if hasattr(shot, 'outfit_character_mapping') and shot.outfit_character_mapping:
                print(f"  👔 Processing {len(shot.outfit_character_mapping)} character-outfit mappings:")
                
                for mapping in shot.outfit_character_mapping:
                    char_name = mapping.character_name.lower()
                    outfit_name = mapping.outfit_name.lower()
                    combined_id = f"{char_name}_{outfit_name}"
                    
                    print(f"     • Looking for: {combined_id}")
                    
                    if combined_id in char_outfit_lookup:
                        char_outfit_data = char_outfit_lookup[combined_id]
                        character_outfit_refs.append(char_outfit_data)
                        print(f"       ✅ Found character-outfit image")
                    else:
                        print(f"       ❌ Not found in lookup")
            
            # Get product reference if needed
            product_ref = None
            if shot.product_image_required and product_info:
                product_ref = product_info
                print(f"  📦 Product reference: {product_info.get('name', 'product')}")
            
            # Summary
            print(f"\n  📊 Reference Summary for Shot {shot.shot_no}:")
            print(f"     • Character-Outfit combinations: {len(character_outfit_refs)}")
            print(f"     • Location: {'Yes' if location_ref else 'No'}")
            print(f"     • Product: {'Yes' if product_ref else 'No'}")
            
            # Generate scene image
            image_path = self.generate_scene_image(
                shot=shot.model_dump(),
                image_prompt=shot.image_prompt,
                character_outfit_refs=character_outfit_refs,  # NEW: Pass character-outfit images
                location_ref=location_ref,
                product_ref=product_ref,
                aspect_ratio=aspect_ratio,
                project_id=project_id
            )
            
            # Delay
            if idx < len(scene_description.shots):
                print(f"\n⏳ Waiting {delay_between_shots}s before next generation...")
                time.sleep(delay_between_shots)
        
        # Print summary
        print("\n" + "="*100)
        print("GENERATION COMPLETE")
        print("="*100)
        print(f"✅ Successfully generated: {len(self.generation_progress['generated_images'])}/{self.generation_progress['total_shots']}")
        print(f"❌ Failed: {len(self.generation_progress['failed_generations'])}")
        
        return self.generation_progress
    
    def save_generation_report(self, output_file: str, output_dir: str = "projects_data"):
        """Save generation progress report to JSON"""
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.generation_progress, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Generation report saved to {file_path}")
        return file_path






