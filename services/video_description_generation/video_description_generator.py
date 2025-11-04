from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv
from utils.llm import get_llm_model


load_dotenv()

llm_client = get_llm_model("gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


class StandardVideoPrompt(BaseModel):
    """Standard video prompt for regular shots"""
    shot_no: int = Field(description="Shot number")
    camera_angle: str = Field(description="Detailed camera angle, movement, and lens specifications")
    scene_description: str = Field(description="Detailed description of action and how it should be performed")
    lighting: str = Field(description="Detailed lighting setup, color temperature, and mood")
    dialogue: Optional[str] = Field(default="", description="Exact dialogue if present")
    voice_over: Optional[str] = Field(default="", description="Voice over narration with voice type")
    additional_notes: str = Field(description="Music, sound design, audio SFX, animation notes, key focus")


class AnimatedProductShowcasePrompt(BaseModel):
    """Animated video prompt for product showcase with first and last frame"""
    shot_no: int = Field(description="Shot number")
    camera_angle: str = Field(description="Dynamic camera angle with movement description")
    scene_description: str = Field(description="Detailed animation from first frame to last frame transformation")
    lighting: str = Field(description="Dynamic lighting throughout animation")
    dialogue: Optional[str] = Field(default="", description="Exact dialogue if present")
    voice_over: Optional[str] = Field(default="", description="Voice over narration with voice type")
    additional_notes: str = Field(description="Animation details, text animations, effects, and transitions")
    requires_two_frames: bool = Field(default=True, description="Indicates this needs first and last frame images")


class VideoPrompt(BaseModel):
    """Container for either standard or animated video prompt"""
    shot_no: int
    prompt_type: str = Field(description="Either 'standard' or 'animated_showcase'")
    standard_prompt: Optional[StandardVideoPrompt] = None
    animated_prompt: Optional[AnimatedProductShowcasePrompt] = None


class VideoDescription(BaseModel):
    """Complete video description for all shots"""
    ad_title: str
    total_shots: int
    video_prompts: List[VideoPrompt]


class VideoDescriptionGenerator:
    def __init__(self):
        self.llm = llm_client
    
    def create_video_prompt_system_prompt(self) -> str:
        """Create system prompt for generating video prompts"""
        return """You are an expert video director and cinematographer specializing in commercial video production for AI video generation models like Google Veo 3.

Your task is to create HIGHLY DETAILED video generation prompts that can be used with image-to-video AI models.

There are TWO types of video prompts you need to generate:

═══════════════════════════════════════════════════════════════════════════════
TYPE 1: STANDARD VIDEO PROMPT (for regular shots)
═══════════════════════════════════════════════════════════════════════════════

Structure:
{
  "camera_angle": "Detailed camera specifications with movement",
  "scene_description": "Detailed action and performance description",
  "lighting": "Complete lighting setup with technical details",
  "dialogue": "Exact dialogue if present (empty string if none)",
  "voice_over": "Voice over with voice type specification (empty string if none)",
  "additional_notes": "Music, sound design, audio SFX, key focus"
}

Guidelines for Standard Prompts:
- Camera Angle: Specify shot type (wide/medium/close-up), camera movement (static/pan/tilt/dolly/tracking), lens (24mm/35mm/50mm/85mm), and any special techniques
- Scene Description: Describe character actions, movements, expressions, interactions in detail. Be specific about timing and pacing
- Lighting: Include light direction, intensity, color temperature (in Kelvin), shadow details, fill light, practical lights, mood
- Dialogue: Include exact spoken words with quotation marks. Leave empty if no dialogue
- Voice Over: Include VO text with voice type (e.g., "in Indian male voice", "in Indian female voice", "in calm narrator voice"). Leave empty if no VO
- Additional Notes: Background sounds, music type/mood, SFX (footsteps, door sounds, etc.), animation requirements, visual effects, key focus of the shot

Example Standard Prompt:
{
  "camera_angle": "Wide shot transitioning smoothly to medium close-up on the man, using a 50mm lens for shallow depth and background compression",
  "scene_description": "He walks confidently towards the pitch under bright, harsh sunlight. He squints briefly at the sun, smiles slightly, adjusts his cap, and says his line with calm confidence.",
  "lighting": "Direct bright sunlight creating strong highlights and subtle shadows on Dhoni's face; slight fill from reflector to maintain detail without flattening contrast; color temperature ~5600K to match daylight.",
  "dialogue": "I am protected.",
  "voice_over": "Champions prepare for everything. Even the sun. (in Indian female voice)",
  "additional_notes": "Stadium ambience with crowd murmurs and distant anthem; natural outdoor acoustics; emphasize confident walk and subtle smile; background should have soft stadium blur"
}

═══════════════════════════════════════════════════════════════════════════════
TYPE 2: ANIMATED PRODUCT SHOWCASE PROMPT (for final product shot)
═══════════════════════════════════════════════════════════════════════════════

This type is ONLY used when:
- It's the FINAL shot of the ad
- It's a product showcase shot
- Animation is requested
- Two frames will be provided (first frame and last frame)

Structure:
{
  "camera_angle": "Dynamic camera movement from start to end position",
  "scene_description": "Detailed animation transformation from first frame to last frame",
  "lighting": "Dynamic lighting changes throughout animation",
  "dialogue": "Exact dialogue if present (empty string if none)",
  "voice_over": "Voice over with voice type (empty string if none)",
  "additional_notes": "Detailed animation breakdown, text animations frame by frame, effects",
  "requires_two_frames": true
}

Guidelines for Animated Showcase Prompts:
- Camera Angle: Describe camera movement path from start to end (e.g., "low-to-mid angle starting from ground level moving upward")
- Scene Description: Describe the complete transformation - what's visible at the start, how it transitions, what's visible at the end. Be specific about animation flow
- Lighting: Describe how lighting evolves during the animation, including any dynamic effects like lens flares, highlights, shadows
- Additional Notes: CRITICAL - Must include:
  * Animation transition details (speed, easing, motion blur)
  * Text overlay animations IN DETAIL (each text element individually with animation type, timing, position)
  * Visual effects (lens flares, glows, reflections, particles)
  * Product highlighting techniques
  * Background animation if any

Example Animated Showcase Prompt:
{
  "camera_angle": "Dynamic low-to-mid angle starting from ground level moving upward and forward toward the product, using a 35mm lens for smooth perspective and natural depth",
  "scene_description": "Animation begins from the ground with a blurred stadium floor and a faint Deconstruct logo on the surface. The camera smoothly rises and transitions to reveal the Deconstruct Gel Sunscreen tube prominently on the center-right. The modern IPL stadium is bright with warm sunlight streaming from the top-left, creating subtle lens flares and golden highlights. Blurred cheering crowd and stadium details provide energetic context. Reflections under the product add realism, and the product remains the visual centerpiece throughout.",
  "lighting": "Dynamic sunlight from top-left creating warm highlights and lens flares; soft rim lighting on product edges; subtle shadows under the product for grounding; color temperature ~5600K for natural sunlight; gradient highlights in yellow, orange, and soft white building in intensity as camera rises.",
  "dialogue": "",
  "voice_over": "Stay Protected with Deconstruct Gel Sunscreen. (in Indian male voice)",
  "additional_notes": "Transition animation from ground to product showcase over 3 seconds with golden highlights and subtle motion blur; animate each text overlay individually: 
1. 'IPL Season Begins.' – bold energetic yellow font, slightly italicized, appearing left of bottle with slide-in from left + fade effect (0.5s delay from start)
2. 'Stay Protected.' – bold black modern sans serif with soft shadow, appearing right of bottle with upward fade-in (1.0s delay)
3. 'Deconstruct' – black thin serif (Didot/Bodoni), spaced wide, animating from top downward to slightly above product (1.5s delay)
4. 'Gel Sunscreen' – modern sans serif light gray with subtle underline, sliding up from below brand name (2.0s delay)
5. 'SPF 55+ | PA+++' – monospaced metallic silver, bottom-right alignment, fading in with gentle glow (2.5s delay)
Include subtle product reflections and golden rim lighting throughout; background maintains modern IPL editorial vibe with slight atmospheric blur; add subtle sparkle effects on product surface"
}

═══════════════════════════════════════════════════════════════════════════════
IMPORTANT RULES:
═══════════════════════════════════════════════════════════════════════════════

1. Choose the correct prompt type:
   - Use STANDARD for all regular shots (99% of shots)
   - Use ANIMATED SHOWCASE only for final product showcase shots when animation is requested

2. Do not include celebrity name this is the main requirement and write a safe prompt avoid unsafe words

2. Be extremely specific and detailed in all descriptions
3. Include technical specifications (focal length, color temperature, etc.)
4. Describe timing and pacing clearly
5. For animated prompts, break down the animation step-by-step
6. Always specify voice type for voice overs (Indian male/female/neutral)
7. Leave dialogue and voice_over as empty strings if not present (not "None" or null)
8. Additional notes should be comprehensive - include ALL audio, visual effects, and timing details

Your prompts will be used directly by AI video generation models, so clarity and detail are critical.
"""

    def generate_video_prompt_for_shot(
        self,
        shot: Dict[str, Any],
        is_final_shot: bool = False,
        enable_animation: bool = False
    ) -> VideoPrompt:
        """
        Generate video prompt for a single shot
        
        Args:
            shot: Shot dictionary with all shot information
            is_final_shot: Whether this is the final shot
            enable_animation: Whether to generate animated showcase (only for final product shots)
            
        Returns:
            VideoPrompt object
        """
        shot_no = shot.get('shot_no', 0)
        
        # Determine prompt type
        is_product_showcase = (
            is_final_shot and 
            shot.get('product_image_required', False) and 
            shot.get('text_overlay') and 
            shot.get('text_overlay') != "None"
        )
        
        prompt_type = "animated_showcase" if (is_product_showcase and enable_animation) else "standard"
        
        system_prompt = self.create_video_prompt_system_prompt()
        
        # Extract shot information
        shot_info = f"""
Shot Number: {shot.get('shot_no', 'N/A')}
Duration: {shot.get('duration', 'N/A')}
Time Stamp: {shot.get('time_stamp', 'N/A')}
Location: {shot.get('location', 'N/A')}
Camera Angle: {shot.get('camera_angle', 'N/A')}
Visual Description: {shot.get('visual_description', 'N/A')}
Action: {shot.get('action', 'N/A')}
Objects/Props Involved: {shot.get('objects_props_involved', 'N/A')}
Audio/SFX: {shot.get('audio_sfx', 'N/A')}
Dialogue: {shot.get('dialogue', 'None')}
Voice Over: {shot.get('voice_over', 'None')}
Text Overlay: {shot.get('text_overlay', 'None')}
Key Focus: {shot.get('key_focus', 'N/A')}
Product Image Required: {shot.get('product_image_required', False)}
Characters Involved: {', '.join(shot.get('characters_involved', []))}
"""

        if prompt_type == "standard":
            user_prompt = f"""Generate a STANDARD video prompt for this shot:

{shot_info}

Create a detailed standard video prompt that includes:
1. Camera angle with technical specifications
2. Detailed scene description with actions and performances
3. Complete lighting setup
4. Exact dialogue (empty string if none)
5. Voice over with voice type (empty string if none)
6. Comprehensive additional notes with audio, SFX, and key focus

Return in StandardVideoPrompt format."""

            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                
                structured_llm = self.llm.with_structured_output(StandardVideoPrompt)
                standard_prompt = structured_llm.invoke(messages)
                
                return VideoPrompt(
                    shot_no=shot_no,
                    prompt_type="standard",
                    standard_prompt=standard_prompt,
                    animated_prompt=None
                )
                
            except Exception as e:
                print(f"Error generating standard video prompt for shot {shot_no}: {e}")
                raise
        
        else:  # animated_showcase
            user_prompt = f"""Generate an ANIMATED PRODUCT SHOWCASE video prompt for this FINAL shot:

{shot_info}

This is a product showcase shot that requires animation between two frames (first frame and last frame).

Create a detailed animated showcase prompt that includes:
1. Dynamic camera movement from start to end
2. Complete animation transformation description (what happens from first frame to last frame)
3. Dynamic lighting evolution during animation
4. Exact dialogue (empty string if none)
5. Voice over with voice type (empty string if none)
6. DETAILED additional notes including:
   - Animation transition details (timing, easing, effects)
   - Individual text overlay animations (each text element with specific animation type, timing, position)
   - Visual effects (lens flares, glows, reflections, highlights)
   - Product highlighting techniques
   - Background animation details

CRITICAL: Text overlay animations must be broken down individually for each text element from the text_overlay field.

Return in AnimatedProductShowcasePrompt format."""

            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                structured_llm= self.llm.with_structured_output(AnimatedProductShowcasePrompt)
                animated_prompt = structured_llm.invoke(messages)
                
                return VideoPrompt(
                    shot_no=shot_no,
                    prompt_type="animated_showcase",
                    standard_prompt=None,
                    animated_prompt=animated_prompt
                )
                
            except Exception as e:
                print(f"Error generating animated video prompt for shot {shot_no}: {e}")
                raise
    
    def generate_video_descriptions(
        self,
        shots: List[Dict[str, Any]],
        ad_title: str,
        enable_animation_for_finale: bool = True
    ) -> VideoDescription:
        """
        Generate video prompts for all shots
        
        Args:
            shots: List of shot dictionaries
            ad_title: Title of the ad
            enable_animation_for_finale: Whether to enable animation for final product showcase
            
        Returns:
            VideoDescription with all video prompts
        """
        print("\n" + "="*100)
        print(f"GENERATING VIDEO DESCRIPTIONS - {ad_title}")
        print("="*100 + "\n")
        
        video_prompts = []
        total_shots = len(shots)
        
        for idx, shot in enumerate(shots, 1):
            shot_no = shot.get('shot_no', idx)
            is_final = (idx == total_shots)
            
            print(f"\n[Shot {shot_no}/{total_shots}] Generating video prompt...")
            
            video_prompt = self.generate_video_prompt_for_shot(
                shot=shot,
                is_final_shot=is_final,
                enable_animation=enable_animation_for_finale
            )
            
            video_prompts.append(video_prompt)
            
            prompt_type_label = "ANIMATED SHOWCASE" if video_prompt.prompt_type == "animated_showcase" else "STANDARD"
            print(f"✓ Generated {prompt_type_label} video prompt for shot {shot_no}")
        
        video_description = VideoDescription(
            ad_title=ad_title,
            total_shots=total_shots,
            video_prompts=video_prompts
        )
        
        print("\n" + "="*100)
        print(f"✓ Video descriptions complete for all {total_shots} shots!")
        print("="*100 + "\n")
        
        return video_description
    
    def save_video_descriptions(
        self,
        video_description: VideoDescription,
        output_file: str,
        output_dir: str = "projects_data"
    ):
        """Save video descriptions to JSON file"""
        video_dict = video_description.model_dump()
        
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Video descriptions saved to {file_path}")
        return file_path
    
    def export_video_prompts_readable(
        self,
        video_description: VideoDescription,
        output_file: str,
        output_dir: str = "projects_data"
    ):
        """Export video prompts in human-readable format"""
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"VIDEO PROMPTS FOR: {video_description.ad_title}\n")
            f.write("="*100 + "\n\n")
            
            for video_prompt in video_description.video_prompts:
                f.write(f"{'═'*100}\n")
                f.write(f"SHOT {video_prompt.shot_no} - {video_prompt.prompt_type.upper()}\n")
                f.write(f"{'═'*100}\n\n")
                
                if video_prompt.prompt_type == "standard" and video_prompt.standard_prompt:
                    prompt = video_prompt.standard_prompt
                    f.write(f"Camera Angle:\n{prompt.camera_angle}\n\n")
                    f.write(f"Scene Description:\n{prompt.scene_description}\n\n")
                    f.write(f"Lighting:\n{prompt.lighting}\n\n")
                    
                    if prompt.dialogue:
                        f.write(f"Dialogue:\n\"{prompt.dialogue}\"\n\n")
                    
                    if prompt.voice_over:
                        f.write(f"Voice Over:\n{prompt.voice_over}\n\n")
                    
                    f.write(f"Additional Notes:\n{prompt.additional_notes}\n\n")
                
                elif video_prompt.prompt_type == "animated_showcase" and video_prompt.animated_prompt:
                    prompt = video_prompt.animated_prompt
                    f.write(f"⚠️ REQUIRES TWO FRAMES: First Frame + Last Frame\n\n")
                    f.write(f"Camera Angle (Dynamic):\n{prompt.camera_angle}\n\n")
                    f.write(f"Scene Description (Animation):\n{prompt.scene_description}\n\n")
                    f.write(f"Lighting (Dynamic):\n{prompt.lighting}\n\n")
                    
                    if prompt.dialogue:
                        f.write(f"Dialogue:\n\"{prompt.dialogue}\"\n\n")
                    
                    if prompt.voice_over:
                        f.write(f"Voice Over:\n{prompt.voice_over}\n\n")
                    
                    f.write(f"Additional Notes (Animation Details):\n{prompt.additional_notes}\n\n")
                
                f.write("\n")
        
        print(f"✓ Readable video prompts exported to {file_path}")
        return file_path
    
    def display_video_descriptions_summary(self, video_description: VideoDescription):
        """Display summary of video descriptions"""
        print("\n" + "="*100)
        print(f"VIDEO DESCRIPTIONS SUMMARY - {video_description.ad_title}")
        print("="*100 + "\n")
        
        print(f"Total Shots: {video_description.total_shots}\n")
        
        standard_count = sum(1 for vp in video_description.video_prompts if vp.prompt_type == "standard")
        animated_count = sum(1 for vp in video_description.video_prompts if vp.prompt_type == "animated_showcase")
        
        print(f"Standard Prompts: {standard_count}")
        print(f"Animated Showcase Prompts: {animated_count}\n")
        
        for video_prompt in video_description.video_prompts:
            print(f"\n{'─'*100}")
            print(f"SHOT {video_prompt.shot_no} - {video_prompt.prompt_type.upper()}")
            print(f"{'─'*100}")
            
            if video_prompt.prompt_type == "standard" and video_prompt.standard_prompt:
                prompt = video_prompt.standard_prompt
                print(f"Camera: {prompt.camera_angle[:80]}...")
                print(f"Scene: {prompt.scene_description[:80]}...")
                if prompt.dialogue:
                    print(f"Dialogue: \"{prompt.dialogue}\"")
                if prompt.voice_over:
                    print(f"VO: {prompt.voice_over[:60]}...")
            
            elif video_prompt.prompt_type == "animated_showcase" and video_prompt.animated_prompt:
                prompt = video_prompt.animated_prompt
                print(f"⚠️ ANIMATED - Requires 2 frames")
                print(f"Camera: {prompt.camera_angle[:80]}...")
                print(f"Animation: {prompt.scene_description[:80]}...")
                if prompt.voice_over:
                    print(f"VO: {prompt.voice_over[:60]}...")
        
        print("\n" + "="*100 + "\n")
    
    def load_video_descriptions(self, file_path: str) -> VideoDescription:
        """Load video descriptions from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return VideoDescription(**data)


# # ============================================================================
# # STANDALONE TESTING
# # ============================================================================

# if __name__ == "__main__":
#     print("\n" + "="*100)
#     print("VIDEO DESCRIPTION GENERATOR - STANDALONE TEST")
#     print("="*100)
    
#     # Example shots data (you can load from your shot script JSON)
#     example_shots = [
#         {
#             "shot_no": 1,
#             "duration": "3 seconds",
#             "time_stamp": "00:00-00:03",
#             "location": "Hotel room, morning light",
#             "location_name": "hotel room",
#             "camera_angle": "Medium shot",
#             "visual_description": "Dhoni sits on bed, checking his cricket bat carefully",
#             "action": "Dhoni examines bat, running fingers along the edge, checking balance",
#             "objects_props_involved": "Cricket bat (worn leather grip, slight scratches), cricket kit bag (CSK blue and yellow), water bottle on nightstand",
#             "audio_sfx": "Soft morning ambience, distant birds chirping",
#             "dialogue": "None",
#             "voice_over": "None",
#             "text_overlay": "None",
#             "key_focus": "Establish Dhoni's meticulous preparation routine",
#             "product_image_required": False,
#             "characters_involved": ["dhoni"],
#             "outfit_character_mapping": []
#         },
        
#         {
#             "shot_no": 8,
#             "duration": "5 seconds",
#             "time_stamp": "00:25-00:30",
#             "location": "Modern studio background with IPL stadium blur",
#             "location_name": "stadium",
#             "camera_angle": "Center product shot",
#             "visual_description": "Deconstruct Gel Sunscreen showcased with text overlays and IPL branding",
#             "action": "Static product display with dynamic lighting and text animations",
#             "objects_props_involved": "Deconstruct Gel Sunscreen tube prominently displayed",
#             "audio_sfx": "Upbeat music crescendo, stadium crowd cheers fading in",
#             "dialogue": "None",
#             "voice_over": "Even the sun.",
#             "text_overlay": "IPL Season Begins. Stay Protected. | Deconstruct | Gel Sunscreen | SPF 55+ | PA+++",
#             "key_focus": "Final product showcase with brand message",
#             "product_image_required": True,
#             "characters_involved": [],
#             "outfit_character_mapping": []
#         }
#     ]
    
#     # Initialize generator
#     generator = VideoDescriptionGenerator()
    
#     # Test 1: Generate video descriptions with animation enabled
#     print("\n" + "─"*100)
#     print("TEST 1: Generating video descriptions with animation for finale")
#     print("─"*100)
    
#     video_descriptions = generator.generate_video_descriptions(
#         shots=example_shots,
#         ad_title="The Captain's Pre-Match Ritual",
#         enable_animation_for_finale=True
#     )
    
#     # Display summary
#     generator.display_video_descriptions_summary(video_descriptions)
    
#     # Save to files
#     json_path = generator.save_video_descriptions(
#         video_descriptions,
#         "video_descriptions_test.json",
#         "test_output"
#     )
    
#     readable_path = generator.export_video_prompts_readable(
#         video_descriptions,
#         "video_prompts_readable_test.txt",
#         "test_output"
#     )
    
#     print("\n" + "─"*100)
#     print("TEST 2: Generating video descriptions WITHOUT animation")
#     print("─"*100)
    
#     video_descriptions_no_anim = generator.generate_video_descriptions(
#         shots=example_shots,
#         ad_title="The Captain's Pre-Match Ritual",
#         enable_animation_for_finale=False
#     )
    
#     generator.display_video_descriptions_summary(video_descriptions_no_anim)
    
#     # Save without animation
#     generator.save_video_descriptions(
#         video_descriptions_no_anim,
#         "video_descriptions_no_animation_test.json",
#         "test_output"
#     )
    
#     generator.export_video_prompts_readable(
#         video_descriptions_no_anim,
#         "video_prompts_no_animation_readable_test.txt",
#         "test_output"
#     )
    
#     print("\n" + "="*100)
#     print("✅ VIDEO DESCRIPTION GENERATOR TEST COMPLETE!")
#     print("="*100)
#     print(f"\nGenerated files:")
#     print(f"  - {json_path}")
#     print(f"  - {readable_path}")
#     print(f"\nCheck the 'test_output' directory for results.")