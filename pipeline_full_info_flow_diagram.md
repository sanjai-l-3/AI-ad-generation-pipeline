┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AD GENERATION PIPELINE                                  │
│                     From Concept to Final Video                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

INPUT: Brand Info + Ad Concept
│
├─> Brand Information
│   ├─ Brand Name
│   ├─ Product Name & Description
│   ├─ Key Features
│   ├─ Target Audience
│   ├─ Campaign Objective
│   └─ Product Image
│
└─> Ad Concept
    ├─ Title
    ├─ One-line Summary
    ├─ Story
    ├─ Visual Flow
    ├─ Voice Over
    ├─ Tagline
    └─ Key Message

═══════════════════════════════════════════════════════════════════════════════════
STAGE 1: AD CONCEPT GENERATION (Optional - if not provided)
═══════════════════════════════════════════════════════════════════════════════════

[AdConceptGenerator]
│
├─> Input: Brand Info
│
├─> Process: LLM generates 5-6 ad concept variations
│   ├─ Different creative angles (lifestyle, problem-solution, celebrity, emotional, humorous)
│   ├─ Each with complete story, visual flow, tagline
│   └─ Tone and duration specified
│
└─> Output: 
    ├─ ad_concepts.json (5-6 variations)
    └─ User selects ONE concept to proceed

═══════════════════════════════════════════════════════════════════════════════════
STAGE 2: SHOT SCRIPT GENERATION
═══════════════════════════════════════════════════════════════════════════════════

[ShotScriptGenerator]
│
├─> Input: Selected Ad Concept + Brand Info + Duration (15/30/45/60 sec)
│
├─> Process: LLM breaks down concept into shot-by-shot script
│   ├─ Analyzes story and creates 8-18 shots
│   ├─ Each shot includes:
│   │   ├─ Shot number, duration, timestamp
│   │   ├─ Location (description + name)
│   │   ├─ Camera angle & visual description
│   │   ├─ Action & objects/props
│   │   ├─ Audio/SFX, dialogue, voice-over
│   │   ├─ Text overlay & key focus
│   │   ├─ Product image required (bool)
│   │   ├─ Characters involved (list)
│   │   └─ Outfit-character mapping (list)
│   │
│   ├─ Extracts ALL unique CHARACTERS:
│   │   ├─ Name, age, gender, role
│   │   └─ Detailed physical description
│   │
│   ├─ Extracts ALL unique LOCATIONS:
│   │   ├─ Name (lowercase)
│   │   └─ Detailed description (design, mood, elements, lighting)
│   │
│   └─ Extracts ALL unique OUTFITS:
│       ├─ Outfit name (lowercase)
│       └─ Detailed outfit description (type, colors, fabric, style, fit, accessories)
│
└─> Output:
    ├─ {project}_shot_script.json
    ├─ {project}_shot_script.csv (for review/editing)
    └─ Contains: shots[], characters_info[], location_info[], character_outfit_info[]

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 3: CHARACTER IMAGE GENERATION
═══════════════════════════════════════════════════════════════════════════════════

[CharacterGenerator]
│
├─> Input: characters_info[] from shot script
│
├─> Process: For EACH character
│   ├─ Creates detailed prompt:
│   │   ├─ Age, gender, ethnicity, skin tone
│   │   ├─ Face structure, hair, distinctive features
│   │   ├─ Standing upright, full body, white background
│   │   └─ Based on overall_description from shot script
│   │
│   ├─ Generates image using Gemini 2.5 Flash Image Preview
│   │   └─ If fails: tries simpler prompt → creates placeholder
│   │
│   └─ Generates reference description:
│       ├─ Uses Gemini to analyze generated image
│       ├─ Extracts: gender + outfit in image + distinctive feature
│       └─ Short 2-3 line description for scene prompts
│
└─> Output:
    ├─ character_images/{char_name}_character.png (for each character)
    ├─ {project}_characters.json (with image_path + reference_description)
    └─ Updates shot_script with character image paths

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 4: LOCATION IMAGE GENERATION
═══════════════════════════════════════════════════════════════════════════════════

[LocationGenerator]
│
├─> Input: location_info[] from shot script
│
├─> Process: For EACH location
│   ├─ Parses structured description:
│   │   ├─ Location type
│   │   ├─ Design style & mood
│   │   ├─ Key architectural elements
│   │   ├─ Color palette & materials
│   │   ├─ Props & visual details
│   │   ├─ Lighting (natural/artificial)
│   │   ├─ Atmosphere & vibe
│   │   └─ Camera framing
│   │
│   ├─ Creates detailed cinematic prompt
│   ├─ Generates EMPTY location (no people) using Gemini
│   └─ If fails: simpler prompt → placeholder
│
└─> Output:
    ├─ location_images/{location_name}_location.png (for each location)
    ├─ {project}_locations.json (with image_path)
    └─ Updates shot_script with location image paths

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 5: OUTFIT IMAGE GENERATION
═══════════════════════════════════════════════════════════════════════════════════

