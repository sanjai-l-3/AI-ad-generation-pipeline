"""
Stage 1: Script Generation Component
"""

import streamlit as st
import os
import json
from services.script_generation.script_generator import ShotScriptGenerator, ShotScript


def display_script_generation_ui(brand_info, ad_concept, project_id):
    """Display script generation stage UI"""
    
    st.header("📝 Stage 1: Shot Script Generation")
    st.info(f"**Project:** `{project_id}`")
    
    script_file = f"projects_data/{project_id}/scripts/{project_id}_shot_script.json"
    
    # Check if script already exists
    if os.path.exists(script_file):
        st.success("✅ Script already generated!")
        
        with open(script_file, 'r') as f:
            script_data = json.load(f)
            shot_script = ShotScript(**script_data)
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Shots", len(shot_script.shots))
        with col2:
            st.metric("Characters", len(shot_script.characters_info))
        with col3:
            st.metric("Locations", len(shot_script.location_info))
        
        st.markdown("---")
        
        # Display shots
        st.subheader("📋 Generated Shots")
        
        for i, shot in enumerate(shot_script.shots, 1):
            with st.expander(f"🎬 Shot {shot.shot_no}: {shot.time_stamp} | {shot.duration}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Location:** {shot.location_name}")
                    st.markdown(f"**Camera:** {shot.camera_angle}")
                    st.markdown(f"**Key Focus:** {shot.key_focus}")
                    st.markdown(f"**Dialogue:** {shot.dialogue}")
                    st.markdown(f"**Voice Over:** {shot.voice_over}")
                
                with col2:
                    st.markdown(f"**Action:** {shot.action}")
                    st.markdown(f"**Visual:** {shot.visual_description}")
                    if shot.text_overlay and shot.text_overlay != "None":
                        st.markdown(f"**Text Overlay:** {shot.text_overlay}")
                
                st.markdown("**Characters Involved:**")
                for char in shot.characters_involved:
                    st.markdown(f"- {char}")
        
        # Regenerate options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Regenerate Script", use_container_width=True):
                if regenerate_script(brand_info, ad_concept, project_id):
                    st.success("✅ Script regenerated!")
                    st.rerun()
        
        with col2:
            if st.button("➡️ Continue to Next Stage", type="primary", use_container_width=True):
                st.session_state["current_stage"] = "characters_locations"
                st.rerun()
    
    else:
        # Generate script
        st.info("No script found. Let's generate one!")
        
        if st.button("🚀 Generate Shot Script", type="primary", use_container_width=True):
            generate_script(brand_info, ad_concept, project_id)


def generate_script(brand_info, ad_concept, project_id):
    """Generate shot script"""
    
    with st.spinner("📝 Generating shot script... This may take a minute."):
        try:
            generator = ShotScriptGenerator()
            shot_script = generator.generate_shot_script(
                ad_concept=ad_concept,
                brand_info=brand_info
            )
            
            # Save script
            os.makedirs(f"projects_data/{project_id}/scripts", exist_ok=True)
            
            generator.save_shot_script_json(
                shot_script,
                f"{project_id}_shot_script.json",
                f"projects_data/{project_id}/scripts"
            )
            
            st.success("✅ Script generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating script: {str(e)}")
            st.exception(e)


def regenerate_script(brand_info, ad_concept, project_id):
    """Regenerate shot script"""
    
    script_file = f"projects_data/{project_id}/scripts/{project_id}_shot_script.json"
    
    if os.path.exists(script_file):
        os.remove(script_file)
    
    generate_script(brand_info, ad_concept, project_id) 