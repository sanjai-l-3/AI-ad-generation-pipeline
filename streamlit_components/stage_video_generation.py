"""
Stage 5: Video Description and Video Generation Component
Modern UI with video generation capabilities
"""

import streamlit as st
import os
import json
from services.video_description_generation.video_description_generator import VideoDescriptionGenerator, VideoDescription
from services.video_generation.video_generator import VideoGenerator


def display_video_generation_ui(project_id, project_path):
    """Display video description and generation stage"""
    
    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">🎥 Video Description & Generation</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Generate video descriptions and create video clips</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 Video Descriptions", "🎬 Video Generation"])
    
    with tab1:
        display_video_descriptions_tab(project_id, project_path)
    
    with tab2:
        display_video_generation_tab(project_id, project_path)


def display_video_descriptions_tab(project_id, project_path):
    """Display video descriptions generation tab"""
    
    video_desc_file = os.path.join(project_path, "prompts", f"{project_id}_video_descriptions.json")
    
    if os.path.exists(video_desc_file):
        st.success("✅ Video descriptions have been generated!")
        
        with open(video_desc_file, 'r') as f:
            video_data = json.load(f)
            video_desc = VideoDescription(**video_data)
        
        st.metric("Total Shots", len(video_desc.video_prompts))
        
        st.markdown("---")
        
        # Display each video prompt
        for i, video_prompt in enumerate(video_desc.video_prompts, 1):
            with st.expander(
                f"🎥 Shot {video_prompt.shot_no} - {video_prompt.prompt_type.title()}",
                expanded=False
            ):
                if video_prompt.prompt_type == "standard" and video_prompt.standard_prompt:
                    prompt = video_prompt.standard_prompt
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Camera Angle:**")
                        st.info(prompt.camera_angle)
                        
                        st.markdown("**Scene Description:**")
                        st.info(prompt.scene_description)
                        
                        st.markdown("**Lighting:**")
                        st.info(prompt.lighting)
                    
                    with col2:
                        if prompt.dialogue:
                            st.markdown("**Dialogue:**")
                            st.success(prompt.dialogue)
                        
                        if prompt.voice_over:
                            st.markdown("**Voice Over:**")
                            st.success(prompt.voice_over)
                        
                        st.markdown("**Additional Notes:**")
                        st.info(prompt.additional_notes)
                
                elif video_prompt.prompt_type == "animated_showcase" and video_prompt.animated_prompt:
                    prompt = video_prompt.animated_prompt
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Camera Angle:**")
                        st.info(prompt.camera_angle)
                        
                        st.markdown("**Scene Description:**")
                        st.info(prompt.scene_description)
                        
                        st.markdown("**Lighting:**")
                        st.info(prompt.lighting)
                    
                    with col2:
                        if prompt.dialogue:
                            st.markdown("**Dialogue:**")
                            st.success(prompt.dialogue)
                        
                        if prompt.voice_over:
                            st.markdown("**Voice Over:**")
                            st.success(prompt.voice_over)
                        
                        st.markdown("**Additional Notes:**")
                        st.info(prompt.additional_notes)
                        
                        if prompt.requires_two_frames:
                            st.warning("⚠️ Requires First & Last Frame Images")
        
        st.markdown("---")
        
        if st.button("🔄 Regenerate Video Descriptions", use_container_width=True):
            regenerate_video_descriptions(project_id, project_path)
            st.rerun()
    
    else:
        # Generate video descriptions
        st.info("Ready to generate video descriptions")
        
        if st.button("🚀 Generate Video Descriptions", type="primary", use_container_width=True):
            generate_video_descriptions(project_id, project_path)
            st.rerun()