[OutfitGenerator]
│
├─> Input: character_outfit_info[] from shot script
│
├─> Process: For EACH outfit
│   ├─ Parses outfit description:
│   │   ├─ Outfit type (casual/formal/sports)
│   │   ├─ Top: item, color, fabric, fit
│   │   ├─ Bottom: item, color, fabric, fit
│   │   ├─ Footwear: item, color, style
│   │   ├─ Accessories
│   │   ├─ Style inspiration
│   │   └─ Condition & context
│   │
│   ├─ Creates professional catalog-style prompt
│   ├─ Generates outfit on white background using Gemini
│   │   ├─ Flat lay OR invisible mannequin style
│   │   └─ All items arranged proportionally
│   └─ If fails: simpler prompt → placeholder
│
└─> Output:
    ├─ outfit_images/{outfit_name}_outfit.png (for each outfit)
    ├─ {project}_outfits.json (with image_path)
    └─ Updates shot_script with outfit image paths

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 6: CHARACTER-OUTFIT COMBINATION GENERATION ⭐ KEY FOR CONSISTENCY
═══════════════════════════════════════════════════════════════════════════════════

[CharacterOutfitGenerator]
│
├─> Input: 
│   ├─ characters_info[] (with image paths)
│   ├─ character_outfit_info[] (with image paths)
│   └─ shots[] (to identify required combinations)
│
├─> Process:
│   ├─ Scans ALL shots to find unique character-outfit pairs
│   │   └─ From outfit_character_mapping in each shot
│   │
│   ├─ For EACH unique combination (e.g., "priya_casual_morning"):
│   │   ├─ Loads character reference image
│   │   ├─ Creates prompt: "Generate [character] wearing [outfit description]"
│   │   │   ├─ CRITICAL: Keep EXACT facial features from reference
│   │   │   ├─ Only change the outfit
│   │   │   ├─ Full body, front-facing, white background
│   │   │   └─ Standing pose, neutral expression
│   │   │
│   │   ├─ Generates using Gemini with character reference
│   │   └─ Saves as: {character}_{outfit}.png
│   │
│   └─ Creates lookup: character_outfit combinations
│
└─> Output:
    ├─ character_outfit_images/{char}_{outfit}.png (for each combo)
    ├─ {project}_character_outfits.json (mapping file)
    └─ Example: priya_casual_morning.png, priya_beach_outfit.png, rahul_sports_wear.png

💡 WHY THIS STAGE IS CRITICAL:
   - Character face + outfit are BOTH correct in ONE reference image
   - Scene generation just needs to place this combo in the location
   - Massively improves character consistency across shots
   - Simplifies scene generation (less to process)

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 7: SCENE DESCRIPTION GENERATION (Image Prompts)
═══════════════════════════════════════════════════════════════════════════════════

[SceneDescriptionGenerator]
│
├─> Input: 
│   ├─ shots[] from shot script
│   ├─ brand_info
│   ├─ characters_info[]
│   ├─ locations_info[]
│   ├─ ad_concept (optional)
│   └─ character_outfit_info[] (filtered per shot)
│
├─> Process: For EACH shot
│   │
│   ├─ Filters outfits to only those used in THIS shot
│   │   └─ Based on outfit_character_mapping
│   │
│   ├─> LLM generates detailed image prompt:
│   │   │
│   │   ├─ Character descriptions:
│   │   │   ├─ References character-outfit image order
│   │   │   ├─ "Priya (first girl in char-outfit ref image)"
│   │   │   ├─ "Keep features and outfit exactly as shown"
│   │   │   ├─ Describes expression, action, position
│   │   │   └─ Handles same-gender differentiation
│   │   │
│   │   ├─ Location description:
│   │   │   ├─ References location by name
│   │   │   ├─ "Same environment as location ref for '{location_name}'"
│   │   │   └─ Additional spatial details
│   │   │
│   │   ├─ Product integration (if required):
│   │   │   ├─ Product name and description
│   │   │   ├─ Placement location
│   │   │   └─ "Same as product reference image"
│   │   │
│   │   ├─ Camera & framing details
│   │   ├─ Lighting (type, direction, color temp)
│   │   ├─ Mood & atmosphere
│   │   ├─ Action & interactions
│   │   ├─ Technical details (DoF, color grading)
│   │   │
│   │   └─ Special handling for FINAL PRODUCT SHOWCASE:
│   │       ├─ Elaborate product positioning
│   │       ├─ Dynamic lighting setup
│   │       ├─ Detailed text overlay layout specifications
│   │       ├─ Each text element: position, font, color, size, effects
│   │       └─ Atmospheric effects (lens flares, highlights)
│   │
│   └─ Stores image_prompt in shot object
│
└─> Output:
    ├─ {project}_scene_descriptions.json (all shots with image_prompt)
    ├─ {project}_image_prompts.txt (readable format)
    └─ Each shot now has: image_prompt field (150-600 words)

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 8: SCENE IMAGE GENERATION (Keyframes)
═══════════════════════════════════════════════════════════════════════════════════

