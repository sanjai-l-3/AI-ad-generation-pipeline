import time
import os
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json
from dotenv import load_dotenv


load_dotenv()


class VideoGenerationResult(BaseModel):
    """Result of video generation for a single shot"""
    shot_no: int
    video_path: str
    prompt_type: str  # "standard" or "animated_showcase"
    duration_seconds: int
    status: str  # "success" or "failed"
    error_message: Optional[str] = None


class VideoGenerationProgress(BaseModel):
    """Progress tracking for video generation"""
    ad_title: str
    total_shots: int
    generated_videos: List[VideoGenerationResult] = Field(default_factory=list)
    failed_generations: List[Dict[str, Any]] = Field(default_factory=list)
    current_shot: Optional[int] = None


class VideoGenerator:
    """Generate videos using Google Veo 3.1 from scene images and video prompts"""
    
    def __init__(self, output_dir: str = "generated_videos", aspect_ratio: str = "16:9"):
        """
        Initialize Video Generator
        
        Args:
            output_dir: Directory to store generated videos
            aspect_ratio: Video aspect ratio (default: "16:9")
        """
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.output_dir = output_dir
        self.aspect_ratio = aspect_ratio
        os.makedirs(output_dir, exist_ok=True)
        
        self.progress = VideoGenerationProgress(
            ad_title="",
            total_shots=0,
            generated_videos=[],
            failed_generations=[]
        )
    
    def determine_video_duration(
        self,
        shot: Dict[str, Any],
        video_prompt: Dict[str, Any]
    ) -> int:
        """
        Determine optimal video duration based on shot content
        Available durations: 4, 6, 8 seconds
        
        Args:
            shot: Shot information dictionary
            video_prompt: Video prompt information
            
        Returns:
            Duration in seconds (4, 6, or 8)
        """
        # Get shot duration from shot info
        shot_duration_str = shot.get('duration', '4 seconds')
        
        # Parse duration
        try:
            shot_duration = int(shot_duration_str.split()[0])
        except:
            shot_duration = 4
        
        # Check for dialogue
        has_dialogue = shot.get('dialogue') and shot.get('dialogue') != "None"
        
        # Check for voice over
        has_voice_over = shot.get('voice_over') and shot.get('voice_over') != "None"
        
        # Check for complex action
        action_text = shot.get('action', '')
        is_complex_action = len(action_text) > 100  # Long action description
        
        # Determine duration
        if shot_duration <= 3:
            duration = 4
        elif shot_duration <= 5:
            if has_dialogue or has_voice_over:
                duration = 6
            else:
                duration = 4
        else:  # shot_duration > 5
            if has_dialogue or has_voice_over or is_complex_action:
                duration = 8
            else:
                duration = 6
        
        print(f"  📏 Determined duration: {duration}s (shot duration: {shot_duration_str}, dialogue: {has_dialogue}, VO: {has_voice_over})")
        
        return duration
    
    def generate_standard_video(
        self,
        shot_no: int,
        first_frame_path: str,
        video_prompt: str,
        duration_seconds: int,
        project_id: str = "project"
    ) -> Optional[str]:
        """
        Generate video from first frame image (standard shot)
        
        Args:
            shot_no: Shot number
            first_frame_path: Path to the first frame image (scene image)
            video_prompt: Detailed video generation prompt
            duration_seconds: Duration in seconds (4, 6, or 8)
            project_id: Project identifier
            
        Returns:
            Path to generated video or None if failed
        """
        print(f"\n{'─'*80}")
        print(f"🎬 Generating STANDARD video for Shot {shot_no}")
        print(f"{'─'*80}")
        print(f"  📸 First frame: {first_frame_path}")
        print(f"  ⏱️  Duration: {duration_seconds}s")
        print(f"  📝 Prompt: {video_prompt[:100]}...")
        
        try:
            # Load first frame image
            if not os.path.exists(first_frame_path):
                print(f"  ❌ First frame image not found: {first_frame_path}")
                return None
            
            first_image = types.Image.from_file(location=first_frame_path)
            print(f"  ✅ Loaded first frame image")
            
            # Generate video
            print(f"  🎬 Starting video generation...")
            operation = self.client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=video_prompt,
                image=first_image,
                config=types.GenerateVideosConfig(
                    aspect_ratio=self.aspect_ratio,
                    duration_seconds=duration_seconds
                )
            )
            
            # Poll operation status
            print(f"  ⏳ Polling for completion...")
            poll_count = 0
            while not operation.done:
                poll_count += 1
                print(f"     Polling attempt {poll_count}... (waiting 10s)")
                time.sleep(10)
                operation = self.client.operations.get(operation)
                print(operation)
            
            print(f"  ✅ Video generation complete after {poll_count} polls")
            
            
            

             # Save video for api
            generated_video = operation.response.generated_videos[0]
            filename = f"{project_id}_shot_{shot_no:03d}_video.mp4"
            video_path = os.path.join(self.output_dir, filename)
            
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(video_path)

            #use this when running with vertex AI client
            # if operation.response.generated_videos:
    
    
            #     for idx, gen_video in enumerate(operation.response.generated_videos, start=1):
            #         filename = f"{project_id}_shot_{shot_no:03d}_video.mp4"
            #         video_path = os.path.join(self.output_dir, filename)
                    
            #         gen_video.video.save(video_path)
            #         print(f"Video saved as {video_path}")

            
            
           
            
            print(f"  💾 Video saved: {video_path}")
            
            return video_path
            
        except Exception as e:
            print(f"  ❌ Error generating standard video for shot {shot_no}: {e}")
            return None
    
    def generate_animated_showcase_video(
        self,
        shot_no: int,
        first_frame_path: str,
        last_frame_path: str,
        video_prompt: str,
        project_id: str = "project"
    ) -> Optional[str]:
        """
        Generate animated video from first and last frame images (product showcase)
        Duration is fixed at 8 seconds for animated showcase
        
        Args:
            shot_no: Shot number
            first_frame_path: Path to the first frame image
            last_frame_path: Path to the last frame image
            video_prompt: Detailed video generation prompt
            project_id: Project identifier
            
        Returns:
            Path to generated video or None if failed
        """
        print(f"\n{'─'*80}")
        print(f"🎬 Generating ANIMATED SHOWCASE video for Shot {shot_no}")
        print(f"{'─'*80}")
        print(f"  📸 First frame: {first_frame_path}")
        print(f"  📸 Last frame: {last_frame_path}")
        print(f"  ⏱️  Duration: 8s (fixed for animated showcase)")
        print(f"  📝 Prompt: {video_prompt[:100]}...")
        
        try:
            # Load images
            if not os.path.exists(first_frame_path):
                print(f"  ❌ First frame image not found: {first_frame_path}")
                return None
            
            if not os.path.exists(last_frame_path):
                print(f"  ❌ Last frame image not found: {last_frame_path}")
                return None
            
            first_image = types.Image.from_file(location=first_frame_path)
            last_image = types.Image.from_file(location=last_frame_path)
            print(f"  ✅ Loaded both frame images")
            
            # Generate video with first and last frame
            print(f"  🎬 Starting animated video generation...")
            operation = self.client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=video_prompt,
                image=first_image,
                config=types.GenerateVideosConfig(
                    aspect_ratio=self.aspect_ratio,
                    last_frame=last_image
                )
            )
            
            # Poll operation status
            print(f"  ⏳ Polling for completion...")
            poll_count = 0
            while not operation.done:
                poll_count += 1
                print(f"     Polling attempt {poll_count}... (waiting 10s)")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            print(f"  ✅ Video generation complete after {poll_count} polls")
            
             # Save video from api key client
            generated_video = operation.response.generated_videos[0]
            filename = f"{project_id}_shot_{shot_no:03d}_video_animated.mp4"
            video_path = os.path.join(self.output_dir, filename)
            
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(video_path)


            #use this when running with vertex AI client
            # if operation.response.generated_videos:
    
    
            #     for idx, gen_video in enumerate(operation.response.generated_videos, start=1):
            #         filename = f"{project_id}_shot_{shot_no:03d}_video.mp4"
            #         video_path = os.path.join(self.output_dir, filename)
                    
            #         gen_video.video.save(video_path)
            #         print(f"Video saved as {video_path}")

            
            print(f"  💾 Video saved: {video_path}")
            
            return video_path
            
        except Exception as e:
            print(f"  ❌ Error generating animated showcase video for shot {shot_no}: {e}")
            return None
    
    def generate_all_videos(
        self,
        shots: List[Dict[str, Any]],
        video_prompts: List[Dict[str, Any]],
        scene_images: Dict[int, str],  # Maps shot_no to scene image path
        ad_title: str,
        project_id: str = "project",
        delay_between_videos: float = 5.0
    ) -> VideoGenerationProgress:
        """
        Generate videos for all shots
        
        Args:
            shots: List of shot dictionaries
            video_prompts: List of video prompt dictionaries
            scene_images: Dictionary mapping shot_no to scene image path
            ad_title: Ad title
            project_id: Project identifier
            delay_between_videos: Delay between video generations (seconds)
            
        Returns:
            VideoGenerationProgress with results
        """
        print("\n" + "="*100)
        print(f"🎬 GENERATING VIDEOS - {ad_title}")
        print(f"Aspect Ratio: {self.aspect_ratio}")
        print("="*100 + "\n")
        
        self.progress.ad_title = ad_title
        self.progress.total_shots = len(shots)
        
        # Create shot_no to video_prompt mapping
        prompt_map = {vp['shot_no']: vp for vp in video_prompts}
        
        for idx, shot in enumerate(shots, 1):
            shot_no = shot.get('shot_no', idx)
            self.progress.current_shot = shot_no
            
            print(f"\n{'='*100}")
            print(f"[{idx}/{len(shots)}] Processing Shot {shot_no}")
            print(f"{'='*100}")
            
            # Get scene image
            scene_image_path = scene_images.get(shot_no)
            if not scene_image_path:
                print(f"  ❌ No scene image found for shot {shot_no}")
                self.progress.failed_generations.append({
                    "shot_no": shot_no,
                    "error": "Scene image not found"
                })
                continue
            
            # Get video prompt
            video_prompt_data = prompt_map.get(shot_no)
            if not video_prompt_data:
                print(f"  ❌ No video prompt found for shot {shot_no}")
                self.progress.failed_generations.append({
                    "shot_no": shot_no,
                    "error": "Video prompt not found"
                })
                continue
            
            prompt_type = video_prompt_data.get('prompt_type', 'standard')
            
            video_path = None
            duration = 0
            
            if prompt_type == "standard":
                # Standard video generation
                standard_prompt_data = video_prompt_data.get('standard_prompt')
                if not standard_prompt_data:
                    print(f"  ❌ No standard prompt data for shot {shot_no}")
                    continue
                
                # Build full prompt
                full_prompt = self._build_full_prompt(standard_prompt_data)
                
                # Determine duration
                duration = self.determine_video_duration(shot, video_prompt_data)
                
                # Generate video
                video_path = self.generate_standard_video(
                    shot_no=shot_no,
                    first_frame_path=scene_image_path,
                    video_prompt=full_prompt,
                    duration_seconds=8,
                    project_id=project_id
                )
                
            elif prompt_type == "animated_showcase":
                # Animated showcase video generation
                animated_prompt_data = video_prompt_data.get('animated_prompt')
                if not animated_prompt_data:
                    print(f"  ❌ No animated prompt data for shot {shot_no}")
                    continue
                
                # Build full prompt
                full_prompt = self._build_full_prompt(animated_prompt_data)
                
                # Get last frame (use previous shot's scene image or same image)
                if idx > 1:
                    previous_shot_no = shots[idx-2].get('shot_no', idx-1)
                    last_frame_path = scene_images.get(previous_shot_no, scene_image_path)
                else:
                    last_frame_path = scene_image_path
                
                duration = 8  # Fixed for animated showcase
                
                # Generate video
                video_path = self.generate_animated_showcase_video(
                    shot_no=shot_no,
                    first_frame_path=last_frame_path,
                    last_frame_path=scene_image_path,
                    video_prompt=full_prompt,
                    project_id=project_id
                )
            
            # Record result
            if video_path:
                result = VideoGenerationResult(
                    shot_no=shot_no,
                    video_path=video_path,
                    prompt_type=prompt_type,
                    duration_seconds=8,
                    status="success"
                )
                self.progress.generated_videos.append(result)
                print(f"  ✅ Successfully generated video for shot {shot_no}")
            else:
                self.progress.failed_generations.append({
                    "shot_no": shot_no,
                    "error": "Video generation failed"
                })
                print(f"  ❌ Failed to generate video for shot {shot_no}")
            
            # Delay before next video
            if idx < len(shots):
                print(f"\n  ⏳ Waiting {delay_between_videos}s before next video generation...")
                time.sleep(delay_between_videos)
        
        # Print summary
        print("\n" + "="*100)
        print("VIDEO GENERATION COMPLETE")
        print("="*100)
        print(f"✅ Successfully generated: {len(self.progress.generated_videos)}/{self.progress.total_shots}")
        print(f"❌ Failed: {len(self.progress.failed_generations)}")
        
        if self.progress.failed_generations:
            print("\nFailed videos:")
            for failed in self.progress.failed_generations:
                print(f"  - Shot {failed['shot_no']}: {failed['error']}")
        
        return self.progress
    
    def _build_full_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """Build full video prompt from prompt data"""
        parts = []
        
        if prompt_data.get('camera_angle'):
            parts.append(f"Camera Angle: {prompt_data['camera_angle']}")
        
        if prompt_data.get('scene_description'):
            parts.append(f"Scene Description: {prompt_data['scene_description']}")
        
        if prompt_data.get('lighting'):
            parts.append(f"Lighting: {prompt_data['lighting']}")
        
        if prompt_data.get('dialogue'):
            parts.append(f"Dialogue: \"{prompt_data['dialogue']}\"")
        
        if prompt_data.get('voice_over'):
            parts.append(f"Voice Over: {prompt_data['voice_over']}")
        
        if prompt_data.get('additional_notes'):
            parts.append(f"Additional Notes: {prompt_data['additional_notes']}")
        
        return "\n".join(parts)
    
    def generate_single_video_with_prompt(
        self,
        shot_no: int,
        shot: Dict[str, Any],
        video_prompt: str,
        scene_image_path: str,
        project_id: str = "project",
        prompt_type: str = "standard"
    ) -> Optional[str]:
        """
        Generate a single video with custom prompt
        
        Args:
            shot_no: Shot number
            shot: Shot information dictionary
            video_prompt: Custom video generation prompt
            scene_image_path: Path to the scene image
            project_id: Project identifier
            prompt_type: Type of video ("standard" or "animated_showcase")
            
        Returns:
            Path to generated video or None if failed
        """
        print(f"\n{'─'*80}")
        print(f"🎬 Generating SINGLE video for Shot {shot_no} with custom prompt")
        print(f"{'─'*80}")
        print(f"  📸 Scene image: {scene_image_path}")
        print(f"  📝 Custom prompt: {video_prompt[:100]}...")
        print(f"  🎭 Prompt type: {prompt_type}")
        
        try:
            if prompt_type == "standard":
                # Determine duration
                duration = self.determine_video_duration(shot, {"duration": shot.get('duration', '4 seconds')})
                
                # Generate standard video
                video_path = self.generate_standard_video(
                    shot_no=shot_no,
                    first_frame_path=scene_image_path,
                    video_prompt=video_prompt,
                    duration_seconds=duration,
                    project_id=project_id
                )
                
            elif prompt_type == "animated_showcase":
                # For animated showcase, we need a last frame
                # Use the same image as last frame for single generation
                video_path = self.generate_animated_showcase_video(
                    shot_no=shot_no,
                    first_frame_path=scene_image_path,
                    last_frame_path=scene_image_path,
                    video_prompt=video_prompt,
                    project_id=project_id
                )
            else:
                print(f"  ❌ Unknown prompt type: {prompt_type}")
                return None
            
            if video_path:
                print(f"  ✅ Successfully generated video: {video_path}")
                return video_path
            else:
                print(f"  ❌ Failed to generate video for shot {shot_no}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error generating single video for shot {shot_no}: {e}")
            return None

    def save_generation_report(
        self,
        output_file: str,
        output_dir: str = "projects_data"
    ) -> str:
        """Save video generation report to JSON"""
        file_path = os.path.join(output_dir, output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        report_dict = self.progress.model_dump()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Video generation report saved to {file_path}")
        return file_path


# ============================================================================
# STANDALONE TESTING
# ============================================================================

# if __name__ == "__main__":
#     print("\n" + "="*100)
#     print("VIDEO GENERATOR - STANDALONE TEST")
#     print("="*100)
    
#     # Example: Test with mock data
#     example_shots = [
#         {
#             "shot_no": 1,
#             "duration": "3 seconds",
#             "dialogue": "None",
#             "voice_over": "Champions prepare for everything.",
#             "action": "the man checks his bat carefully"
#         },
#         {
#             "shot_no": 2,
#             "duration": "5 seconds",
#             "dialogue": "I am protected.",
#             "voice_over": "None",
#             "action": "the man walks confidently towards the pitch"
#         }
#     ]
    
#     example_video_prompts = [
#         {
#             "shot_no": 1,
#             "prompt_type": "standard",
#             "standard_prompt": {
#                 "camera_angle": "Medium shot, 50mm lens",
#                 "scene_description": "the man examines his cricket bat carefully",
#                 "lighting": "Soft morning light, 5600K",
#                 "dialogue": "",
#                 "voice_over": "Champions prepare for everything. (in Indian female voice)",
#                 "additional_notes": "Morning ambience, subtle sounds"
#             }
#         },
#         {
#             "shot_no": 2,
#             "prompt_type": "standard",
#             "standard_prompt": {
#                 "camera_angle": "Wide to medium close-up, 50mm lens",
#                 "scene_description": "the man walks confidently towards pitch",
#                 "lighting": "Bright sunlight, 5600K",
#                 "dialogue": "I am protected.",
#                 "voice_over": "",
#                 "additional_notes": "Stadium crowd ambience"
#             }
#         }
#     ]
    
#     # Mock scene images (replace with actual paths)
#     scene_images = {
#         1: "/Users/sanjail/Akaike/Internal_project/ads_poc/projects_data/deconstruct_dhoni_004/scene_images/deconstruct_dhoni_004_shot_002_scene.png",
#         2: "/Users/sanjail/Akaike/Internal_project/ads_poc/projects_data/deconstruct_dhoni_004/scene_images/deconstruct_dhoni_004_shot_007_scene.png"
#     }
    
#     # Initialize generator
#     generator = VideoGenerator(
#         output_dir="test_videos",
#         aspect_ratio="16:9"
#     )
    
#     # Generate videos
#     progress = generator.generate_all_videos(
#         shots=example_shots,
#         video_prompts=example_video_prompts,
#         scene_images=scene_images,
#         ad_title="Test Ad",
#         project_id="test_project",
#         delay_between_videos=5.0
#     )
    
#     # Save report
#     generator.save_generation_report(
#         "video_generation_report_test.json",
#         "test_output"
#     )
    
#     print("\n✅ Video generation test complete!")