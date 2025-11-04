"""
Stage 4: Scene Description and Scene Image Generation Component
Modern UI with descriptions and images
"""

import streamlit as st
import os
import json
from PIL import Image
from services.scene_description_generation.scene_description_generator import SceneDescriptionGenerator, SceneDescription
try:
    from services.scene_generation.scene_image_generator import SceneImageGenerator
except ImportError:
    SceneImageGenerator = None
    st.warning("SceneImageGenerator not available")


def display_scene_generation_ui(project_id, project_path):
    """Display scene description and image generation stage"""
    
    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">🎬 Scene Description & Image Generation</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Generate scene descriptions and scene images</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 Scene Descriptions", "🖼️ Scene Images"])
    
    with tab1:
        display_scene_descriptions_tab(project_id, project_path)
    
    with tab2:
        display_scene_images_tab(project_id, project_path)


def display_scene_descriptions_tab(project_id, project_path):
    """Display scene descriptions generation tab"""
    
    scene_desc_file = os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json")
    
    if os.path.exists(scene_desc_file):
        st.success("✅ Scene descriptions have been generated!")
        
        with open(scene_desc_file, 'r') as f:
            scene_data = json.load(f)
            scene_desc = SceneDescription(**scene_data)
        
        st.metric("Total Shots", len(scene_desc.shots))
        
        st.markdown("---")
        
        # Display each shot with description
        for i, shot in enumerate(scene_desc.shots, 1):
            with st.expander(
                f"🎬 Shot {shot.shot_no}: {shot.time_stamp} | Location: {shot.location_name}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Image Prompt:**")
                    st.text_area(
                        "",
                        value=shot.image_prompt if shot.image_prompt else "No prompt generated yet",
                        height=200,
                        key=f"prompt_{i}",
                        disabled=True
                    )
                
                with col2:
                    st.markdown("**Shot Details:**")
                    st.markdown(f"**Duration:** {shot.duration}")
                    st.markdown(f"**Camera:** {shot.camera_angle}")
                    st.markdown(f"**Dialogue:** {shot.dialogue}")
                    st.markdown(f"**Voice Over:** {shot.voice_over}")
                    
                    st.markdown("**Characters:**")
                    for char in shot.characters_involved:
                        st.markdown(f"• {char}")
        
        st.markdown("---")
        
        if st.button("🔄 Regenerate Scene Descriptions", use_container_width=True):
            with st.spinner("Regenerating scene descriptions..."):
                regenerate_scene_descriptions(project_id, project_path)
            st.rerun()
    
    else:
        # Generate scene descriptions
        st.info("Ready to generate scene descriptions")
        
        if st.button("🚀 Generate Scene Descriptions", type="primary", use_container_width=True):
            with st.spinner("Generating scene descriptions..."):
                generate_scene_descriptions(project_id, project_path)
            st.rerun()