[SceneImageGenerator]
│
├─> Input:
│   ├─ scene_descriptions (with image_prompts)
│   ├─ character_outfit_images[] (pre-generated combos)
│   ├─ locations_info[] (with image paths)
│   ├─ product_info (with image path, if needed)
│   └─ aspect_ratio (e.g., 16:9)
│
├─> Process: For EACH shot
│   │
│   ├─ Load reference images:
│   │   │
│   │   ├─ Character-outfit references:
│   │   │   ├─ Maps from outfit_character_mapping
│   │   │   ├─ Finds: {char_name}_{outfit_name}.png
│   │   │   └─ Loads PIL Image for each combo
│   │   │
│   │   ├─ Location reference:
│   │   │   ├─ Uses location_name to find exact location
│   │   │   └─ Loads location image
│   │   │
│   │   └─ Product reference (if required):
│   │       └─ Loads product image
│   │
│   ├─ Create enhanced prompt:
│   │   ├─ Base: image_prompt from scene description
│   │   ├─ Adds: reference image instructions
│   │   │   ├─ "Character-outfit ref 1: {char} wearing {outfit}"
│   │   │   ├─ "Keep exact features and outfit from reference"
│   │   │   ├─ "Location ref: match environment"
│   │   │   └─ "Product ref: match appearance"
│   │   └─ Aspect ratio specification
│   │
│   ├─ Prepare Gemini content:
│   │   ├─ [enhanced_prompt]
│   │   ├─ [char-outfit image 1]
│   │   ├─ [char-outfit image 2] (if multiple)
│   │   ├─ [location image]
│   │   └─ [product image] (if required)
│   │
│   ├─> Generate scene image using Gemini 2.5 Flash Image Preview
│   │   ├─ Prompt + all reference images
│   │   ├─ Aspect ratio: specified (16:9, 9:16, 1:1)
│   │   └─ Model composes scene with references
│   │
│   └─ Save: {project}_shot_{num}_scene.png
│
└─> Output:
    ├─ scene_images/{project}_shot_001_scene.png (for each shot)
    ├─ scene_images/{project}_shot_002_scene.png
    ├─ ...
    ├─ {project}_scene_generation_report.json
    └─ Report includes: generated_images{}, failed_generations[]

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 9: VIDEO DESCRIPTION GENERATION (Video Prompts for Veo)
═══════════════════════════════════════════════════════════════════════════════════

[VideoDescriptionGenerator]
│
├─> Input:
│   ├─ shots[] (with all shot details)
│   ├─ ad_title
│   └─ enable_animation_for_finale (bool)
│
├─> Process: For EACH shot
│   │
│   ├─ Analyze shot content:
│   │   ├─ Has dialogue? Has voice-over?
│   │   ├─ Action complexity
│   │   └─ Is final product showcase?
│   │
│   ├─ Determine video prompt type:
│   │   │
│   │   ├─ STANDARD PROMPT (most shots):
│   │   │   ├─ Camera Angle: detailed specs + lens
│   │   │   ├─ Scene Description: action & performance
│   │   │   ├─ Lighting: setup with color temp
│   │   │   ├─ Dialogue: exact words (or empty)
│   │   │   ├─ Voice Over: VO + voice type (or empty)
│   │   │   └─ Additional Notes: music, SFX, key focus
│   │   │
│   │   └─ ANIMATED SHOWCASE PROMPT (final shot only):
│   │       ├─ Camera Angle: dynamic movement path
│   │       ├─ Scene Description: complete transformation (first→last frame)
│   │       ├─ Lighting: dynamic evolution
│   │       ├─ Dialogue: (or empty)
│   │       ├─ Voice Over: VO + voice type
│   │       └─ Additional Notes:
│   │           ├─ Transition animation details (speed, easing)
│   │           ├─ Each text overlay animated individually:
│   │           │   ├─ Text content
│   │           │   ├─ Position, font, color, size
│   │           │   ├─ Animation type (slide, fade, etc.)
│   │           │   └─ Timing/delay
│   │           ├─ Visual effects (lens flares, glows)
│   │           └─ Product highlighting
│   │
│   └─> LLM generates detailed video prompt
│       └─ Stores in video_prompts[]
│
└─> Output:
    ├─ {project}_video_descriptions.json (all prompts)
    ├─ {project}_video_prompts.txt (readable)
    └─ Each prompt: 200-500 words, ready for Veo 3

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 10: VIDEO GENERATION (Image-to-Video with Veo 3)
═══════════════════════════════════════════════════════════════════════════════════