def display_video_generation_tab(project_id, project_path):
    """Display video generation tab"""
    
    video_desc_file = os.path.join(project_path, "prompts", f"{project_id}_video_descriptions.json")
    
    if not os.path.exists(video_desc_file):
        st.error("❌ Please generate video descriptions first!")
        return
    
    with open(video_desc_file, 'r') as f:
        video_data = json.load(f)
        video_desc = VideoDescription(**video_data)
    
    # Check if videos already generated
    video_report_file = os.path.join(project_path, "scripts", f"{project_id}_video_generation_report.json")
    
    if os.path.exists(video_report_file):
        with open(video_report_file, 'r') as f:
            report_data = json.load(f)
        
        generated_videos = report_data.get("generated_videos", [])
        failed_generations = report_data.get("failed_generations", [])
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Shots", len(video_desc.video_prompts))
        with col2:
            st.metric("Generated", len(generated_videos))
        with col3:
            st.metric("Failed", len(failed_generations))
        
        st.markdown("---")
        
        # Display videos
        st.subheader("🎬 Generated Videos")
        
        # Display in grid
        cols = st.columns(3)
        for i, video_result in enumerate(generated_videos):
            with cols[i % 3]:
                shot_no = video_result.get('shot_no', 'N/A')
                video_path = video_result.get('video_path', '')
                
                if os.path.exists(video_path):
                    st.video(video_path)
                    st.markdown(f"**Shot {shot_no}**")
                    st.caption(f"Duration: {video_result.get('duration_seconds', 0)}s")
                    
                    # Add edit prompt button
                    if st.button(f"📝 Edit Prompt & Regenerate", key=f"edit_video_{shot_no}", use_container_width=True):
                        st.session_state[f"editing_video_{shot_no}"] = True
                    
                    # Show prompt editor if editing
                    if st.session_state.get(f"editing_video_{shot_no}", False):
                        st.markdown("**Edit Prompt for Regeneration:**")
                        
                        # Get the current prompt from video descriptions
                        current_video_prompt = next((vp for vp in video_desc.video_prompts if vp.shot_no == shot_no), None)
                        current_prompt = ""
                        prompt_type = "standard"
                        
                        if current_video_prompt:
                            prompt_type = current_video_prompt.prompt_type
                            if prompt_type == "standard" and current_video_prompt.standard_prompt:
                                # Build prompt from standard prompt data
                                prompt_data = current_video_prompt.standard_prompt
                                current_prompt = f"Camera Angle: {prompt_data.camera_angle}\n"
                                current_prompt += f"Scene Description: {prompt_data.scene_description}\n"
                                current_prompt += f"Lighting: {prompt_data.lighting}\n"
                                if prompt_data.dialogue:
                                    current_prompt += f"Dialogue: \"{prompt_data.dialogue}\"\n"
                                if prompt_data.voice_over:
                                    current_prompt += f"Voice Over: {prompt_data.voice_over}\n"
                                current_prompt += f"Additional Notes: {prompt_data.additional_notes}"
                            elif prompt_type == "animated_showcase" and current_video_prompt.animated_prompt:
                                # Build prompt from animated prompt data
                                prompt_data = current_video_prompt.animated_prompt
                                current_prompt = f"Camera Angle: {prompt_data.camera_angle}\n"
                                current_prompt += f"Scene Description: {prompt_data.scene_description}\n"
                                current_prompt += f"Lighting: {prompt_data.lighting}\n"
                                if prompt_data.dialogue:
                                    current_prompt += f"Dialogue: \"{prompt_data.dialogue}\"\n"
                                if prompt_data.voice_over:
                                    current_prompt += f"Voice Over: {prompt_data.voice_over}\n"
                                current_prompt += f"Additional Notes: {prompt_data.additional_notes}"
                        
                        custom_prompt = st.text_area(
                            "Custom Prompt:",
                            value=current_prompt,
                            height=200,
                            key=f"prompt_video_{shot_no}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button(f"✨ Regenerate with Custom Prompt", key=f"save_video_{shot_no}", type="primary"):
                                regenerate_single_video_with_prompt(shot_no, custom_prompt, prompt_type, project_id, project_path)
                                st.session_state[f"editing_video_{shot_no}"] = False
                                st.rerun()
                        with col_cancel:
                            if st.button(f"❌ Cancel", key=f"cancel_video_{shot_no}"):
                                st.session_state[f"editing_video_{shot_no}"] = False
                                st.rerun()
                    
                    with st.expander("Details"):
                        st.markdown(f"**Status:** {video_result.get('status', 'N/A')}")
                        st.markdown(f"**Type:** {video_result.get('prompt_type', 'N/A')}")
                        
                        if st.button(f"🔄 Regenerate", key=f"regen_video_{shot_no}"):
                            regenerate_single_video(project_id, project_path, shot_no)
                            st.rerun()
                else:
                    st.error(f"Shot {shot_no} - Video not found")
        
        st.markdown("---")
        
        if failed_generations:
            with st.expander("⚠️ Failed Generations"):
                for failure in failed_generations:
                    st.error(f"Shot {failure.get('shot_no', 'N/A')}: {failure.get('error', 'Unknown error')}")
        
        if st.button("🔄 Regenerate All Videos", use_container_width=True):
            regenerate_all_videos(project_id, project_path)
            st.rerun()
    
    else:
        # Generate videos
        st.info(f"Ready to generate {len(video_desc.video_prompts)} video(s)")
        
        st.markdown("### Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["16:9", "9:16", "1:1"],
                index=0
            )
        
        with col2:
            show_progress = st.checkbox("Show Progress", value=True)
        
        st.markdown("---")
        
        st.warning("⚠️ Video generation will take several minutes. Please be patient.")
        
        if st.button("🚀 Generate All Videos", type="primary", use_container_width=True):
            with st.spinner("🎬 Generating videos... This will take several minutes."):
                generate_all_videos(project_id, project_path, aspect_ratio)
                st.rerun()


def generate_video_descriptions(project_id, project_path):
    """Generate video descriptions"""
    # Load scene descriptions
    scene_desc_file = os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json")
    
    with open(scene_desc_file, 'r') as f:
        scene_data = json.load(f)
    
    # Load script
    with open(os.path.join(project_path, "scripts", f"{project_id}_shot_script.json"), 'r') as f:
        script_data = json.load(f)
    
    # Load brand info
    with open(os.path.join(project_path, "scripts", "brand_info.json"), 'r') as f:
        brand_info = json.load(f)
    
    generator = VideoDescriptionGenerator()
    
    video_descriptions = generator.generate_video_descriptions(
        shots=script_data['shots'],
        ad_title=script_data['ad_title'],
        enable_animation_for_finale=True
    )
    
    # Save
    video_desc_json = generator.save_video_descriptions(
        video_descriptions,
        f"{project_id}_video_descriptions.json",
        os.path.join(project_path, "prompts")
    )


def regenerate_video_descriptions(project_id, project_path):
    """Regenerate video descriptions"""
    video_desc_file = os.path.join(project_path, "prompts", f"{project_id}_video_descriptions.json")
    if os.path.exists(video_desc_file):
        os.remove(video_desc_file)
    
    generate_video_descriptions(project_id, project_path)


def generate_all_videos(project_id, project_path, aspect_ratio="16:9"):
    """Generate all videos"""
    # Load video descriptions
    with open(os.path.join(project_path, "prompts", f"{project_id}_video_descriptions.json"), 'r') as f:
        video_data = json.load(f)
        video_desc = VideoDescription(**video_data)
    
    # Load scene images
    generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
    with open(generation_report_file, 'r') as f:
        scene_report = json.load(f)
    
    scene_images_dict = scene_report.get("generated_images", {})
    
    # Convert to shot_no -> image_path mapping
    scene_images = {}
    for shot_key, img_data in scene_images_dict.items():
        shot_no = img_data.get('shot_no')
        if shot_no:
            scene_images[shot_no] = img_data.get('filepath')
    
    # Load script
    with open(os.path.join(project_path, "scripts", f"{project_id}_shot_script.json"), 'r') as f:
        script_data = json.load(f)
    
    # Convert video descriptions to list format
    video_prompts_list = []
    for vp in video_desc.video_prompts:
        vp_dict = vp.model_dump()
        video_prompts_list.append(vp_dict)
    
    # Generate videos
    generator = VideoGenerator(
        output_dir=os.path.join(project_path, "generated_videos"),
        aspect_ratio=aspect_ratio
    )
    
    generation_results = generator.generate_all_videos(
        shots=script_data['shots'],
        video_prompts=video_prompts_list,
        scene_images=scene_images,
        ad_title=script_data['ad_title'],
        project_id=project_id
    )
    
    # Save report
    report_path = generator.save_generation_report(
        f"{project_id}_video_generation_report.json",
        os.path.join(project_path, "scripts")
    )


def regenerate_all_videos(project_id, project_path):
    """Regenerate all videos"""
    video_report_file = os.path.join(project_path, "scripts", f"{project_id}_video_generation_report.json")
    if os.path.exists(video_report_file):
        os.remove(video_report_file)
    
    generate_all_videos(project_id, project_path)


def regenerate_single_video_with_prompt(shot_no, custom_prompt, prompt_type, project_id, project_path):
    """Regenerate a single video with custom prompt"""
    # Load video descriptions
    with open(os.path.join(project_path, "prompts", f"{project_id}_video_descriptions.json"), 'r') as f:
        video_data = json.load(f)
        video_desc = VideoDescription(**video_data)
    
    # Find the video prompt
    current_video_prompt = next((vp for vp in video_desc.video_prompts if vp.shot_no == shot_no), None)
    if not current_video_prompt:
        st.error(f"Video prompt for shot {shot_no} not found")
        return
    
    # Load scene images
    generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
    with open(generation_report_file, 'r') as f:
        scene_report = json.load(f)
    
    scene_images = scene_report.get("generated_images", {})
    scene_image_path = None
    
    # Find the scene image for this shot
    for shot_key, img_data in scene_images.items():
        if img_data.get('shot_no') == shot_no:
            scene_image_path = img_data.get('filepath')
            break
    
    if not scene_image_path or not os.path.exists(scene_image_path):
        st.error(f"Scene image for shot {shot_no} not found")
        return
    
    # Load script to get shot info
    with open(os.path.join(project_path, "scripts", f"{project_id}_shot_script.json"), 'r') as f:
        script_data = json.load(f)
    
    # Find the shot
    shot_info = None
    for shot in script_data['shots']:
        if shot.get('shot_no') == shot_no:
            shot_info = shot
            break
    
    if not shot_info:
        st.error(f"Shot {shot_no} not found in script")
        return
    
    # Generate video with custom prompt
    generator = VideoGenerator(
        output_dir=os.path.join(project_path, "generated_videos"),
        aspect_ratio="16:9"
    )
    
    new_video_path = generator.generate_single_video_with_prompt(
        shot_no=shot_no,
        shot=shot_info,
        video_prompt=custom_prompt,
        scene_image_path=scene_image_path,
        project_id=project_id,
        prompt_type=prompt_type
    )
    
    if new_video_path:
        # Update the video generation report
        video_report_file = os.path.join(project_path, "scripts", f"{project_id}_video_generation_report.json")
        if os.path.exists(video_report_file):
            with open(video_report_file, 'r') as f:
                report_data = json.load(f)
            
            # Update the specific shot's video path
            generated_videos = report_data.get("generated_videos", [])
            for video_result in generated_videos:
                if video_result.get('shot_no') == shot_no:
                    video_result['video_path'] = new_video_path
                    break
            
            with open(video_report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
        
        st.success(f"✅ Successfully regenerated video for shot {shot_no}")
    else:
        st.error(f"❌ Failed to regenerate video for shot {shot_no}")


def regenerate_single_video(project_id, project_path, shot_no):
    """Regenerate a single video"""
    # This would need to be implemented based on the video generator
    st.info("Single video regeneration coming soon...")