def display_scene_images_tab(project_id, project_path):
    """Display scene images generation tab"""
    
    scene_desc_file = os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json")
    
    if not os.path.exists(scene_desc_file):
        st.error("❌ Please generate scene descriptions first!")
        return
    
    with open(scene_desc_file, 'r') as f:
        scene_data = json.load(f)
        scene_desc = SceneDescription(**scene_data)
    
    # Check if images already generated
    generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
    
    if os.path.exists(generation_report_file):
        with open(generation_report_file, 'r') as f:
            report_data = json.load(f)
        
        generated_images = report_data.get("generated_images", {})
        failed_generations = report_data.get("failed_generations", [])
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Shots", len(scene_desc.shots))
        with col2:
            st.metric("Generated", len(generated_images))
        with col3:
            st.metric("Failed", len(failed_generations))
        
        st.markdown("---")
        
        # Display images
        st.subheader("🖼️ Scene Images Gallery")
        
        # Display in grid
        cols = st.columns(3)
        for i, (shot_id, img_data) in enumerate(generated_images.items()):
            with cols[i % 3]:
                shot_no = img_data.get('shot_no', 'N/A')
                filepath = img_data.get('filepath', '')
                
                if os.path.exists(filepath):
                    st.image(filepath, caption=f"Shot {shot_no}", use_container_width=True)
                    
                    # Add edit prompt button
                    if st.button(f"📝 Edit Prompt & Regenerate", key=f"edit_shot_{shot_no}", use_container_width=True):
                        st.session_state[f"editing_shot_{shot_no}"] = True
                    
                    # Show prompt editor if editing
                    if st.session_state.get(f"editing_shot_{shot_no}", False):
                        st.markdown("**Edit Prompt for Regeneration:**")
                        
                        # Get the current prompt from scene descriptions
                        current_shot = next((s for s in scene_desc.shots if s.shot_no == shot_no), None)
                        current_prompt = current_shot.image_prompt if current_shot else ""
                        
                        custom_prompt = st.text_area(
                            "Custom Prompt:",
                            value=current_prompt,
                            height=150,
                            key=f"prompt_shot_{shot_no}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button(f"✨ Regenerate with Custom Prompt", key=f"save_shot_{shot_no}", type="primary"):
                                with st.spinner("Regenerating shot with custom prompt..."):
                                    regenerate_single_scene_with_prompt(shot_no, custom_prompt, project_id, project_path)
                                st.session_state[f"editing_shot_{shot_no}"] = False
                                st.rerun()
                        with col_cancel:
                            if st.button(f"❌ Cancel", key=f"cancel_shot_{shot_no}"):
                                st.session_state[f"editing_shot_{shot_no}"] = False
                                st.rerun()
                    
                    with st.expander(f"📝 Shot {shot_no} Details"):
                        st.markdown(f"**Location:** {img_data.get('location_name', 'N/A')}")
                        st.markdown(f"**File:** {os.path.basename(filepath)}")
                        
                        if st.button(f"🔄 Regenerate", key=f"regen_shot_{shot_no}"):
                            with st.spinner("Regenerating shot image..."):
                                regenerate_single_scene_image(project_id, project_path, shot_no)
                            st.rerun()
                else:
                    st.info(f"Shot {shot_no} - Image not found")
        
        st.markdown("---")
        
        if failed_generations:
            with st.expander("⚠️ Failed Generations"):
                for failure in failed_generations:
                    st.error(f"Shot {failure.get('shot_no', 'N/A')}: {failure.get('error', 'Unknown error')}")
        
        if st.button("🔄 Regenerate All Scene Images", use_container_width=True):
            regenerate_all_scene_images(project_id, project_path)
            st.rerun()
    
    else:
        # Generate scene images
        st.info(f"Ready to generate {len(scene_desc.shots)} scene image(s)")
        
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
        
        if st.button("🚀 Generate All Scene Images", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating scene images... This will take several minutes."):
                generate_all_scene_images(project_id, project_path, aspect_ratio)
                st.rerun()


def generate_scene_descriptions(project_id, project_path):
    """Generate scene descriptions"""
    # Load required data
    with open(os.path.join(project_path, "scripts", f"{project_id}_shot_script.json"), 'r') as f:
        script_data = json.load(f)
    
    with open(os.path.join(project_path, "scripts", "brand_info.json"), 'r') as f:
        brand_info = json.load(f)
    
    # Load ad concept
    ad_concept = None
    if os.path.exists(os.path.join(project_path, "scripts", "selected_concept.json")):
        with open(os.path.join(project_path, "scripts", "selected_concept.json"), 'r') as f:
            ad_concept = json.load(f)
    
    with open(os.path.join(project_path, "scripts", f"{project_id}_characters.json"), 'r') as f:
        char_data = json.load(f)
    
    with open(os.path.join(project_path, "scripts", f"{project_id}_locations.json"), 'r') as f:
        loc_data = json.load(f)
    
    # Convert dict shots to Shot objects
    from services.script_generation.script_generator import Shot as ScriptShot
    shots_list = []
    for shot_data in script_data['shots']:
        if isinstance(shot_data, dict):
            shots_list.append(ScriptShot(**shot_data))
        else:
            shots_list.append(shot_data)
    
    generator = SceneDescriptionGenerator()
    scene_descriptions = generator.generate_scene_descriptions(
        shots=shots_list,
        brand_info=brand_info,
        ad_title=script_data['ad_title'],
        characters_info=char_data['characters'],
        locations_info=loc_data['locations'],
        ad_concept=ad_concept
    )
    
    # Save
    scene_desc_json = generator.save_scene_descriptions(
        scene_descriptions,
        f"{project_id}_scene_descriptions.json",
        os.path.join(project_path, "prompts")
    )


def regenerate_scene_descriptions(project_id, project_path):
    """Regenerate scene descriptions"""
    scene_desc_file = os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json")
    if os.path.exists(scene_desc_file):
        os.remove(scene_desc_file)
    
    generate_scene_descriptions(project_id, project_path)


def generate_all_scene_images(project_id, project_path, aspect_ratio="16:9"):
    """Generate all scene images"""
    # Load scene descriptions
    with open(os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json"), 'r') as f:
        scene_data = json.load(f)
        scene_desc = SceneDescription(**scene_data)
    
    # Load characters and locations
    with open(os.path.join(project_path, "scripts", f"{project_id}_characters.json"), 'r') as f:
        char_data = json.load(f)
    
    with open(os.path.join(project_path, "scripts", f"{project_id}_locations.json"), 'r') as f:
        loc_data = json.load(f)
    
    char_outfit_file = os.path.join(project_path, "scripts", f"{project_id}_character_outfits.json")
    char_outfits = []
    if os.path.exists(char_outfit_file):
        with open(char_outfit_file, 'r') as f:
            char_outfit_data = json.load(f)
            char_outfits = char_outfit_data.get("character_outfits", [])
    
    # Load product image path if exists
    brand_info_file = os.path.join(project_path, "scripts", "brand_info.json")
    product_info = None
    if os.path.exists(brand_info_file):
        with open(brand_info_file, 'r') as f:
            brand_info_data = json.load(f)
            product_image_path = brand_info_data.get("product_image_path")
            
            if product_image_path and os.path.exists(product_image_path):
                product_info = {
                    "name": brand_info_data.get("product_name", "product"),
                    "image_path": product_image_path
                }
    
    # Generate images
    generator = SceneImageGenerator(
        output_dir=os.path.join(project_path, "scene_images")
    )
    
    generation_results = generator.generate_all_scene_images(
        scene_description=scene_desc,
        characters_info=char_data['characters'],
        locations_info=loc_data['locations'],
        character_outfit_images=char_outfits,
        product_info=product_info,  # Pass actual product info
        aspect_ratio=aspect_ratio,
        project_id=project_id
    )
    
    # Save report
    report_path = generator.save_generation_report(
        f"{project_id}_scene_generation_report.json",
        os.path.join(project_path, "scripts")
    )


def regenerate_all_scene_images(project_id, project_path):
    """Regenerate all scene images"""
    generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
    if os.path.exists(generation_report_file):
        os.remove(generation_report_file)
    
    generate_all_scene_images(project_id, project_path)


def regenerate_single_scene_image(project_id, project_path, shot_no):
    """Regenerate a single scene image"""
    # Load scene descriptions
    scene_desc_path = os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json")
    if not os.path.exists(scene_desc_path):
        st.error("Scene descriptions not found. Generate them first.")
        return
    with open(scene_desc_path, 'r') as f:
        scene_data = json.load(f)
        scene_desc = SceneDescription(**scene_data)

    # Find the shot
    current_shot = next((s for s in scene_desc.shots if s.shot_no == shot_no), None)
    if not current_shot:
        st.error(f"Shot {shot_no} not found")
        return

    shot_dict = current_shot.model_dump()

    # Load characters and locations
    with open(os.path.join(project_path, "scripts", f"{project_id}_characters.json"), 'r') as f:
        char_data = json.load(f)

    with open(os.path.join(project_path, "scripts", f"{project_id}_locations.json"), 'r') as f:
        loc_data = json.load(f)

    # Get character-outfit mappings for this shot
    char_outfit_refs = []
    char_outfit_file = os.path.join(project_path, "scripts", f"{project_id}_character_outfits.json")
    if os.path.exists(char_outfit_file):
        with open(char_outfit_file, 'r') as f:
            char_outfit_data = json.load(f)
            outfit_mappings = shot_dict.get('outfit_character_mapping', [])
            for mapping in outfit_mappings:
                char_name = mapping.get('character_name', '').lower()
                outfit_name = mapping.get('outfit_name', '').lower()
                for combo in char_outfit_data.get('character_outfits', []):
                    if combo.get('character_name', '').lower() == char_name and combo.get('outfit_name', '').lower() == outfit_name:
                        char_outfit_refs.append(combo)
                        break

    # Get location reference
    location_ref = None
    loc_name = shot_dict.get('location_name', '')
    if loc_name:
        for loc in loc_data['locations']:
            if loc.get('name', '').lower() == loc_name.lower():
                location_ref = loc
                break

    # Get product reference
    product_info = None
    brand_info_file = os.path.join(project_path, "scripts", "brand_info.json")
    if os.path.exists(brand_info_file):
        with open(brand_info_file, 'r') as f:
            brand_info_data = json.load(f)
            product_image_path = brand_info_data.get("product_image_path")
            if product_image_path and os.path.exists(product_image_path):
                product_info = {
                    "name": brand_info_data.get("product_name", "product"),
                    "image_path": product_image_path
                }

    # Use the existing image prompt from scene description
    image_prompt = current_shot.image_prompt

    generator = SceneImageGenerator(output_dir=os.path.join(project_path, "scene_images"))

    new_image_path = generator.generate_scene_image(
        shot=shot_dict,
        image_prompt=image_prompt,
        character_outfit_refs=char_outfit_refs,
        location_ref=location_ref,
        product_ref=product_info,
        aspect_ratio="16:9",
        project_id=project_id
    )

    if new_image_path:
        # Update the generation report
        generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
        if os.path.exists(generation_report_file):
            with open(generation_report_file, 'r') as f:
                report_data = json.load(f)

            shot_key = f"shot_{shot_no}"
            if shot_key in report_data.get("generated_images", {}):
                report_data["generated_images"][shot_key]["filepath"] = new_image_path
            else:
                # If not present, add entry
                if "generated_images" not in report_data:
                    report_data["generated_images"] = {}
                report_data["generated_images"][shot_key] = {
                    "filepath": new_image_path,
                    "shot_no": shot_no,
                    "status": "success"
                }

            with open(generation_report_file, 'w') as f:
                json.dump(report_data, f, indent=2)


def regenerate_single_scene_with_prompt(shot_no, custom_prompt, project_id, project_path):
    """Regenerate a single scene image with custom prompt"""
    # Load scene descriptions
    with open(os.path.join(project_path, "prompts", f"{project_id}_scene_descriptions.json"), 'r') as f:
        scene_data = json.load(f)
        scene_desc = SceneDescription(**scene_data)
    
    # Find the shot
    current_shot = next((s for s in scene_desc.shots if s.shot_no == shot_no), None)
    if not current_shot:
        st.error(f"Shot {shot_no} not found")
        return
    
    shot_dict = current_shot.model_dump()
    
    # Load characters and locations
    with open(os.path.join(project_path, "scripts", f"{project_id}_characters.json"), 'r') as f:
        char_data = json.load(f)
    
    with open(os.path.join(project_path, "scripts", f"{project_id}_locations.json"), 'r') as f:
        loc_data = json.load(f)
    
    # Get character-outfit mappings for this shot
    char_outfit_refs = []
    char_outfit_file = os.path.join(project_path, "scripts", f"{project_id}_character_outfits.json")
    if os.path.exists(char_outfit_file):
        with open(char_outfit_file, 'r') as f:
            char_outfit_data = json.load(f)
            # Filter for this shot's character-outfit combinations
            outfit_mappings = shot_dict.get('outfit_character_mapping', [])
            for mapping in outfit_mappings:
                char_name = mapping.get('character_name', '').lower()
                outfit_name = mapping.get('outfit_name', '').lower()
                # Find matching combination
                for combo in char_outfit_data.get('character_outfits', []):
                    if combo.get('character_name', '').lower() == char_name and combo.get('outfit_name', '').lower() == outfit_name:
                        char_outfit_refs.append(combo)
                        break
    
    # Get location reference
    location_ref = None
    loc_name = shot_dict.get('location_name', '')
    if loc_name:
        for loc in loc_data['locations']:
            if loc.get('name', '').lower() == loc_name.lower():
                location_ref = loc
                break
    
    # Get product reference
    product_info = None
    brand_info_file = os.path.join(project_path, "scripts", "brand_info.json")
    if os.path.exists(brand_info_file):
        with open(brand_info_file, 'r') as f:
            brand_info_data = json.load(f)
            product_image_path = brand_info_data.get("product_image_path")
            if product_image_path and os.path.exists(product_image_path):
                product_info = {
                    "name": brand_info_data.get("product_name", "product"),
                    "image_path": product_image_path
                }
    
    # Generate image with custom prompt
    generator = SceneImageGenerator(output_dir=os.path.join(project_path, "scene_images"))
    
    new_image_path = generator.generate_single_scene_image_with_prompt(
        shot=shot_dict,
        custom_prompt=custom_prompt,
        character_outfit_refs=char_outfit_refs,
        location_ref=location_ref,
        product_ref=product_info,
        aspect_ratio="16:9",
        project_id=project_id
    )
    
    if new_image_path:
        # Update the generation report
        generation_report_file = os.path.join(project_path, "scripts", f"{project_id}_scene_generation_report.json")
        if os.path.exists(generation_report_file):
            with open(generation_report_file, 'r') as f:
                report_data = json.load(f)
            
            # Update the specific shot's image path
            shot_key = f"shot_{shot_no}"
            if shot_key in report_data.get("generated_images", {}):
                report_data["generated_images"][shot_key]["filepath"] = new_image_path
            
            with open(generation_report_file, 'w') as f:
                json.dump(report_data, f, indent=2) 