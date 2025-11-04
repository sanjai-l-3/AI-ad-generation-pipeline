import os
import json
from typing import Dict, Any, Optional, List
from services.script_generation.script_generator import *
from services.character_generation.character_generator import *
from services.location_generation.location_generator import *
from services.outfit_generation.outfit_generator import *
from services.character_outfit_generation.character_outfit_generator import *
from services.scene_description_generation.scene_description_generator import *
from services.scene_generation.scene_image_generator import *
from services.video_description_generation.video_description_generator import *
from services.video_generation.video_generator import *
import time


class CompleteAdProductionPipeline:
    """Complete end-to-end pipeline with outfit generation"""
    
    def __init__(self, project_id: str, base_output_dir: str = "projects_data"):
        self.project_id = project_id
        self.base_output_dir = base_output_dir
        
        # Create directory structure
        self.dirs = {
            "base": base_output_dir,
            "project": os.path.join(base_output_dir, project_id),
            "characters": os.path.join(base_output_dir, project_id, "character_images"),
            "locations": os.path.join(base_output_dir, project_id, "location_images"),
            "outfits": os.path.join(base_output_dir, project_id, "outfit_images"),  # NEW
            "products": os.path.join(base_output_dir, project_id, "product_images"),
            "character_outfits": os.path.join(base_output_dir, project_id, "character_outfit_images"),
            "scenes": os.path.join(base_output_dir, project_id, "scene_images"),
            "scripts": os.path.join(base_output_dir, project_id, "scripts"),
            "prompts": os.path.join(base_output_dir, project_id, "prompts"),
            "videos": os.path.join(base_output_dir, project_id, "generated_videos")
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Define expected file paths for each stage
        self.stage_files = {
            "shot_script": os.path.join(self.dirs["scripts"], f"{project_id}_shot_script.json"),
            "shot_script_complete": os.path.join(self.dirs["scripts"], f"{project_id}_shot_script_complete.json"),
            "characters": os.path.join(self.dirs["scripts"], f"{project_id}_characters.json"),
            "locations": os.path.join(self.dirs["scripts"], f"{project_id}_locations.json"),
            "outfits": os.path.join(self.dirs["scripts"], f"{project_id}_outfits.json"),  # NEW
            "character_outfits": os.path.join(self.dirs["scripts"], f"{project_id}_character_outfits.json"), 
            "scene_descriptions": os.path.join(self.dirs["prompts"], f"{project_id}_scene_descriptions.json"),
            "generation_report": os.path.join(self.dirs["scripts"], f"{project_id}_scene_generation_report.json"),
            "video_descriptions": os.path.join(self.dirs["prompts"], f"{project_id}_video_descriptions.json"),  # NEW
            "video_generation_report": os.path.join(self.dirs["scripts"], f"{project_id}_video_generation_report.json"),
        }
        
        print(f"✅ Initialized project: {project_id}")
        self._check_existing_stages()
        
    def _check_existing_stages(self):
        """Check which stages have already been completed"""
        print("\n📋 Checking existing stages...")
        self.completed_stages = {}
        
        for stage, filepath in self.stage_files.items():
            exists = os.path.exists(filepath)
            self.completed_stages[stage] = exists
            status = "✅ COMPLETED" if exists else "❌ PENDING"
            print(f"  {stage}: {status}")
    def _stage_completed(self, stage: str) -> bool:
        """Check if a stage is completed"""
        return self.completed_stages.get(stage, False)
    
    def _mark_stage_completed(self, stage: str):
        """Mark a stage as completed"""
        self.completed_stages[stage] = True
    
    def _load_json(self, filepath: str) -> Optional[Dict]:
        """Load JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Error loading {filepath}: {e}")
            return None
    
    def load_existing_data(self) -> Dict[str, Any]:
        """Load all existing data from previous stages"""
        print("\n" + "="*100)
        print("📂 LOADING EXISTING DATA")
        print("="*100 + "\n")
        
        loaded_data = {
            "shot_script": None,
            "characters": None,
            "locations": None,
            "outfits": None,  # NEW
            "scene_descriptions": None
        }
        
        # Load shot script
        shot_script_path = self.stage_files.get("shot_script_complete") or self.stage_files.get("shot_script")
        if os.path.exists(shot_script_path):
            print(f"📄 Loading shot script from: {shot_script_path}")
            shot_script_data = self._load_json(shot_script_path)
            if shot_script_data:
            
                loaded_data["shot_script"] = ShotScript(**shot_script_data)
                print(f"  ✅ Loaded {len(loaded_data['shot_script'].shots)} shots")
        
        # Load characters
        if os.path.exists(self.stage_files["characters"]):
            print(f"📄 Loading characters from: {self.stage_files['characters']}")
            char_data = self._load_json(self.stage_files["characters"])
            if char_data:
                loaded_data["characters"] = char_data.get("characters", [])
                print(f"  ✅ Loaded {len(loaded_data['characters'])} characters")
        
        # Load locations
        if os.path.exists(self.stage_files["locations"]):
            print(f"📄 Loading locations from: {self.stage_files['locations']}")
            loc_data = self._load_json(self.stage_files["locations"])
            if loc_data:
                loaded_data["locations"] = loc_data.get("locations", [])
                print(f"  ✅ Loaded {len(loaded_data['locations'])} locations")
        
        # NEW: Load outfits
        if os.path.exists(self.stage_files["outfits"]):
            print(f"📄 Loading outfits from: {self.stage_files['outfits']}")
            outfit_data = self._load_json(self.stage_files["outfits"])
            if outfit_data:
                loaded_data["outfits"] = outfit_data.get("outfits", [])
                print(f"  ✅ Loaded {len(loaded_data['outfits'])} outfits")
        
        # Load scene descriptions
        if os.path.exists(self.stage_files["scene_descriptions"]):
            print(f"📄 Loading scene descriptions from: {self.stage_files['scene_descriptions']}")
            scene_data = self._load_json(self.stage_files["scene_descriptions"])
            if scene_data:
               
                loaded_data["scene_descriptions"] = SceneDescription(**scene_data)
                print(f"  ✅ Loaded {len(loaded_data['scene_descriptions'].shots)} scene descriptions")
        
        print("\n" + "="*100)
        print("📂 DATA LOADING COMPLETE")
        print("="*100 + "\n")
        
        return loaded_data
    
    def run_complete_pipeline(
        self,
        ad_concept: Dict[str, Any],
        brand_info: Dict[str, Any],
        product_image_path: Optional[str] = None,
        target_duration: str = "30 seconds",
        aspect_ratio: str = "16:9",
        generate_character_images: bool = True,
        generate_location_images: bool = True,
        generate_outfit_images: bool = True, 
        character_outfit_images:bool=True, # NEW
        generate_scene_images: bool = True,
        generate_videos:bool=True,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Run complete pipeline including outfit generation"""
        
        results = {
            "project_id": self.project_id,
            "directories": self.dirs,
            "files": {},
            "assets": {},
            "stages_executed": [],
            "stages_skipped": []
        }
        
        print("\n" + "="*100)
        print(f"🎬 STARTING COMPLETE AD PRODUCTION PIPELINE")
        print(f"Project: {self.project_id}")
        print(f"Force Regenerate: {force_regenerate}")
        print("="*100 + "\n")
        
        
        # ====================================================================
        # STEP 1: Generate Shot Script
        # ====================================================================
        print("\n" + "─"*100)
        print("STEP 1: SHOT SCRIPT GENERATION")
        print("─"*100)
        
        shot_script = None
        
        if force_regenerate or not self._stage_completed("shot_script"):
            print("🔄 Generating shot script...")
            
            
            
            shot_generator = ShotScriptGenerator()
            shot_script = shot_generator.generate_shot_script(
                ad_concept=ad_concept,
                brand_info=brand_info
            )
            
            # Save shot script
            shot_script_json = shot_generator.save_shot_script_json(
                shot_script,
                f"{self.project_id}_shot_script.json",
                self.dirs["scripts"]
            )
            
            
            results["files"]["shot_script_json"] = shot_script_json
          
            
            self._mark_stage_completed("shot_script")
            results["stages_executed"].append("shot_script_generation")
        else:
            print("✅ Shot script already exists, loading from file...")
            shot_script_data = self._load_json(self.stage_files["shot_script"])
            
            if shot_script_data:
            
                shot_script = ShotScript(**shot_script_data)
                results["files"]["shot_script_json"] = self.stage_files["shot_script"]
                results["stages_skipped"].append("shot_script_generation")
            else:
                print("⚠ Failed to load existing shot script, regenerating...")
                force_regenerate = True  # Force regeneration of subsequent stages
                return self.run_complete_pipeline(
                    ad_concept, brand_info, product_image_path, target_duration,
                    aspect_ratio, generate_character_images, generate_location_images,
                    generate_scene_images, force_regenerate=True
                )
        
        results["assets"]["shot_script"] = shot_script
        
        # ====================================================================
        # STEP 2: Generate Character Images
        # ====================================================================
        characters_with_images = None
        
        if generate_character_images and shot_script.characters_info:
            print("\n" + "─"*100)
            print("STEP 2: CHARACTER IMAGE GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("characters"):
                print(f"🔄 Generating images for {len(shot_script.characters_info)} characters...")
                
                
                
                # Convert to FullCharacter format
                full_characters = []
                for idx, char in enumerate(shot_script.characters_info, 1):
                    full_char = FullCharacter(
                        name=char.name,
                        age=char.age,
                        role=char.role,
                        gender=char.gender,
                        overall_description=char.overall_description
                    )
                    full_characters.append(full_char)
                
                # Generate images
                char_generator = CharacterGenerator(output_dir=self.dirs["characters"])
                characters_with_images = char_generator.generate_images_for_all_characters(full_characters)
                
                # Save character info
                char_json_path = os.path.join(self.dirs["scripts"], f"{self.project_id}_characters.json")
                char_generator.save_characters_with_images(characters_with_images, char_json_path)
                
                results["files"]["characters_json"] = char_json_path
                
                self._mark_stage_completed("characters")
                results["stages_executed"].append("character_image_generation")
            else:
                print("✅ Character images already exist, loading from file...")
                char_data = self._load_json(self.stage_files["characters"])
                
                if char_data:
                    
                    characters_with_images = [
                        FullCharacter(**char) for char in char_data.get("characters", [])
                    ]
                    results["files"]["characters_json"] = self.stage_files["characters"]
                    results["stages_skipped"].append("character_image_generation")
                else:
                    print("⚠ Failed to load existing character data")
            
            if characters_with_images:
                results["assets"]["characters"] = [char.model_dump() for char in characters_with_images]
                
                # Update shot script with image paths AND reference descriptions
                char_image_map = {char.name.lower(): char.image_path for char in characters_with_images}
                char_ref_desc_map = {char.name.lower(): char.reference_description for char in characters_with_images}  # NEW
                
                for char_info in shot_script.characters_info:
                    char_name_lower = char_info.name.lower()
                    if char_name_lower in char_image_map:
                        char_info.image_path = char_image_map[char_name_lower]
                    if char_name_lower in char_ref_desc_map:  # NEW
                        char_info.reference_description = char_ref_desc_map[char_name_lower]
        
        # ====================================================================
        # STEP 3: Generate Location Images
        # ====================================================================
        locations_with_images = None
        
        if generate_location_images and shot_script.location_info:
            print("\n" + "─"*100)
            print("STEP 3: LOCATION IMAGE GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("locations"):
                print(f"🔄 Generating images for {len(shot_script.location_info)} locations...")
                
              
                
                # Convert to FullLocation format
                full_locations = []
                for loc in shot_script.location_info:
                    full_loc = FullLocation(
                        name=loc.name,
                        overall_description=loc.overall_description
                    )
                    full_locations.append(full_loc)
                
                # Generate images
                loc_generator = LocationGenerator(output_dir=self.dirs["locations"])
                locations_with_images = loc_generator.generate_images_for_all_locations(full_locations)
                
                # Save location info
                loc_json_path = os.path.join(self.dirs["scripts"], f"{self.project_id}_locations.json")
                loc_generator.save_locations_with_images(locations_with_images, loc_json_path)
                
                results["files"]["locations_json"] = loc_json_path
                
                self._mark_stage_completed("locations")
                results["stages_executed"].append("location_image_generation")
            else:
                print("✅ Location images already exist, loading from file...")
                loc_data = self._load_json(self.stage_files["locations"])
                
                if loc_data:
               
                    locations_with_images = [
                        FullLocation(**loc) for loc in loc_data.get("locations", [])
                    ]
                    results["files"]["locations_json"] = self.stage_files["locations"]
                    results["stages_skipped"].append("location_image_generation")
                else:
                    print("⚠ Failed to load existing location data")
            
            if locations_with_images:
                results["assets"]["locations"] = [loc.model_dump() for loc in locations_with_images]
                
                # Update shot script with image paths
                loc_image_map = {loc.name.lower(): loc.image_path for loc in locations_with_images}
                for loc_info in shot_script.location_info:
                    if loc_info.name.lower() in loc_image_map:
                        loc_info.image_path = loc_image_map[loc_info.name.lower()]
        
        # Save updated shot script with all image paths
        if characters_with_images or locations_with_images:
       
            shot_generator = ShotScriptGenerator()
            shot_script_json = shot_generator.save_shot_script_json(
                shot_script,
                f"{self.project_id}_shot_script_complete.json",
                self.dirs["scripts"]
            )
            results["files"]["shot_script_complete"] = shot_script_json
            self._mark_stage_completed("shot_script_complete")

          # ====================================================================
        # STEP 4: Generate Outfit Images (NEW)
        # ====================================================================
        outfits_with_images = None
        
        if generate_outfit_images and shot_script.character_outfit_info:
            print("\n" + "─"*100)
            print("STEP 4: OUTFIT IMAGE GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("outfits"):
                print(f"🔄 Generating images for {len(shot_script.character_outfit_info)} outfits...")
                
                
                
                # Convert to FullOutfit format
                full_outfits = []
                for outfit_info in shot_script.character_outfit_info:
                    full_outfit = FullOutfit(
                        outfit=outfit_info.outfit,
                        outfit_description=outfit_info.outfit_description
                    )
                    full_outfits.append(full_outfit)
                
                # Generate images
                outfit_generator = OutfitGenerator(output_dir=self.dirs["outfits"])
                outfits_with_images = outfit_generator.generate_images_for_all_outfits(full_outfits)
                
                # Save outfit info
                outfit_json_path = os.path.join(self.dirs["scripts"], f"{self.project_id}_outfits.json")
                outfit_generator.save_outfits_with_images(outfits_with_images, outfit_json_path)
                
                results["files"]["outfits_json"] = outfit_json_path
                
                self._mark_stage_completed("outfits")
                results["stages_executed"].append("outfit_image_generation")
            else:
                print("✅ Outfit images already exist, loading from file...")
                outfit_data = self._load_json(self.stage_files["outfits"])
                
                if outfit_data:
                    
                    outfits_with_images = [
                        FullOutfit(**outfit) for outfit in outfit_data.get("outfits", [])
                    ]
                    results["files"]["outfits_json"] = self.stage_files["outfits"]
                    results["stages_skipped"].append("outfit_image_generation")
                else:
                    print("⚠ Failed to load existing outfit data")
            
            if outfits_with_images:
                results["assets"]["outfits"] = [outfit.model_dump() for outfit in outfits_with_images]
                
                # Update shot script with image paths
                outfit_image_map = {outfit.outfit.lower(): outfit.image_path for outfit in outfits_with_images}
                for outfit_info in shot_script.character_outfit_info:
                    if outfit_info.outfit.lower() in outfit_image_map:
                        outfit_info.image_path = outfit_image_map[outfit_info.outfit.lower()]
        
        # Save updated shot script
        if characters_with_images or locations_with_images or outfits_with_images:
            
            shot_generator = ShotScriptGenerator()
            shot_script_json = shot_generator.save_shot_script_json(
                shot_script,
                f"{self.project_id}_shot_script_complete.json",
                self.dirs["scripts"]
            )
            results["files"]["shot_script_complete"] = shot_script_json
            self._mark_stage_completed("shot_script_complete")

              # ====================================================================
    # STEP 4.5: Generate Character-Outfit Combinations (NEW)
    # ====================================================================
        character_outfit_images = None

        if generate_character_images and generate_outfit_images:
            print("\n" + "─"*100)
            print("STEP 4.5: CHARACTER-OUTFIT COMBINATION GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("character_outfits"):
                print(f"🔄 Generating character-outfit combinations...")
                
                
                
                char_outfit_gen = CharacterOutfitGenerator(output_dir=self.dirs["character_outfits"])
                
                character_outfit_images = char_outfit_gen.generate_all_character_outfits(
                    characters_info=results["assets"].get("characters", []),
                    outfits_info=results["assets"].get("outfits", []),
                    shots_info=[shot.model_dump() for shot in shot_script.shots]
                )
                
                # Save mapping
                char_outfit_json = char_outfit_gen.save_character_outfit_mapping(
                    character_outfit_images,
                    f"{self.project_id}_character_outfits.json",
                    self.dirs["scripts"]
                )
                
                results["files"]["character_outfits"] = char_outfit_json
                self._mark_stage_completed("character_outfits")
                results["stages_executed"].append("character_outfit_generation")
            else:
                print("✅ Character-outfit images already exist")
                # Load existing
                co_data = self._load_json(self.stage_files["character_outfits"])
                if co_data:
                    character_outfit_images = co_data.get("character_outfits", [])
                    results["stages_skipped"].append("character_outfit_generation")
            
            if character_outfit_images:
                results["assets"]["character_outfits"] = character_outfit_images
        
        # ====================================================================
        # STEP 5: Generate Scene Descriptions (Updated with outfits)
        # ====================================================================
        print("\n" + "─"*100)
        print("STEP 5: SCENE DESCRIPTION GENERATION")
        print("─"*100)
        
        scene_descriptions = None
        
        if force_regenerate or not self._stage_completed("scene_descriptions"):
            print("🔄 Generating scene descriptions and image prompts...")
            
           
            
            scene_desc_generator = SceneDescriptionGenerator()
            scene_descriptions = scene_desc_generator.generate_scene_descriptions(
                shots=shot_script.shots,
                brand_info=brand_info,
                ad_title=shot_script.ad_title,
                characters_info=[char.model_dump() for char in shot_script.characters_info],
                locations_info=[loc.model_dump() for loc in shot_script.location_info], # NEW: Pass outfits
                ad_concept=ad_concept
            )
            
            # Save scene descriptions
            scene_desc_json = scene_desc_generator.save_scene_descriptions(
                scene_descriptions,
                f"{self.project_id}_scene_descriptions.json",
                self.dirs["prompts"]
            )
            scene_prompts_txt = scene_desc_generator.export_prompts_only(
                scene_descriptions,
                f"{self.project_id}_image_prompts.txt",
                self.dirs["prompts"]
            )
            
            results["files"]["scene_descriptions"] = scene_desc_json
            results["files"]["image_prompts"] = scene_prompts_txt
            
            self._mark_stage_completed("scene_descriptions")
            results["stages_executed"].append("scene_description_generation")
        else:
            print("✅ Scene descriptions already exist, loading from file...")
            scene_desc_data = self._load_json(self.stage_files["scene_descriptions"])
            
            if scene_desc_data:
        
                scene_descriptions = SceneDescription(**scene_desc_data)
                results["files"]["scene_descriptions"] = self.stage_files["scene_descriptions"]
                results["stages_skipped"].append("scene_description_generation")
        
        results["assets"]["scene_descriptions"] = scene_descriptions


      

        
        # ====================================================================
        # STEP 5: Generate Scene Images
        # ====================================================================
        # In CompleteAdProductionPipeline.run_complete_pipeline()

# STEP 6: Generate Scene Images (Updated)
        if generate_scene_images and scene_descriptions:
            print("\n" + "─"*100)
            print("STEP 6: SCENE IMAGE GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("generation_report"):
                print("🔄 Generating scene images...")
                
               
                
                scene_image_generator = SceneImageGenerator(output_dir=self.dirs["scenes"])
                
                # Prepare product info
                product_info = None
                if product_image_path and os.path.exists(product_image_path):
                    product_info = {
                        "name": brand_info.get("product_name", "product"),
                        "image_path": product_image_path
                    }
                    print("Character_info")
                    print(results["assets"].get("characters", []))

                    print("Location Info")
                    print(results["assets"].get("locations", []))

                    print("Outfit Info")
                    print(results["assets"].get("outfits", []))
                
                # Generate all scene images with outfit references
                generation_results = scene_image_generator.generate_all_scene_images(
                    scene_description=scene_descriptions,
                    characters_info=results["assets"].get("characters", []),
                    locations_info=results["assets"].get("locations", []),
                    character_outfit_images=results["assets"].get("character_outfits", []),
                    product_info=product_info,
                    aspect_ratio=aspect_ratio,
                    project_id=self.project_id
                )
                
                # Save generation report
                report_path = scene_image_generator.save_generation_report(
                    f"{self.project_id}_scene_generation_report.json",
                    self.dirs["scripts"]
                )
                
                results["files"]["generation_report"] = report_path
                results["assets"]["scene_images"] = generation_results
                
                self._mark_stage_completed("generation_report")
                results["stages_executed"].append("scene_image_generation")
            else:
                print("✅ Scene images already generated, loading report...")
                report_data = self._load_json(self.stage_files["generation_report"])
                
                if report_data:
                    results["files"]["generation_report"] = self.stage_files["generation_report"]
                    results["assets"]["scene_images"] = report_data
                    results["stages_skipped"].append("scene_image_generation")
                else:
                    print("⚠ Failed to load existing generation report")

        # ====================================================================
        # STEP 7: Generate Video Descriptions (NEW)
        # ====================================================================
        print("\n" + "─"*100)
        print("STEP 7: VIDEO DESCRIPTION GENERATION")
        print("─"*100)

        video_descriptions = None

        if force_regenerate or not self._stage_completed("video_descriptions"):
            print("🔄 Generating video descriptions...")
            

            
            video_desc_generator = VideoDescriptionGenerator()
            video_descriptions = video_desc_generator.generate_video_descriptions(
                shots=[shot.model_dump() for shot in shot_script.shots],
                ad_title=shot_script.ad_title,
                enable_animation_for_finale=True  # Can be parameterized
            )
            
            # Save video descriptions
            video_desc_json = video_desc_generator.save_video_descriptions(
                video_descriptions,
                f"{self.project_id}_video_descriptions.json",
                self.dirs["prompts"]
            )
            video_desc_txt = video_desc_generator.export_video_prompts_readable(
                video_descriptions,
                f"{self.project_id}_video_prompts.txt",
                self.dirs["prompts"]
            )
            
            results["files"]["video_descriptions"] = video_desc_json
            results["files"]["video_prompts_txt"] = video_desc_txt
            
            self._mark_stage_completed("video_descriptions")
            results["stages_executed"].append("video_description_generation")
        else:
            print("✅ Video descriptions already exist, loading...")
            # Load existing video descriptions
            video_desc_data = self._load_json(self.stage_files["video_descriptions"])
            if video_desc_data:

                video_descriptions = VideoDescription(**video_desc_data)
                results["stages_skipped"].append("video_description_generation")

        results["assets"]["video_descriptions"] = video_descriptions


        # ====================================================================
        # STEP 8: Generate Videos (NEW)
        # ====================================================================
        if generate_videos and video_descriptions:  # Add generate_videos parameter
            print("\n" + "─"*100)
            print("STEP 8: VIDEO GENERATION")
            print("─"*100)
            
            if force_regenerate or not self._stage_completed("video_generation_report"):
                print("🔄 Generating videos...")
                
                
                
                video_generator = VideoGenerator(
                    output_dir=self.dirs["videos"],
                    aspect_ratio=aspect_ratio
                )
                
                # Build scene images mapping from generation report
                scene_images = {}
                if results["assets"].get("scene_images"):
                    for shot_id, img_data in results["assets"]["scene_images"]["generated_images"].items():
                        shot_no = img_data.get("shot_no")
                        filepath = img_data.get("filepath")
                        if shot_no and filepath:
                            scene_images[shot_no] = filepath
                
                # Generate all videos
                video_progress = video_generator.generate_all_videos(
                    shots=[shot.model_dump() for shot in shot_script.shots],
                    video_prompts=[vp.model_dump() for vp in video_descriptions.video_prompts],
                    scene_images=scene_images,
                    ad_title=shot_script.ad_title,
                    project_id=self.project_id,
                    delay_between_videos=5.0
                )
                
                # Save video generation report
                video_report_path = video_generator.save_generation_report(
                    f"{self.project_id}_video_generation_report.json",
                    self.dirs["scripts"]
                )
                
                results["files"]["video_generation_report"] = video_report_path
                results["assets"]["generated_videos"] = video_progress
                
                self._mark_stage_completed("video_generation_report")
                results["stages_executed"].append("video_generation")
            else:
                print("✅ Videos already generated")
                results["stages_skipped"].append("video_generation")
                
        # ====================================================================
        # Final Summary
        # ====================================================================
        print("\n" + "="*100)
        print("🎉 PIPELINE COMPLETE!")
        print("="*100)
        print(f"\n📁 Project Directory: {self.dirs['project']}")
        
        if results["stages_executed"]:
            print(f"\n✅ Stages Executed ({len(results['stages_executed'])}):")
            for stage in results["stages_executed"]:
                print(f"  - {stage}")
        
        if results["stages_skipped"]:
            print(f"\n⏭️  Stages Skipped ({len(results['stages_skipped'])}):")
            for stage in results["stages_skipped"]:
                print(f"  - {stage}")
        
        print(f"\n📄 Generated/Loaded Files:")
        for key, path in results["files"].items():
            print(f"  - {key}: {path}")
        
        return results
    
    def reset_stage(self, stage: str):
        """
        Reset a specific stage by deleting its output files
        
        Args:
            stage: Stage name (shot_script, characters, locations, scene_descriptions, generation_report)
        """
        if stage not in self.stage_files:
            print(f"⚠ Unknown stage: {stage}")
            return
        
        filepath = self.stage_files[stage]
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Deleted: {filepath}")
            self.completed_stages[stage] = False
        else:
            print(f"⚠ File not found: {filepath}")
    
    def reset_all_stages(self):
        """Reset all stages"""
        print("🗑️  Resetting all stages...")
        for stage in self.stage_files.keys():
            self.reset_stage(stage)
        print("✅ All stages reset")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of all pipeline stages"""
        self._check_existing_stages()
        
        status = {
            "project_id": self.project_id,
            "completed_stages": [],
            "pending_stages": [],
            "stage_details": {}
        }
        
        for stage, completed in self.completed_stages.items():
            if completed:
                status["completed_stages"].append(stage)
                status["stage_details"][stage] = {
                    "status": "completed",
                    "file": self.stage_files[stage]
                }
            else:
                status["pending_stages"].append(stage)
                status["stage_details"][stage] = {
                    "status": "pending",
                    "file": self.stage_files[stage]
                }
        
        return status


# Example usage
if __name__ == "__main__":
    # Example ad concept
    ad_concept = {
    "title": "Did I Apply Sunscreen?",
    "one_line_summary": "Two Friends Girl and Boy Protogonist and her friend Boy ,A playful, memorable routine where our protagonist keeps forgetting she already applied the gel sunscreen because it's so light.",
    "story": "A young woman goes through her day under strong sun. The sunscreen is so weightless that she keeps forgetting she applied it, leading to a repeated humorous exchange.",
    "visual_flow": {
        "Opening": "Morning street scene - soft natural light. She touches her face: 'Did I apply sunscreen?' Companion replies calmly, 'Yes, you did.'",
        "Sequence": "Afternoon at the beach - strong sun. She pauses mid-conversation, touches her face again, 'Did I apply sunscreen?' Same calm reply: 'Yes, you did.'",
        "Evening": "Outdoor café sunset - warm tones. Once again, she checks: 'Did I apply sunscreen?' Companion: 'Yes, you did.' Both laugh.",
    },
    "voice_over": "So light, you might forget you applied it.",
    "tagline": "So light, you’ll forget.",
    "key_message": "Invisible comfort; protection without the heaviness.",
    "key_features": ["SPF 55+", "PA+++", "Weightless gel texture", "No white cast", "Sweat-resistant"]
}

    
    # Example brand info
    brand_info = {
        "brand_name": "Deconstruct",
        "product_name": "Gel Sunscreen SPF 55",
        "product_description": "Lightweight, matte finish sunscreen",
        "key_features": ["SPF 55+", "PA+++", "Matte finish", "Sweat-resistant"]
    }
    
    # Initialize pipeline
    pipeline = CompleteAdProductionPipeline(project_id="deconstruct_light_weight_multiple_character_004")
    
    # Check current status
    status = pipeline.get_pipeline_status()
    print("\n📊 Current Pipeline Status:")
    print(f"Completed: {status['completed_stages']}")
    print(f"Pending: {status['pending_stages']}")
    
    # Run pipeline (will skip completed stages automatically)
    results = pipeline.run_complete_pipeline(
        ad_concept=ad_concept,
        brand_info=brand_info,
        product_image_path="/Users/sanjail/Akaike/Internal_project/ads_poc/product_image.png",
        target_duration="45 seconds",
        aspect_ratio="16:9",
        generate_character_images=True,
        generate_location_images=True,
        generate_outfit_images=True,
        generate_scene_images=True,
        generate_videos=True,
        force_regenerate=False  # Set to True to regenerate everything
    )
    
    print("\n✅ Pipeline execution complete!")
    
    # Example: Reset a specific stage if you want to regenerate it
    # pipeline.reset_stage("scene_descriptions")
    
    # Example: Reset all stages
    # pipeline.reset_all_stages()