[VideoGenerator]
│
├─> Input:
│   ├─ shots[] (shot metadata)
│   ├─ video_prompts[] (from video description)
│   ├─ scene_images{} (generated keyframes)
│   └─ aspect_ratio (16:9)
│
├─> Process: For EACH shot
│   │
│   ├─ Determine video generation method:
│   │   │
│   │   ├─ STANDARD VIDEO (most shots):
│   │   │   │
│   │   │   ├─ Input: First frame image (scene image)
│   │   │   ├─ Prompt: Video prompt from video_descriptions
│   │   │   │
│   │   │   ├─ Determine duration intelligently:
│   │   │   │   ├─ Based on: dialogue, VO, action complexity
│   │   │   │   ├─ Available: 4s, 6s, or 8s
│   │   │   │   └─ Logic:
│   │   │   │       ├─ ≤3s shot → 4s video
│   │   │   │       ├─ 4-5s + dialogue/VO → 6s video
│   │   │   │       ├─ >5s + dialogue/VO/complex → 8s video
│   │   │   │       └─ Else → 6s video
│   │   │   │
│   │   │   ├─> Google Veo 3.1 Generate:
│   │   │   │   ├─ model: veo-3.1-generate-preview
│   │   │   │   ├─ prompt: full video prompt
│   │   │   │   ├─ image: first_frame (scene image)
│   │   │   │   ├─ config:
│   │   │   │   │   ├─ aspect_ratio: 16:9
│   │   │   │   │   └─ duration_seconds: [4/6/8]
│   │   │   │   └─ Poll until done (~30-60s)
│   │   │   │
│   │   │   └─ Save: {project}_shot_{num}_video.mp4
│   │   │
│   │   └─ ANIMATED SHOWCASE (final shot only):
│   │       │
│   │       ├─ Input: 
│   │       │   ├─ First frame: previous shot's scene image
│   │       │   └─ Last frame: current shot's scene image
│   │       ├─ Prompt: Animated showcase video prompt
│   │       │
│   │       ├─> Google Veo 3.1 Generate:
│   │       │   ├─ model: veo-3.1-generate-preview
│   │       │   ├─ prompt: animated prompt
│   │       │   ├─ image: first_frame
│   │       │   ├─ config:
│   │       │   │   ├─ aspect_ratio: 16:9
│   │       │   │   └─ last_frame: last_frame image
│   │       │   │       (duration fixed at 8s)
│   │       │   └─ Poll until done
│   │       │
│   │       └─ Save: {project}_shot_{num}_video_animated.mp4
│   │
│   └─ Delay between generations (avoid rate limit)
│
└─> Output:
    ├─ generated_videos/{project}_shot_001_video.mp4
    ├─ generated_videos/{project}_shot_002_video.mp4
    ├─ ...
    ├─ generated_videos/{project}_shot_00N_video_animated.mp4 (if final showcase)
    └─ {project}_video_generation_report.json
        ├─ generated_videos[] (shot_no, path, duration, status)
        └─ failed_generations[] (errors)

                                    ↓

═══════════════════════════════════════════════════════════════════════════════════
STAGE 11: VIDEO STITCHING & FINAL COMPOSITION
═══════════════════════════════════════════════════════════════════════════════════

