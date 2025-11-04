from typing import List, Optional, Dict, Any
from utils.llm import get_llm_model
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv


load_dotenv()




class CharacterInfo(BaseModel):
    """Character information extracted from the script"""
    name: str = Field(description="Character name (lowercase)")
    age: Optional[int] = Field(default=None, description="Approximate age of the character")
    role: Optional[str] = Field(default=None, description="Role in the ad (e.g., 'protagonist', 'friend', 'colleague')")
    gender: Optional[str] = Field(default=None, description="Gender of the character")
    overall_description: Optional[str] = Field(default=None, description="Detailed physical and personality description")
    image_path: Optional[str] = None
    reference_description: Optional[str] = None

class LocationInfo(BaseModel):
    """Character information extracted from the script"""
    name: str = Field(description="Location Name")
    overall_description: Optional[str] = Field(default=None, description="Detailed visual Description of the location how it looks what all things it has and key information of the location in detail")
    image_path: Optional[str] = None

class CharacterOutfitInfo(BaseModel):
    outfit: str= Field(description="name of the outfit in lowercase")
    outfit_description :str=Field(description="Detailed description of the outfit")
    image_path: Optional[str] = None

class OutfitMapping(BaseModel):
    character_name: str= Field(description="name of the character in lowercase")
    outfit_name :str=Field(description="name of the outfit in lowercase")


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


class ShotScript(BaseModel):
    """Complete shot-level script"""
    ad_title: str = Field(description="Title of the ad concept")
    total_duration: str = Field(description="Total ad duration")
    shots: List[Shot] = Field(description="List of all shots in sequence")
    characters_info: List[CharacterInfo] = Field(
        default_factory=list,
        description="List of all characters with detailed descriptions"
    )
    location_info:List[LocationInfo]=Field(
        default_factory=list,
        description="List of all Location with detailed descriptions"
    )
    character_outfit_info:List[CharacterOutfitInfo]=Field(
     description="List of detailed description of oufit and its name in lowercase"
     )


