from openai import OpenAI
import base64
import os
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from PIL import Image
from google import genai
from google.genai import types
from io import BytesIO
import io
import datetime
import PIL.Image as PILImage
import tempfile

from dotenv import load_dotenv

load_dotenv()


class LocationInfo(BaseModel):
    """Location information extracted from the script"""
    name: str = Field(description="Location Name (lowercase)")
    overall_description: Optional[str] = Field(
        default=None, 
        description="Detailed visual description of the location"
    )
    image_path: Optional[str] = Field(default=None, description="Path to generated location image")


class FullLocation(BaseModel):
    """Full location details for image generation"""
    name: str
    overall_description: Optional[str] = None
    image_path: Optional[str] = None


class LocationGenerator:
    def __init__(self, output_dir: str = "location_images"):
        # Configure Google Generative AI
        self.client = genai.Client()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_location_prompt(self, location: dict) -> str:
        """
        Create detailed prompt for location image generation
        
        Args:
            location: Dictionary with 'name' and 'overall_description'
        """
        name = location.get('name', 'Location')
        description = location.get('overall_description', '')
        
        # Parse the description to extract structured details
        location_details = self._parse_location_description(description)
        
        base_prompt = f"""
Create a highly realistic, cinematic photograph of a {name}.

{description}

DETAILED SPECIFICATIONS:

Location Type: {location_details.get('location_type', name)}

Design Style & Mood:
{location_details.get('design_style', 'Modern and realistic')}

Key Architectural Elements:
{location_details.get('architectural_elements', 'Authentic architectural details appropriate to the location type')}

Color Palette & Materials:
{location_details.get('color_palette', 'Natural, realistic color palette')}

Props & Visual Details:
{location_details.get('props', 'Appropriate props and details that make the space feel lived-in and authentic')}

Lighting:
{location_details.get('lighting', 'Natural, cinematic lighting that enhances the mood')}

Atmosphere & Vibe:
{location_details.get('atmosphere', 'Realistic and inviting atmosphere')}

PHOTOGRAPHY REQUIREMENTS:
- Camera: {location_details.get('camera_framing', 'Wide shot showing the full space')}
- High resolution, photorealistic quality
- Professional cinematography style suitable for commercial advertising
- Perfect for film production reference
- No people in the frame - empty location shot
- Sharp focus with appropriate depth of field
- Color graded for commercial/cinematic look
- Indian context and aesthetic where applicable

IMPORTANT:
- Create an EMPTY location (no people)
- Focus on the environment and atmosphere
- Realistic, not CGI or cartoon-like
- Professional photography quality
- Suitable for use as a filming location reference

Style: Cinematic photography, commercial advertisement quality, realistic and detailed.
"""
        return base_prompt.strip()
    
    def _parse_location_description(self, description: str) -> Dict[str, str]:
        """
        Parse the structured location description into components
        
        Args:
            description: Structured description string with format:
                Location Type: ..., Design Style & Mood: ..., etc.
        
        Returns:
            Dictionary with parsed components
        """
        if not description:
            return {}
        
        components = {
            'location_type': '',
            'design_style': '',
            'architectural_elements': '',
            'color_palette': '',
            'props': '',
            'lighting': '',
            'atmosphere': '',
            'camera_framing': ''
        }
        
        # Parse each component
        lines = description.split(',')
        current_key = None
        
        for line in lines:
            line = line.strip()
            
            # Check for component headers
            if 'Location Type:' in line:
                components['location_type'] = line.split('Location Type:')[1].strip()
            elif 'Design Style & Mood:' in line or 'Design Style and Mood:' in line:
                components['design_style'] = line.split(':')[1].strip() if ':' in line else line
            elif 'Key Architectural Elements:' in line:
                components['architectural_elements'] = line.split('Key Architectural Elements:')[1].strip()
            elif 'Color Palette & Materials:' in line or 'Color Palette and Materials:' in line:
                components['color_palette'] = line.split(':')[1].strip() if ':' in line else line
            elif 'Props & Visual Details:' in line or 'Props and Visual Details:' in line:
                components['props'] = line.split(':')[1].strip() if ':' in line else line
            elif 'Lighting:' in line:
                components['lighting'] = line.split('Lighting:')[1].strip()
            elif 'Atmosphere & Vibe:' in line or 'Atmosphere and Vibe:' in line:
                components['atmosphere'] = line.split(':')[1].strip() if ':' in line else line
            elif 'Camera Framing Note:' in line:
                components['camera_framing'] = line.split('Camera Framing Note:')[1].strip()
            else:
                # Continuation of previous component
                if current_key and components[current_key]:
                    components[current_key] += ', ' + line
        
        # If parsing failed, use the entire description as location_type
        if not any(components.values()):
            components['location_type'] = description[:200]
        
        return components
    
    def generate_image(self, prompt: str, location_id: str) -> Optional[str]:
        """
        Generate location image using Gemini
        
        Args:
            prompt: Detailed prompt for image generation
            location_id: Unique identifier for the location
            
        Returns:
            File path to generated image or None if failed
        """
        try:
            print(f"Generating location image for {location_id} using Gemini...")
            
            # Use Gemini model for image generation
            
            
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
            filename = f"{location_id}_location.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Check if response has images
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        image.save(filepath)
                        image_saved = True
                        print(f"✓ Saved location image: {filepath}")
                        break
                    elif hasattr(part, 'text') and part.text:
                        print(f"Gemini response: {part.text[:100]}...")
            
            if not image_saved:
                print(f"⚠ No image data generated for {location_id}")
                return None
                
            return filepath
            
        except Exception as e:
            print(f"✗ Error generating location image for {location_id}: {str(e)}")
            return None
    
    def generate_location_image(self, location: FullLocation, location_id: str = None) -> FullLocation:
        """
        Generate image for a single location
        
        Args:
            location: FullLocation object
            location_id: Optional custom location ID
            
        Returns:
            FullLocation object with image_path populated
        """
        if not location_id:
            location_id = location.name.lower().replace(' ', '_')
        
        print(f"\nGenerating image for location: {location.name} ({location_id})")
        
        location_dict = location.model_dump()
        
        # Generate location image
        location_prompt = self.create_location_prompt(location_dict)
        print(f"Location prompt preview: {location_prompt[:150]}...")
        location_image_path = self.generate_image(location_prompt, location_id)
        
        if not location_image_path:
            print(f"Trying simpler prompt for {location.name}...")
            simple_prompt = f"Professional cinematic photograph of a {location.name}, empty location, realistic, high quality, suitable for film production"
            location_image_path = self.generate_image(simple_prompt, location_id)
        
        if not location_image_path:
            print(f"Creating placeholder for {location.name}...")
            location_image_path = self.create_placeholder_image(location_id, location.name)
        
        # Update location with image path
        location_dict['image_path'] = location_image_path
        location_with_image = FullLocation(**location_dict)
        
        return location_with_image
    
    def generate_single_location_image(self, location_dict: Dict, custom_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate image for a single location with optional custom prompt
        
        Args:
            location_dict: Location dictionary
            custom_prompt: Optional custom prompt to use instead of default
            
        Returns:
            File path to generated image or None if failed
        """
        try:
            location_id = location_dict['name'].lower().replace(' ', '_')
            
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self.create_location_prompt(location_dict)
            
            print(f"Generating location image with prompt: {prompt[:100]}...")
            location_image_path = self.generate_image(prompt, location_id)
            
            if not location_image_path:
                print(f"Trying simpler prompt for {location_dict['name']}...")
                simple_prompt = f"Professional cinematic photograph of a {location_dict['name']}, empty location, realistic, high quality, suitable for film production"
                location_image_path = self.generate_image(simple_prompt, location_id)
            
            return location_image_path
        except Exception as e:
            print(f"Error generating single location image: {e}")
            return None

    def generate_locations_image(self, location: FullLocation) -> FullLocation:
        """
        Generate image for a single location
        
        Args:
            location: FullLocation object
            location_id: Optional custom location ID
            
        Returns:
            FullLocation object with image_path populated
        """
        if not location_id:
            location_id = location.name.lower().replace(' ', '_')
        
        print(f"\nGenerating image for location: {location.name} ({location_id})")
        
        location_dict = location.model_dump()
        
        # Generate location image
        location_prompt = self.create_location_prompt(location_dict)
        print(f"Location prompt preview: {location_prompt[:150]}...")
        location_image_path = self.generate_image(location_prompt, location_id)
        
        if not location_image_path:
            print(f"Trying simpler prompt for {location.name}...")
            simple_prompt = f"Professional cinematic photograph of a {location.name}, empty location, realistic, high quality, suitable for film production"
            location_image_path = self.generate_image(simple_prompt, location_id)
        
        if not location_image_path:
            print(f"Creating placeholder for {location.name}...")
            location_image_path = self.create_placeholder_image(location_id, location.name)
        
        # Update location with image path
        location_dict['image_path'] = location_image_path
        location_with_image = FullLocation(**location_dict)
        
        return location_with_image
    
    def create_placeholder_image(self, location_id: str, location_name: str) -> str:
        """Create a placeholder image when AI generation fails"""
        try:
            filename = f"{location_id}_location.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create a simple placeholder image
            img = Image.new('RGB', (800, 600), color='lightblue')
            
            # Add text
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                text = f"{location_name}\n(Location Placeholder)"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (800 - text_width) // 2
                y = (600 - text_height) // 2
                
                draw.text((x, y), text, fill='black', font=font)
            except:
                pass
            
            img.save(filepath)
            print(f"✓ Created placeholder image: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"✗ Error creating placeholder: {str(e)}")
            return None
    
    def generate_images_for_all_locations(self, locations: List[FullLocation]) -> List[FullLocation]:
        """
        Generate images for all locations
        
        Args:
            locations: List of FullLocation objects
            
        Returns:
            List of FullLocation objects with image_path populated
        """
        locations_with_images = []
        
        print(f"\n{'='*80}")
        print(f"Starting image generation for {len(locations)} locations...")
        print(f"{'='*80}\n")
        
        for i, location in enumerate(locations, 1):
            print(f"\n--- Location {i}/{len(locations)} ---")
            location_id = f"loc_{i:03d}_{location.name.lower().replace(' ', '_')}"
            location_with_image = self.generate_location_image(location, location_id)
            locations_with_images.append(location_with_image)
        
        print(f"\n{'='*80}")
        print(f"✓ Image generation complete for all locations!")
        print(f"{'='*80}\n")
        
        return locations_with_images
    
    def save_locations_with_images(self, locations: List[FullLocation], filename: str):
        """
        Save locations with image paths to JSON file
        
        Args:
            locations: List of FullLocation objects
            filename: Output JSON filename
        """
        import json
        
        locations_dict = {
            "locations": [loc.model_dump() for loc in locations],
            "total_locations": len(locations)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(locations_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Locations with image paths saved to {filename}")
    
    def display_locations_summary(self, locations: List[FullLocation]):
        """Display summary of locations"""
        print("\n" + "="*100)
        print("LOCATIONS SUMMARY")
        print("="*100 + "\n")
        
        for idx, location in enumerate(locations, 1):
            print(f"\n--- Location {idx}: {location.name.upper()} ---")
            print(f"Description: {location.overall_description[:150]}..." if location.overall_description else "No description")
            if location.image_path:
                print(f"Image: {location.image_path}")
            print("-" * 100)


# Example usage
# if __name__ == "__main__":
#     # Example locations
#     example_locations = [
#         FullLocation(
#             name="hotel room",
#             overall_description="Location Type: Hotel Room (Morning), Design Style & Mood: Minimal modern Indian, soft and calm mood, Key Architectural Elements: Light wooden furniture, soft beige curtains, neutral wall tones, Color Palette & Materials: Warm beige, soft white, natural wood, cotton bedding, Props & Visual Details: Cricket duffel bag by bedside, water bottle, sports shoes, framed art on wall, Lighting: Soft natural morning light filtering through curtains, warm gentle shadows, Atmosphere & Vibe: Peaceful morning preparation atmosphere, Camera Framing Note: Wide shot"
#         ),
#         FullLocation(
#             name="cricket stadium",
#             overall_description="Location Type: Cricket Stadium Exterior (Day), Design Style & Mood: Modern Indian sports venue, energetic and vibrant, Key Architectural Elements: Large concrete structure, steel railings, stadium seating visible, Color Palette & Materials: Blue stadium seats, white concrete, green field visible in background, Props & Visual Details: Stadium signage, flags, crowd barriers, Lighting: Bright harsh daylight from above, strong shadows, Atmosphere & Vibe: Match day excitement and anticipation, Camera Framing Note: Wide establishing shot"
#         ),
#         FullLocation(
#             name="stadium entrance",
#             overall_description="Location Type: Stadium Entrance Gate, Design Style & Mood: Industrial modern, busy and crowded feel, Key Architectural Elements: Metal gates, ticket counters, security checkpoints, Color Palette & Materials: Steel grey, concrete, glass panels, Props & Visual Details: Ticket scanners, security barriers, directional signs, sponsor banners, Lighting: Mix of natural daylight and artificial overhead lights, Atmosphere & Vibe: Pre-match buzz and crowd energy, Camera Framing Note: Medium shot"
#         )
#     ]
    
#     # Initialize generator
#     generator = LocationGenerator(output_dir="location_images")
    
#     # Generate images for all locations
#     locations_with_images = generator.generate_images_for_all_locations(example_locations)
    
#     # Display summary
#     generator.display_locations_summary(locations_with_images)
    
#     # Save to file
#     generator.save_locations_with_images(
#         locations_with_images, 
#         "locations_with_images.json"
#     )