[VideoStitcher]
│
├─> Input:
│   ├─ generated_videos[] (all shot videos)
│   ├─ shots[] (metadata)
│   ├─ music_theme (e.g., "sports_energetic") OR music_file_path
│   ├─ aspect_ratio
│   └─ stitching_config (resolution, fps, codec)
│
├─> Process:
│   │
│   ├─ Analyze video segments:
│   │   ├─ For each video: duration, has_dialogue, has_VO
│   │   ├─ Determine transition types:
│   │   │   ├─ First shot: fade in
│   │   │   ├─ Location change: dissolve
│   │   │   ├─ Product showcase: fade
│   │   │   └─ Default: cut
│   │   └─ Create VideoSegment objects
│   │
│   ├─ Load video clips (MoviePy):
│   │   ├─ VideoFileClip for each shot
│   │   ├─ Apply fade in (first clip)
│   │   ├─ Apply fade out (last clip)
│   │   └─ Apply transitions between clips
│   │
│   ├─ Concatenate video clips:
│   │   └─ concatenate_videoclips(method="compose")
│   │
│   ├─ Background music handling:
│   │   │
│   │   ├─ Select music:
│   │   │   ├─ From theme library (random/first)
│   │   │   │   └─ music_library/sports_energetic/track1.mp3
│   │   │   └─ OR direct file path
│   │   │
│   │   ├─ Adjust music to video:
│   │   │   ├─ Loop if too short
│   │   │   ├─ Trim to exact duration
│   │   │   └─ Apply fade in (1s) & fade out (2s)
│   │   │
│   │   ├─ Intelligent volume adjustment:
│   │   │   ├─ Base volume: 0.3 (30%)
│   │   │   ├─ During dialogue/VO: 0.15 (15%) - ducking
│   │   │   └─ Smooth transitions
│   │   │
│   │   └─ Mix audio tracks:
│   │       ├─ Video audio (dialogue, VO, SFX)
│   │       ├─ + Background music
│   │       └─ CompositeAudioClip
│   │
│   ├─ Set resolution:
│   │   └─ Resize to output_resolution (1920x1080)
│   │
│   └─> Export final video:
│       ├─ Codec: libx264
│       ├─ Audio codec: aac
│       ├─ Bitrate: 8000k
│       ├─ FPS: 30
│       ├─ Preset: medium
│       └─ Threads: 4
│
└─> Output:
    ├─ final_videos/{project}_final_ad.mp4
    ├─ {project}_stitching_report.json
    └─ Complete ad video with:
        ├─ All shots stitched with transitions
        ├─ Background music mixed with audio
        ├─ Professional quality output
        └─ Ready for distribution

═══════════════════════════════════════════════════════════════════════════════════
FINAL OUTPUT
═══════════════════════════════════════════════════════════════════════════════════

📦 Complete Project Structure:

projects_data/
└── {project_id}/
    ├── scripts/
    │   ├── {project}_shot_script.json ................... Stage 2
    │   ├── {project}_shot_script.csv .................... Stage 2
    │   ├── {project}_shot_script_complete.json .......... After Stages 3-6
    │   ├── {project}_characters.json .................... Stage 3
    │   ├── {project}_locations.json ..................... Stage 4
    │   ├── {project}_outfits.json ....................... Stage 5
    │   ├── {project}_character_outfits.json ............. Stage 6
    │   ├── {project}_scene_generation_report.json ....... Stage 8
    │   ├── {project}_video_generation_report.json ....... Stage 10
    │   └── {project}_stitching_report.json .............. Stage 11
    │
    ├── prompts/
    │   ├── {project}_scene_descriptions.json ............ Stage 7
    │   ├── {project}_image_prompts.txt .................. Stage 7
    │   ├── {project}_video_descriptions.json ............ Stage 9
    │   └── {project}_video_prompts.txt .................. Stage 9
    │
    ├── character_images/
    │   ├── {char1}_character.png ........................ Stage 3
    │   ├── {char2}_character.png
    │   └── ...
    │
    ├── location_images/
    │   ├── {loc1}_location.png .......................... Stage 4
    │   ├── {loc2}_location.png
    │   └── ...
    │
    ├── outfit_images/
    │   ├── {outfit1}_outfit.png ......................... Stage 5
    │   ├── {outfit2}_outfit.png
    │   └── ...
    │
    ├── character_outfit_images/
    │   ├── {char1}_{outfit1}.png ........................ Stage 6 ⭐
    │   ├── {char1}_{outfit2}.png
    │   ├── {char2}_{outfit1}.png
    │   └── ...
    │
    ├── scene_images/
    │   ├── {project}_shot_001_scene.png ................. Stage 8
    │   ├── {project}_shot_002_scene.png
    │   └── ...
    │
    ├── generated_videos/
    │   ├── {project}_shot_001_video.mp4 ................. Stage 10
    │   ├── {project}_shot_002_video.mp4
    │   └── ...
    │
    └── final_videos/
        └── {project}_final_ad.mp4 ....................... Stage 11 ✨

═══════════════════════════════════════════════════════════════════════════════════
``