class ShotScriptGenerator:
    def __init__(self):
        self.llm = get_llm_model("gpt-5", api_key=os.getenv("OPENAI_API_KEY"))
        
    def create_shot_script_system_prompt(self) -> str:
        """Create system prompt for generating shot-level scripts"""
        return """You are an expert film director and scriptwriter specializing in commercial advertisements.

Your task is to convert ad concepts into detailed, shot-by-shot production scripts.

Each shot MUST include these specific columns this is for single shot information:
1. **Shot No**: Sequential number
2. **Duration**: Length of shot (e.g., "2 seconds", "3 seconds")
3. **Time stamp**: Time range (e.g., "00:00-00:02")
4. **Location**: Detailed location description with lighting/atmosphere
5. **Location Name**: EXACT name of the location from location_info list (lowercase) - this will be used to match the location reference image
6. **Camera Angle**: Shot type and angle (e.g., "Medium close-up", "Wide shot", "POV", "Over-the-shoulder")
7. **Visual Description**: Detailed description of what's visible in frame give as many inforamtion as in clear in detailed way
8. **objects_props_involved**:Detailed description of what all objects are present,(for example if bag is present give detailed description of the bag, like CSK cricket kit with blue and yellow in color with logo)
9. **Action**: Specific actions/movements happening
10. **Audio/SFX**: Sound effects and ambient audio
11. **Dialogue**: Any spoken words (use "None" if no dialogue)
12. **Voice Over**: VO narration (use "None" if no VO in this shot)
13. **Text Overlay**: On-screen text/graphics (use "None" if no text)
14. **Key Focus**: Primary purpose/goal of the shot
15. **Product image** Boolean say True when product image required or False if this shot does not contain product image in focus
16. **Characters Involved** (list of character names in lowercase)
17 **Character outfit mapping** (list of character and their outfit mapping)

 example for character outfit mapping ["priya": "priya_casual_wear"] for single shot like wise if we had multiple character include their outfit also ["priya": "priya_office_formal" ,"jay": "jay_casual_wear"]


Guidelines for shot creation:
- Each shot should be 2-5 seconds typically
- Ensure smooth flow and narrative progression
- Include establishing shots, action shots, product shots, and closing shots
- Always End the Video with Product Showcase shot where at the final shot you need to generate with text overlay describing with keyfeatures and tagline or keymessage in this ad
- Timestamps must be sequential and accurate
- Be specific about camera movements, angles, and framing
- Include relevant audio design (SFX, ambient sounds, music cues)
- For Object and Props give as many detailed description in detail and pass all nuance
- Distribute voice over strategically across shots
- Identify key product showcase moments
- Consider pacing and emotional beats
- Ensure visual variety and dynamic composition

Guidelines for outfit generaion and mapping on shot level

    1. **Decide outfit per shot**:
    - For every shot that contains characters, determine what outfit they are wearing.
    - If the same outfit continues across multiple shots, keep the same outfit name.
    - If the outfit changes, assign a *new outfit name*.
    2. **Outfit Naming Convention** (STRICT):
    <character_name_in_lowercase>_<type_of_wear_or_scene_keyword>
    Examples:
    - priya_casual_wear
    - priya_bathroom_morning_fit
    - genie_modern_magic_fit

    3. **Output Format** *(VERY IMPORTANT)*:
    ### A. List of CharacterOutfitInfo (unique outfits only):
    [
    {
    "outfit": "<outfit_name>",
    "outfit_description": "<detailed outfit description>"
    },
    ...
    ]

    ### B. For each shot, provide Outfit Mapping only:
    "outfit_character_mapping": [
    {"character_name": "<character>", "outfit_name": "<outfit_name>"},
    ...
    ]

    4. DO NOT repeat full descriptions inside shot objects — only reference the outfit name.
    5. Ensure consistency: The same outfit name must have the same description everywhere.



 **Character Extraction**:
   - Identify ALL unique characters in the script
   - Provide detailed descriptions including:
     * Name (lowercase)
     * Approximate age
     * Role in the ad
     * Gender
     * Description in description you should mention ethinicity,skin tone,face structure,hair,outfit choose mostly used from script,pose always standing upright, full body view and background white
   - Characters should be consistent across shots

HERE IS THE EXAMPLE OF CHARACTER INFO:
    name:ajay
    age:20
    role:hero
    gender:male
    overall_description: Ethnicity: South Indian, Skin tone: Warm medium brown, golden undertones, healthy complexion,Face: Oval face, expressive almond-shaped dark brown eyes, slightly arched brows, medium lips, natural look,Hair :Long, dark brown hair, Outfit & Styling: Use common in the script, Pose & Expression :Standing straight, front-facing, full body, Lighting & Background :Neutral indoor studio lighting (soft, flattering) Clean white background (AI consistency, no distractions)

**Location Extraction**:
   - Identify ALL unique location in the script
   - Provide detailed descriptions of the location:
     * Name (lowercase)
     * description detailed description of the location in detail like( Location Type: [What place is it]
                                        Design Style & Mood: [Modern / Minimal / Classic / Luxury, emotional feel]
                                        Key Architectural Elements: [Describe surfaces, fixtures, layout]
                                        Color Palette & Materials: [Dominant tones + key materials]
                                        Props & Visual Details: [List clearly visible objects]
                                        Lighting: [Natural or artificial + brightness + source direction]
                                        Atmosphere & Vibe: [Emotional tone or story feeling]
                                        Camera Framing Note: [Wide / Medium / Close / OTS / POV]
                                        )

HERE IS THE EXAMPLE OF LOCATION INFO:
name: hotel(lowercase)
overall_description: Location Type: Hotel Room (Morning),Design Style & Mood: Minimal modern Indian, soft and calm mood,Key Architectural Elements: Light wooden furniture, soft beige curtains, neutral wall tones, Color Palette & Materials: Warm beige, soft white, natural wood, cotton bedding,Props & Visual Details: Cricket duffel bag by bedside, water bottle, sports shoes, framed art on wall,Lighting: Soft natural morning light filtering through curtains, warm gentle shadows


HERE IS THE EXAMPLE OF CHARACTER OUTFIT INFO:
Format for outfit information for the character
outfit_name:priya_casual_outfit(lowercase)
outfit_description:[Outfit Type], Top: [Item, Color, Fabric, Fit], Bottom: [Item, Color, Fabric, Fit], Footwear: [Item, Color, Style], Accessories: [List], Style Inspiration: [Mood/Reference], Condition: [New/Worn], Context: [Scene Usage]

Example Description:
Athleisure casual, Top: performance t-shirt, muted charcoal gray, lightweight stretch fabric, athletic fit; Bottom: navy training joggers, soft knit, slim tapered fit; Footwear: white running shoes, clean minimal design; Accessories: black sports watch; Style Inspiration: disciplined minimal sports aesthetic; Condition: clean and well-kept; Context: early morning pre-match indoor preparation.



Shot types to consider:
- Establishing shots (wide)
- Close-ups (product, face, details)
- Medium shots (action, interaction)
- POV shots (perspective)
- Over-the-shoulder
- Tracking/following shots
- Static vs. dynamic camera work

Your Response should include:

ad_title: title of the ad
total_duration:
shot: list of shots
characters_info:list of detailed description of the characters in this script
location_info: list of detailed information of the location in this script
character_outfit_info list of detailed description of the outfit for all unique outfit
"""

    def generate_shot_script(
        self, 
        ad_concept: Dict[str, Any],
        brand_info:Optional,
        duration: int= 15,
        
    ) -> ShotScript:
        """
        Generate detailed shot-level script from ad concept
        
        Args:
            ad_concept: Dictionary containing ad concept details (can be AdConcept.model_dump())
            target_duration: Target duration for the ad
            
        Returns:
            ShotScript object with complete shot breakdown
        """
        system_prompt = self.create_shot_script_system_prompt()
        
        user_prompt = f"""Convert the following ad concept into a detailed shot-by-shot script.

Ad Concept:
{json.dumps(ad_concept, indent=2)}

Target Duration: {duration} sec

this is the Brand info {json.dumps(brand_info, indent=2)}

Requirements:
- Break down the story into 8-15 shots
- Each shot should advance the narrative
- Include proper establishing shots
- Showcase product features clearly
- Build to the tagline/message
- Ensure timestamps are sequential and accurate
- Be specific about every detail

Follow the visual flow from the concept and expand it into precise, producible shots.
Make sure each shot has ALL required fields filled out properly.

Return a complete shot script in valid JSON format matching the ShotScript schema."""

        try:
            messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
            ]
            self.llm=self.llm.with_structured_output(ShotScript)
            shot_script = self.llm.invoke(messages)

            print(shot_script)
            
            
            print(f"✓ Successfully generated {len(shot_script.shots)} shots for '{shot_script.ad_title}'")
            return shot_script
            
        except Exception as e:
            print(f"Error generating shot script: {str(e)}")
            raise

    def save_shot_script_json(
        self, 
        shot_script: ShotScript, 
        output_file: str, 
        output_dir: str = "projects_data"
    ):
        """Save shot script to JSON file"""
        script_dict = shot_script.model_dump()
        
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(script_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Shot script saved to {file_path}")
        return file_path

   

    def load_shot_script(self, file_path: str) -> ShotScript:
        """Load shot script from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return ShotScript(**data)

    def display_shot_script(self, shot_script: ShotScript):
        """Display formatted shot script"""
        print("\n" + "="*100)
        print(f"SHOT SCRIPT: {shot_script.ad_title}")
        print(f"Total Duration: {shot_script.total_duration}")
        print("="*100 + "\n")

        print("-" * 100)
        print("CHARACTERS:")
        print("-" * 100)
        for char in shot_script.characters_info:
            print(f"\n{char.name.upper()}")
            print(f"  Role: {char.role}")
            print(f"  Age: {char.age}, Gender: {char.gender}")
            print(f"  Description: {char.overall_description}")

        print("LOCATION:")
        print("-" * 100)
        for char in shot_script.characters_info:
            print(f"\n{char.name.upper()}")
            print(f"  Description: {char.overall_description}")
        
        
        for shot in shot_script.shots:
            print(f"\n{'─'*100}")
            print(f"SHOT {shot.shot_no} | {shot.duration} | {shot.time_stamp}")
            print(f"{'─'*100}")
            print(f"📍 Location: {shot.location}")
            print(f"🎥 Camera: {shot.camera_angle}")
            print(f"👁️  Visual: {shot.visual_description}")
            print(f"🎬 Action: {shot.action}")
            print(f"🔊 Audio/SFX: {shot.audio_sfx}")
            if shot.dialogue and shot.dialogue != "None":
                print(f"💬 Dialogue: {shot.dialogue}")
            if shot.voice_over and shot.voice_over != "None":
                print(f"🎙️  Voice Over: {shot.voice_over}")
            if shot.text_overlay and shot.text_overlay != "None":
                print(f"📝 Text Overlay: {shot.text_overlay}")
            print(f"🎯 Key Focus: {shot.key_focus}")
        
        print("\n" + "="*100 + "\n")

    



# if __name__ == "__main__":
#     # Example: Load a previously generated ad concept
#     ad_concept_example = {
#         "title": "The Captain's Pre-Match Ritual",
#         "one_line_summary": "Dhoni's calm morning routine - applying sunscreen is as essential as checking his bat",
#         "story": "In the quiet hours before a crucial match, MS Dhoni follows his meticulous routine. He checks his bat, packs his kit, and applies Deconstruct gel sunscreen with the same calm focus he brings to captaincy. As he walks out to the toss under harsh stadium lights, his face shows no sweat shine - just confidence and preparation.",
#         "visual_flow": {
#             "Opening": "Dhoni in hotel room, early morning light",
#             "Sequence": "Checking bat → packing kit → Applying Deconstruct gel sunscreen calmly",
#             "Stadium": "Walking out to toss under harsh sun, confident and protected",
#             "Close-up": "Face showing no sweat shine, matte finish despite heat"
#         },
#         "voice_over": "Champions prepare for everything. Even the sun.",
#         "tagline": "Dhoni's choice. Captain Cool stays protected.",
#         "key_message": "Preparation and attention to detail, like Dhoni's captaincy style",
#         "key_features": [
#             "SPF 55 protection",
#             "Matte finish",
#             "Sweat-resistant",
#             "No white cast"
#         ],
#         "tone": "Inspirational, authentic",
#     }
    
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
#     generator = ShotScriptGenerator()
    
#     # Generate shot script
#     shot_script = generator.generate_shot_script(ad_concept_example,brand_info)
    
#     # Display the script
#     generator.display_shot_script(shot_script)
    
#     # Save as JSON
#     generator.save_shot_script_json(shot_script, "shot_script_generated.json")
    
