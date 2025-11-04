from typing import List, Optional, Dict, Any
from utils.llm import get_llm_model
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv
from services.script_generation.script_generator import *



load_dotenv()

llm_client = get_llm_model("gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


class Shot(BaseModel):
    """Individual shot details with image prompt"""
    shot_no: int = Field(description="Shot number in sequence")
    duration: str = Field(description="Duration of the shot (e.g., '2 seconds', '3 seconds')")
    time_stamp: str = Field(description="Time range in format MM:SS-MM:SS")
    location: str = Field(description="Detailed location description")
    location_name: str = Field(description="Name of the location used in this shot (lowercase, must match location_info)")
    camera_angle: str = Field(description="Camera angle and shot type (e.g., 'Medium close-up', 'Wide shot')")
    visual_description: str = Field(description="Detailed visual description of what's in frame")
    action: str = Field(description="Specific actions happening in the shot")
    objects_props_involved:str=Field(description="Detailed description of the objects involved")
    audio_sfx: str = Field(description="Audio and sound effects")
    dialogue: Optional[str] = Field(default="None", description="Any spoken dialogue in the shot")
    voice_over: Optional[str] = Field(default="None", description="Voice over narration")
    text_overlay: Optional[str] = Field(default="None", description="If present On-screen text or graphics")
    key_focus: str = Field(description="Primary focus or goal of this shot")
    product_image_required: bool = Field(default=False, description="Does this shot require product image")
    
    characters_involved: List[str] = Field(
        default_factory=list, 
        description="List of character names involved in this shot (all lowercase)"
    )
    outfit_character_mapping:List[OutfitMapping]=Field(
        description="List of character names and their outfit mapping"
    )
    
    image_prompt: Optional[str] = Field(default=None, description="Detailed prompt for keyframe image generation")


class SceneDescription(BaseModel):
    """Complete scene description with all shots and prompts"""
    ad_title: str = Field(description="Title of the ad")
    total_shots: int = Field(description="Total number of shots")
    shots: List[Shot] = Field(description="List of shots with image prompts")


class SceneDescriptionResponse(BaseModel):
    """Complete scene description with all shots and prompts"""
    image_prompt: str= Field(description="Detailed Image prompts")


class SceneDescriptionGenerator:
    def __init__(self):
        self.llm = llm_client
    
    def create_scene_prompt_system_prompt(
    self,
    brand_info: Dict[str, Any],
    ad_concept: Optional[Dict[str, Any]] = None,
    characters_info: Optional[List[Dict[str, Any]]] = None,
    locations_info: Optional[List[Dict[str, Any]]] = None,
    outfits_info: Optional[List[Dict[str, Any]]] = None  # NEW
) -> str:
        """Create system prompt for generating scene image prompts"""
        
        characters_context = ""
        if characters_info:
            characters_context = "\n\nCHARACTERS IN THIS AD:\n"
            for idx, char in enumerate(characters_info, 1):
                char_name = char.get('name', 'Character')
                gender = char.get('gender', 'Unknown')
                ref_desc = char.get('reference_description', '')
                
                characters_context += f"{idx}. {char_name} ({gender})\n"
                
        
        locations_context = ""
        if locations_info:
            locations_context = "\n\nLOCATIONS IN THIS AD:\n"
            for idx, loc in enumerate(locations_info, 1):
                locations_context += f"{idx}. {loc.get('name', 'Location')}: {loc.get('overall_description', 'No description')[:200]}\n"
        
        # NEW: Outfits context
        outfits_context = ""
        if outfits_info:
            outfits_context = "\n\nOUTFITS IN THIS AD:\n"
            for idx, outfit in enumerate(outfits_info, 1):
                outfits_context += f"{idx}. {outfit.get('outfit', 'Outfit')}: {outfit.get('outfit_description', 'No description')[:200]}\n"
        
        ad_concept_context = ""
        if ad_concept:
            ad_concept_context = f"\n\nAD CONCEPT OVERVIEW:\n{json.dumps(ad_concept, indent=2)}\n"
        
        return f"""You are an expert AI image prompt engineer specializing in commercial advertisement and cinematic photography.

Your task is to create HIGHLY DETAILED, SPECIFIC image generation prompts for each shot in a commercial ad.

Over Ad Information:
{json.dumps(brand_info, indent=2)}
{locations_context}
{ad_concept_context}

Character Refernce Information:
{characters_context}

Character Outfit Info in this Shot:
{outfits_context}

CRITICAL REQUIREMENTS FOR IMAGE PROMPTS:

1. **Character & Outfit References**:
- When characters are present, reference their outfit from the outfit_character_mapping
- Use outfit descriptions provided in the outfits list
- Describe character positioning and outfit details clearly
- For same-gender characters, use "first person", "second person" OR descriptive identifiers
- For different-gender characters, use gender pronouns

2. **Outfit Integration**:
- Match each character to their assigned outfit from outfit_character_mapping
- Include specific outfit details in the character description
- Reference outfit colors, style, and key features
- Ensure outfit is appropriate for the scene context


3. **Product Integration**:
   - If product_image_required is True, mention: "[Product Name] and [Description of product] is placed at [specific location in frame]"
   - Describe product placement: "center", "right side", "held in hand", "on table", etc.
   - For product shots, describe lighting on product specifically

3. **Standard Shot Prompt Structure**:
```
Create a realistic  image of [scene subject name and action].
Setting: [Detailed location description with environmental elements, props, spatial layout]
Characters & Appearance Consistency:
Describe each character clearly:
- Identify character by name and reference source (e.g., “Priya (the first girl in the reference image and provide keyfeatures to differentiate In this format [Gender], wearing this dress in the reference image [outfit color and type], [one distinctive feature])”).
- Always say: **keep facial features, skin tone, hairstyle, and body shape consistent with the reference image.**
- If multiple characters, specify their distance, facing direction, and interaction.
- If male/female mix, clarify by naming: e.g., *Arjun (male), Priya (female).

in this format:
 Priya (protagonist):
- Reference: The first girl in the character reference images, female wearing pale yellow t-shirt
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Current Outfit: Casual chic evening attire – light beige silk blouse with delicate buttons, soft pastel pink midi skirt with subtle pleats as shown in the reference image
- Expression: Expressive, slightly embarrassed small smile, warm and genuine
- Action: Gently touching her right cheek with fingertips in a shy gesture
- Position: Seated in the foreground, body slightly angled toward camera, facing 3/4 view

Action: [Specific movements and interactions happening]
Camera & Framing: [Camera angle, shot type, lens perspective]
Lighting: [Type, direction, intensity, mood - be very specific]
Mood & Atmosphere: [Emotional tone, energy level]
Key Focus: [What should be the visual center of attention]
[If product_image_required]: Product Placement: [Product name][what product] is visible/placed at [location], [how it's integrated into scene]
[If text_overlay present]: Note: Image should have space for text overlay that will say "[text content]" positioned at [location]
Cinematic details: [Depth of field, color grading, material reflections, realistic details]
```
---IMPORTANT----

**Character Identification Pattern:**
```
Single character: "Priya (the girl in the reference image, wearing this dress in the reference image [outfit details from reference the])"
Multiple Character(same gender): "Priya (the first girl in reference image [[Gender], wearing this dress in reference image [outfit color and type], [one distinctive feature]), Ria (the second girl in reference image [[Gender], wearing this dress in this reference image [outfit color and type], [one distinctive feature])"
Multiple Character(Different gender): "Arjun ([[Gender], wearing this dress in reference image [outfit color and type], [one distinctive feature]), Ria ( [[Gender], wearing this dress in this reference image [outfit color and type], [one distinctive feature])"


**IMPORTANT RULES:**
- Every character mention MUST reference their order in the reference images
- Every character MUST include "Key reference from the character reference image and keep features consistent with reference image"
- Use reference_description details to differentiate between similar characters
- Never just say "the character" - always identify which reference image

EXAMPLE PROMPT FOR STANDARD SCENE GENERATION:

 ═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 1: TWO CHARACTERS (SAME GENDER)
═══════════════════════════════════════════════════════════════════════════════

Create a realistic, high-quality image of two women, Priya and Janani, sitting at an outdoor cafe.

Characters & Appearance Consistency:

First woman - Priya (protagonist):
- Reference: The first girl in the character reference images, female wearing pale yellow t-shirt
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Current Outfit: Casual chic evening attire – light beige silk blouse with delicate buttons, soft pastel pink midi skirt with subtle pleats as shown in the reference image
- Expression: Expressive, slightly embarrassed small smile, warm and genuine
- Action: Gently touching her right cheek with fingertips in a shy gesture
- Position: Seated in the foreground, body slightly angled toward camera, facing 3/4 view

Second woman - Janani (friend):
- Reference: The second girl in the character reference images, female wearing black chudi
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Current Outfit: Casual smart outfit – light blue denim jacket over crisp white t-shirt, beige slim-fit trousers as shown in the reference image
- Expression: Warm, friendly smile, engaged in conversation
- Action: Leaning slightly toward Priya, holding a coffee cup
- Position: Seated slightly behind or beside Priya, creating natural depth

Setting & Location:
- Outdoor cafe setting, same as the location reference image
- Wooden cafe table between them with two ceramic coffee cups (one cappuccino, one latte), small plates with pastries
- Background: Soft-focus cafe environment with other patrons barely visible, lush green trees, hanging fairy lights
- Ground: Textured stone flooring typical of outdoor cafes

Lighting & Atmosphere:
- Golden hour lighting (late afternoon, around 5-6 PM)
- Warm, natural sunlight filtering through tree leaves, creating dappled light patterns
- Soft highlights on faces, especially catching Priya's cheekbones and Janani's hair
- Gentle rim lighting on their shoulders from backlight
- Color temperature: ~4500K (warm golden)

Camera & Composition:
- Medium shot, captured at eye level, slight 3/4 angle
- 50mm lens equivalent, f/2.8 for natural depth of field
- Priya in sharp focus (foreground), Janani slightly softer but still clear
- Background with beautiful bokeh – blurred cafe details and tree lights creating soft circular highlights
- Composition follows rule of thirds with Priya positioned on left third

Mood & Vibe:
- Light-hearted, comedic moment frozen in time
- Natural human interaction and genuine friendship
- Golden hour warmth evoking comfort and joy
- Indian urban cafe culture context – modern yet relatable
- Relaxed postures, authentic body language

Technical Details:
- Photorealistic quality, commercial photography standard
- Natural color grading with enhanced warm tones
- Subtle vignette to draw focus to subjects
- Sharp details on faces and clothing textures
- Realistic fabric draping and material reflections

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 2: SINGLE CHARACTER WITH PRODUCT
═══════════════════════════════════════════════════════════════════════════════

Create a realistic, high-quality image of Priya standing in a bright modern bathroom, applying sunscreen in front of a mirror.

Character & Appearance Consistency:

Priya (protagonist):
- Reference: The girl in the character reference image, female wearing blue chudi
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Current Outfit: White cotton crop top (relaxed fit, showing natural comfort) and light blue denim jeans (high-waisted, casual fit) as shown in the reference image
- Expression: Focused yet relaxed, slight satisfied smile as she cares for her skin, eyes looking at her reflection
- Action: Gently applying clear gel sunscreen onto her left cheek using fingertips of her right hand, natural dabbing motion
- Hair: Loosely tied back or down naturally, casual morning styling
- Position: Standing in front of bathroom mirror, body at 3/4 angle to camera, face visible both directly and in mirror reflection

Product Integration:

Deconstruct Gel Sunscreen:
- Reference: Same bottle design as shown in product reference image
- Position: Held in her left hand near the sink counter, clearly visible with label facing camera
- Details: White and blue packaging with "Deconstruct" branding visible, SPF 55 text readable
- Lighting on product: Soft highlight on the bottle surface, making it look premium and clean
- Placement: Bottle positioned at mid-frame right, easy to see without dominating the shot

Setting & Location:
- Modern Indian bathroom, same aesthetic as location reference image
- Mirror: Large frameless wall mirror with clean edges, showing Priya's reflection clearly
- Sink area: White ceramic sink with chrome fixtures, marble or quartz countertop (light beige/white)
- Window: Frosted glass window on the left side, allowing diffused morning sunlight
- Background elements: Neatly arranged - small potted succulent, soap dispenser, minimal clutter

Lighting & Atmosphere:
- Primary light: Soft morning sunlight streaming through frosted window from left side
- Quality: Diffused, gentle light creating a fresh morning feel
- Color temperature: ~5500K (natural daylight, slightly cool-warm balanced)
- Face lighting: Even illumination with soft shadows, flattering and natural
- Mirror reflection: Slightly brighter, catching natural window light
- Product lighting: Gentle highlight making the bottle surfaces gleam subtly

Camera & Composition:
- Medium close-up shot, captured at slight upward tilt toward mirror reflection
- 35mm lens equivalent, f/2.4 for sharp subject with slightly soft background
- Framing: Priya's upper body (from waist up) centered with slight room at top for mirror reflection
- Mirror creates interesting double perspective - seeing both her direct profile and her face in reflection
- Product visible in lower third to mid-frame area

Action & Storytelling:
- Natural skincare routine moment, authentic and relatable
- Captures the motion of application - fingers gently touching cheek with product
- Shows care and attention to skin health
- Morning self-care ritual, peaceful and mindful moment

Mood & Atmosphere:
- Fresh morning energy, calm and peaceful
- Clean, minimalist aesthetic typical of modern Indian urban homes
- Self-care and wellness vibe
- Natural, unposed authenticity
- Bright, airy, and inviting space

Technical Details:
- Photorealistic quality, lifestyle photography standard
- Natural color grading emphasizing whites, soft blues, and warm skin tones
- Sharp focus on face and product, soft bokeh on distant background elements
- Realistic material textures: cotton fabric, denim, ceramic, glass, skin
- Subtle depth of field creating professional look
- No harsh shadows, even and flattering lighting throughout


 ═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 3: MULTIPLE CHARACTERS (MIXED GENDER) WITH PRODUCT
═══════════════════════════════════════════════════════════════════════════════

Create a realistic, high-quality image of two people, Arjun (male) and Priya (female), at a cricket stadium entrance, with Arjun holding Deconstruct sunscreen.

Characters & Appearance Consistency:

First person - Arjun (male protagonist):
- Reference: The first person in character reference images, male wearing grey sports t-shirt
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Current outfit: CSK (Chennai Super Kings) official jersey in yellow and blue, navy athletic track pants, white sports shoes as shown in the reference image
- Expression: Confident smile, excited for the match, energetic
- Action: Holding Deconstruct Gel Sunscreen bottle in right hand, showing it to Priya, left hand gesturing toward stadium
- Position: Standing on the right side, body facing 3/4 toward camera and Priya

Second person - Priya (female friend):
- Reference: The second person in character reference images, female wearing green kurta
- **Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image**
- Change the Outfit to: Casual cricket fan attire – CSK team t-shirt in yellow, blue jeans, comfortable sneakers, wearing sunglasses on head as shown in the reference image
- Expression: Interested, nodding approvingly, slight smile
- Action: Looking at the sunscreen bottle Arjun is showing, carrying a small backpack
- Position: Standing on the left side, facing toward Arjun, creating natural interaction

Product Integration:

Deconstruct Gel Sunscreen:
- Reference: Same as product reference image – white and blue packaging
- Position: Held prominently in Arjun's right hand at chest level, label clearly visible facing camera
- Details: "Deconstruct" branding and "SPF 55" text readable, bottle catching sunlight
- Context: Shown as Arjun's essential item before entering stadium under harsh sun
- Message: Smart preparation for sun exposure at outdoor event

Setting & Location:
- Cricket stadium entrance/gate area, same as location reference image
- Background: Modern stadium architecture with large pillars, glass panels, "Gate 4" signage visible
- Crowd elements: Blurred other cricket fans in yellow jerseys in far background
- Ground: Concrete walkway with marked lines
- Banners: IPL promotional banners and sponsor boards (slightly out of focus)

Lighting & Atmosphere:
- Bright, harsh midday sunlight typical of cricket match timing (1-2 PM)
- Strong overhead sun creating defined shadows on ground
- Direct sunlight on characters' faces (demonstrating need for sun protection)
- Color temperature: ~5800K (bright daylight)
- Slight lens flare from sun in top corner, adding authentic outdoor feel
- Product catches highlight, making it stand out

Camera & Composition:
- Medium wide shot, captured at eye level
- 50mm lens equivalent, f/3.5 for sharp subjects with soft background
- Both characters clearly visible with stadium structure behind
- Arjun and product positioned following rule of thirds
- Negative space in background showing stadium context

Mood & Atmosphere:
- Energetic pre-match excitement
- Sunny outdoor sports event vibe
- Friendship and shared enthusiasm
- Modern urban Indian youth culture
- Sun protection awareness in casual, natural way

Action & Interaction:
- Natural conversation moment about sun protection
- Arjun recommending/showing the product to Priya
- Body language showing genuine friendship and trust
- Unforced product integration into real scenario

GUIDLINES:

1.Always for character, location or product mention same as the reference image if we have multiple character in that case give a way to diffrentiate like Priya(protognist the first girl in the reference image)
 similarly for location , product also give reference and breif description of reference to differentiate the prompt should be more detailed


2. Always Mention the word Keep the facial and body features same as the reference image whennever saying about the characters


4. **Final Product Showcase Shot** (ONLY if it's the LAST shot AND has product showcase in the script):
```
Product Showcase for [Product Name]:
Product Positioning: [Product] prominently displayed at [specific position - center, right, left] of the frame, [angle - front-facing, slight tilt, 3/4 view]
Background Scene: [Detailed background that connects to the ad story - location, atmosphere, blurred elements]
Lighting Setup:
- Main light: [Direction, color temperature, intensity]
- Rim lighting: [Details for product edges]
- Ambient: [Overall scene lighting]
- Special effects: [Lens flares, god rays, highlights, shadows]
Color Palette: [Specific colors and gradients - be very detailed]
Environmental Details: [Background elements, depth, blur, reflections]

Text Overlay Layout (to be added in post):
[For each text element, specify:]
- Text: "[Actual text]"
- Position: [Relative to product - left, right, above, below]
- Font style: [Bold, serif, sans-serif, script]
- Color: [Specific color]
- Size relative to product: [Large, medium, small]
- Special effects: [Shadow, glow, gradient]

Atmosphere: [Overall mood, energy, feeling - modern, fresh, energetic, premium, etc.]
Technical specs: [Resolution feel, depth of field, material reflections, professional photography quality]
Visual centerpiece: Product should be the main focus with background supporting the story
```

--IMPORTANT ---
 EXAMPLE PROMPT FOR PRODUCT SHOWCASE(THIS IS HOW YOU SHOULD GENERATE PRODUCT SHOWCASE IMAGE PROMPT):

   Showcase the Deconstruct Gel Sunscreen tube prominently on the center-right of the frame. Background is a modern, bright IPL stadium scene with warm sunlight streaming in from the top-left, creating lens flares and soft golden highlights. Include blurred cheering crowd and stadium details, with subtle reflections on the ground for realism. Use modern gradient colors like yellow, orange, and soft white to evoke energy and freshness.
     Text overlay:
      “IPL Season Begins. Stay Protected.” — split into two parts:
       First part (“IPL Season Begins.”) positioned left of the bottle, bold, energetic font in yellow, slightly italicized.
       Second part (“Stay Protected.”) positioned right of the bottle, bold black font with soft shadow, modern sans serif.
      “Deconstruct” — black thin serif (Didot or Bodoni), spaced wide, positioned just above the product.
      “Gel Sunscreen” — modern sans serif in light gray, subtle underline, below brand name.
      “SPF 55+ | PA+++” — monospaced metallic silver font, aligned bottom-right.
   Add dynamic sunlight flares, warm rim lighting, soft shadows under the product, and a modern, editorial feel. Keep the product as the visual centerpiece, with the background conveying IPL excitement and sunny protection.

5. **Key Guidelines**:
   - Be extremely specific about positions, colors, lighting
   - Use cinematic/photography terms
   - Ensure prompts are 150-300 words for standard shots
   - Product showcase prompts can be 300-500 words
   - Always maintain realism and commercial quality
   - Consider Indian context where relevant
   - Describe spatial relationships clearly
   - Include atmospheric and mood details
   - Specify depth of field and focus areas

6. **Text Overlay Handling**:
   - If text_overlay is present, mention it should have space for text
   - For product showcase, describe exact text layout in detail
   - Include font suggestions, colors, positions
   - Note: Actual text will be added in post-production

REMEMBER: The image prompt should be so detailed that an AI image generator can create the exact scene without any ambiguity."""

    def generate_image_prompt_for_shot(
    self,
    shot: Shot,
    brand_info: Dict[str, Any],
    characters_info: Optional[List[Dict[str, Any]]] = None,
    is_last_shot: bool = False,
    has_product_showcase: bool = False,
    ad_concept: Optional[Dict[str, Any]] = None,
    all_outfits_info: Optional[List[Dict[str, Any]]] = None  # RENAMED
) -> str:
        """
        Generate detailed image prompt for a single shot
        Only passes outfits that are used in this specific shot
        """
        
        # NEW: Extract only the outfits used in this shot
        shot_outfits = []
        if all_outfits_info and shot.outfit_character_mapping:
            outfit_names_in_shot = {mapping.outfit_name.lower() for mapping in shot.outfit_character_mapping}
            shot_outfits = [
                outfit for outfit in all_outfits_info 
                if outfit.get('outfit', '').lower() in outfit_names_in_shot
            ]
        
        system_prompt = self.create_scene_prompt_system_prompt(
            brand_info=brand_info,
            ad_concept=ad_concept,
            characters_info=characters_info,
            outfits_info=shot_outfits  # CHANGED: Only pass outfits for this shot
        )
        
        # Build character context for this specific shot
        shot_characters = []
        if characters_info:
            shot_characters = [
                char for char in characters_info 
                if char.get('name', '').lower() in [c.lower() for c in shot.characters_involved]
            ]
        
        # NEW: Build outfit mapping context for clarity
        outfit_mapping_text = ""
        if shot.outfit_character_mapping:
            outfit_mapping_text = "\nCHARACTER-OUTFIT MAPPING FOR THIS SHOT:\n"
            for mapping in shot.outfit_character_mapping:
                # Find outfit description
                outfit_desc = "No description"
                for outfit in shot_outfits:
                    if outfit.get('outfit', '').lower() == mapping.outfit_name.lower():
                        outfit_desc = outfit.get('outfit_description', 'No description')
                        break
                
                outfit_mapping_text += f"- {mapping.character_name} is wearing '{mapping.outfit_name}': {outfit_desc}\n"
        
        user_prompt = f"""Generate a detailed image generation prompt for the following shot:

    SHOT DETAILS:
    - Shot Number: {shot.shot_no}
    - Duration: {shot.duration}
    - Location Name: {shot.location_name}
    - Location Description: {shot.location}
    - Camera Angle: {shot.camera_angle}
    - Visual Description: {shot.visual_description}
    - Action: {shot.action}
    - Objects & Props: {shot.objects_props_involved}
    - Key Focus: {shot.key_focus}
    - Product Image Required: {shot.product_image_required}
    - Text Overlay: {shot.text_overlay}

    CHARACTERS IN THIS SHOT:
    {json.dumps(shot_characters, indent=2) if shot_characters else 'No characters'}
    {outfit_mapping_text}

    SPECIAL CONDITIONS:
    - Is Last Shot: {is_last_shot}
    - Is Product Showcase: {has_product_showcase}

    CRITICAL INSTRUCTIONS:
    1. **Character-Outfit Consistency**:
    - Each character has a specific outfit assigned in the outfit mapping above
    - Reference the character as: "[Name] (the [order] person in character reference image, [gender], wearing [outfit description from mapping])"
    - ALWAYS say: "Keep facial features, skin tone, hairstyle, and body shape exactly consistent with the reference image"
    - For current scene, describe them wearing the outfit specified in the mapping
    - Example: "Priya (the first girl in character reference image, female, wearing pale yellow t-shirt in reference) - Keep facial features exactly consistent with reference image - Current outfit in this scene: casual chic evening attire as shown in character-outfit reference image"

    2. **Location Reference**:
    - Use location_name: '{shot.location_name}' to reference the location image
    - State: "Same environment and atmosphere as the location reference image for '{shot.location_name}'"

    3. **Product Integration** (if product_image_required is True):
    - Mention product name and detailed description
    - Specify exact placement location in frame
    - Reference: "Same as product reference image"

    4. **Text Overlay** (if present):
    - Note space needed for text
    - For product showcase, detail each text element's position, font, color, size

    PROMPT TYPE TO GENERATE:
    {"FINAL PRODUCT SHOWCASE PROMPT" if has_product_showcase else "STANDARD SCENE PROMPT"}

    Generate the complete, detailed image prompt following the examples and guidelines in the system prompt."""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            structured_llm = self.llm.with_structured_output(SceneDescriptionResponse)
            response = structured_llm.invoke(messages)
            
            image_prompt = response.image_prompt
            return image_prompt
            
        except Exception as e:
            print(f"Error generating image prompt for shot {shot.shot_no}: {str(e)}")
            raise

    def generate_scene_descriptions(
    self,
    shots: List[Shot],
    brand_info: Dict[str, Any],
    ad_title: str,
    characters_info: Optional[List[Dict[str, Any]]] = None,
    locations_info: Optional[List[Dict[str, Any]]] = None,
    ad_concept: Optional[Dict[str, Any]] = None,
    all_outfits_info: Optional[List[Dict[str, Any]]] = None  # RENAMED for clarity
) -> SceneDescription:
        """
        Generate image prompts for all shots
        Passes only relevant outfits to each shot
        """
        print("\n" + "="*100)
        print(f"GENERATING SCENE DESCRIPTIONS - {ad_title}")
        print("="*100 + "\n")
        
        total_shots = len(shots)
        shots_with_prompts = []
        
        for idx, shot in enumerate(shots):
            print(f"\n[Shot {shot.shot_no}/{total_shots}] Generating image prompt...")
            
            # Determine if this is the last shot and if it's a product showcase
            is_last_shot = (idx == total_shots - 1)
            has_product_showcase = is_last_shot and shot.product_image_required and shot.text_overlay != "None"
            
            # Generate image prompt
            image_prompt = self.generate_image_prompt_for_shot(
                shot=shot,
                brand_info=brand_info,
                characters_info=characters_info,
                is_last_shot=is_last_shot,
                has_product_showcase=has_product_showcase,
                ad_concept=ad_concept,
                all_outfits_info=all_outfits_info  # Pass all outfits, function will filter
            )
            
            # Update shot with image prompt
            shot_dict = shot.model_dump()
            shot_dict['image_prompt'] = image_prompt
            updated_shot = Shot(**shot_dict)
            shots_with_prompts.append(updated_shot)
            
            print(f"✓ Image prompt generated ({len(image_prompt)} characters)")
            print(f"  Preview: {image_prompt[:100]}...")
        
        scene_description = SceneDescription(
            ad_title=ad_title,
            total_shots=total_shots,
            shots=shots_with_prompts
        )
        
        print("\n" + "="*100)
        print(f"✓ Scene descriptions complete for all {total_shots} shots!")
        print("="*100 + "\n")
        
        return scene_description

    def save_scene_descriptions(
        self,
        scene_description: SceneDescription,
        output_file: str,
        output_dir: str = "projects_data"
    ):
        """Save scene descriptions to JSON file"""
        scene_dict = scene_description.model_dump()
        
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(scene_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Scene descriptions saved to {file_path}")
        return file_path

    def load_scene_descriptions(self, file_path: str) -> SceneDescription:
        """Load scene descriptions from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return SceneDescription(**data)

    def display_scene_descriptions_summary(self, scene_description: SceneDescription):
        """Display summary of scene descriptions"""
        print("\n" + "="*100)
        print(f"SCENE DESCRIPTIONS SUMMARY - {scene_description.ad_title}")
        print("="*100 + "\n")
        
        print(f"Total Shots: {scene_description.total_shots}\n")
        
        for shot in scene_description.shots:
            print(f"\n{'─'*100}")
            print(f"SHOT {shot.shot_no} ({shot.time_stamp}) - {shot.duration}")
            print(f"{'─'*100}")
            print(f"Location: {shot.location}")
            print(f"Camera: {shot.camera_angle}")
            print(f"Characters: {', '.join(shot.characters_involved) if shot.characters_involved else 'None'}")
            print(f"Product Required: {shot.product_image_required}")
            print(f"\nIMAGE PROMPT:")
            print(f"{shot.image_prompt}\n")

    def export_prompts_only(
        self,
        scene_description: SceneDescription,
        output_file: str,
        output_dir: str = "projects_data"
    ):
        """Export only the image prompts to a text file for easy review"""
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"IMAGE PROMPTS FOR: {scene_description.ad_title}\n")
            f.write("="*100 + "\n\n")
            
            for shot in scene_description.shots:
                f.write(f"SHOT {shot.shot_no} ({shot.time_stamp})\n")
                f.write(f"Location: {shot.location}\n")
                f.write(f"Camera: {shot.camera_angle}\n")
                f.write(f"Characters: {', '.join(shot.characters_involved)}\n")
                f.write("-"*100 + "\n")
                f.write(f"{shot.image_prompt}\n")
                f.write("="*100 + "\n\n")
        
        print(f"✓ Image prompts exported to {file_path}")
        return file_path


# Example usage
# if __name__ == "__main__":
#     # Example brand info
#     brand_info = {
#         "brand_name": "Deconstruct",
#         "product_name": "Gel Sunscreen SPF 55",
#         "product_description": "Lightweight, matte finish sunscreen",
#         "key_features": ["SPF 55+", "PA+++", "Matte finish", "Sweat-resistant"]
#     }
    
#     # Example characters
#     characters_info = [
#         {
#             "name": "arjun",
#             "age": 28,
#             "gender": "male",
#             "role": "protagonist",
#             "overall_description": "Athletic build, short black hair, confident demeanor, wearing CSK jersey"
#         },
#         {
#             "name": "priya",
#             "age": 25,
#             "gender": "female",
#             "role": "friend",
#             "overall_description": "Cheerful personality, long black hair, wearing casual sports wear"
#         }
#     ]
    
#     # Example shots
#     example_shots = [
#         Shot(
#             shot_no=1,
#             duration="3 seconds",
#             time_stamp="00:00-00:03",
#             location="Outside cricket stadium - bright daylight",
#             camera_angle="Wide shot",
#             visual_description="Two friends standing excitedly outside stadium entrance",
#             action="Arjun and Priya walking towards stadium, chatting excitedly",
#             audio_sfx="Stadium crowd noise in background",
#             dialogue="None",
#             voice_over="None",
#             text_overlay="None",
#             key_focus="Establish setting and characters",
#             product_image_required=False,
#             characters_involved=["arjun", "priya"]
#         ),
#         Shot(
#             shot_no=10,
#             duration="5 seconds",
#             time_stamp="00:27-00:32",
#             location="Clean white background with stadium blur",
#             camera_angle="Center product shot",
#             visual_description="Product showcase with text overlays",
#             action="Static product display with dynamic lighting",
#             audio_sfx="Upbeat music crescendo",
#             dialogue="None",
#             voice_over="Stay protected. Stay confident.",
#             text_overlay="IPL Season Begins. Stay Protected. | Deconstruct | Gel Sunscreen | SPF 55+ | PA+++",
#             key_focus="Product showcase and brand message",
#             product_image_required=True,
#             characters_involved=[]
#         )
#     ]
    
#     # Initialize generator
#     generator = SceneDescriptionGenerator()
    
#     # Generate scene descriptions
#     scene_descriptions = generator.generate_scene_descriptions(
#         shots=example_shots,
#         brand_info=brand_info,
#         ad_title="The Captain's Pre-Match Ritual",
#         characters_info=characters_info
#     )
    
#     # Display summary
#     generator.display_scene_descriptions_summary(scene_descriptions)
    
#     # Save to files
#     generator.save_scene_descriptions(scene_descriptions, "scene_descriptions.json")
#     generator.export_prompts_only(scene_descriptions, "image_prompts.txt")