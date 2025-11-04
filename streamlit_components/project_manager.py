"""
Project Manager Component
Handles project creation and loading from existing projects
"""

import streamlit as st
import os
import json
from pathlib import Path


def list_existing_projects(projects_dir="projects_data"):
    """List all existing projects"""
    if not os.path.exists(projects_dir):
        return []
    
    projects = []
    for item in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, item)
        if os.path.isdir(project_path) and not item.startswith('.'):
            projects.append(item)
    
    return sorted(projects)


def project_selection_ui(projects_dir="projects_data"):
    """Display project selection or creation UI"""
    
    st.header("📁 Project Manager")
    
    existing_projects = list_existing_projects(projects_dir)
    
    # Tabs for New or Existing Project
    tab1, tab2 = st.tabs(["➕ Create New Project", "📂 Load Existing Project"])
    
    with tab1:
        st.subheader("Create New Project")
        st.markdown("Enter details for your new ad production project")
        
        col1, col2 = st.columns(2)
        
        project_name = col1.text_input(
            "Project ID *",
            placeholder="e.g., deconstruct_sunscreen_001",
            help="Use lowercase letters, numbers, and underscores"
        )
        
        aspect_ratio = col2.selectbox(
            "Aspect Ratio",
            ["16:9", "9:16", "1:1"],
            index=0
        )
        
        duration = st.slider("Ad Duration (seconds)", 15, 60, 30, 15)
        
        st.markdown("---")
        
        if st.button("✅ Create Project", type="primary", use_container_width=True):
            if project_name:
                if not project_name.replace("_", "").replace("-", "").replace(" ", "").isalnum():
                    st.error("❌ Project name should only contain letters, numbers, underscores, and hyphens")
                else:
                    project_path = os.path.join(projects_dir, project_name)
                    if os.path.exists(project_path):
                        st.error(f"❌ Project '{project_name}' already exists!")
                    else:
                        # Create project structure
                        os.makedirs(project_path, exist_ok=True)
                        os.makedirs(os.path.join(project_path, "character_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "location_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "outfit_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "character_outfit_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "product_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "scene_images"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "prompts"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "generated_videos"), exist_ok=True)
                        os.makedirs(os.path.join(project_path, "final_videos"), exist_ok=True)
                        
                        # Save project metadata
                        metadata = {
                            "project_id": project_name,
                            "aspect_ratio": aspect_ratio,
                            "duration": duration,
                            "created_at": str(Path(__file__).stat().st_mtime) if os.path.exists(__file__) else ""
                        }
                        
                        with open(os.path.join(project_path, "project_metadata.json"), 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        st.session_state["project_id"] = project_name
                        st.session_state["project_path"] = project_path
                        st.session_state["aspect_ratio"] = aspect_ratio
                        st.session_state["duration"] = duration
                        st.session_state["project_created"] = True
                        
                        st.success(f"✅ Project '{project_name}' created successfully!")
                     
                        st.rerun()
            else:
                st.error("❌ Please enter a project name")
    
    with tab2:
        st.subheader("Load Existing Project")
        
        if existing_projects:
            st.markdown(f"Found **{len(existing_projects)}** existing project(s):")
            
            selected_project = st.selectbox(
                "Select a project to load:",
                options=existing_projects,
                key="existing_project_selector"
            )
            
            if selected_project:
                # Load project metadata
                project_path = os.path.join(projects_dir, selected_project)
                metadata_file = os.path.join(project_path, "project_metadata.json")
                
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Project:** {selected_project}")
                    with col2:
                        st.info(f"**Aspect Ratio:** {metadata.get('aspect_ratio', 'N/A')}")
                
                st.markdown("---")
                
                if st.button("📂 Load Project", type="primary", use_container_width=True):
                    # Load existing project data
                    load_project_data(selected_project, project_path, projects_dir)
                    
        else:
            st.info("No existing projects found. Create a new project to get started!")


def load_project_data(project_id, project_path, projects_dir="projects_data"):
    """Load all available data from an existing project"""
    
    st.session_state["project_id"] = project_id
    st.session_state["project_path"] = project_path
    st.session_state["project_created"] = False  # Existing project
    
    # Load metadata
    metadata_file = os.path.join(project_path, "project_metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        st.session_state["aspect_ratio"] = metadata.get("aspect_ratio", "16:9")
        st.session_state["duration"] = metadata.get("duration", 30)
    
    # Load brand info if exists
    brand_info_file = os.path.join(project_path, "scripts", "brand_info.json")
    if os.path.exists(brand_info_file):
        with open(brand_info_file, 'r') as f:
            st.session_state["brand_info"] = json.load(f)
    
    # Load selected concept if exists
    concept_file = os.path.join(project_path, "scripts", "selected_concept.json")
    if os.path.exists(concept_file):
        with open(concept_file, 'r') as f:
            st.session_state["selected_concept"] = json.load(f)
            st.session_state["ad_concept_selected"] = True  # Mark as selected
    
    # Load generated concepts if they exist
    concepts_file = os.path.join(project_path, "ad_concepts.json")
    if os.path.exists(concepts_file):
        with open(concepts_file, 'r') as f:
            concepts_data = json.load(f)
            st.session_state["generated_concepts"] = concepts_data.get("ad_concepts", [])
            st.session_state["concepts_generated"] = True
    
    st.success(f"✅ Project '{project_id}' loaded successfully!")
    st.balloons()
    
    # Show what's already generated
    show_project_status(project_path)
    
    st.rerun()


def show_project_status(project_path):
    """Show status of what's been generated in the project"""
    
    st.markdown("### 📊 Project Status")
    
    status_items = []
    
    # Check script
    script_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_shot_script.json")
    if os.path.exists(script_file):
        status_items.append(("📝 Shot Script", "✅", "Generated"))
    
    # Check characters
    char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    if os.path.exists(char_file):
        with open(char_file, 'r') as f:
            char_data = json.load(f)
            num_chars = len(char_data.get("characters", []))
        status_items.append((f"👥 Characters", "✅", f"{num_chars} characters"))
    
    # Check locations
    loc_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
    if os.path.exists(loc_file):
        with open(loc_file, 'r') as f:
            loc_data = json.load(f)
            num_locs = len(loc_data.get("locations", []))
        status_items.append((f"📍 Locations", "✅", f"{num_locs} locations"))
    
    # Check outfits
    outfit_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    if os.path.exists(outfit_file):
        with open(outfit_file, 'r') as f:
            outfit_data = json.load(f)
            num_outfits = len(outfit_data.get("outfits", []))
        status_items.append((f"👕 Outfits", "✅", f"{num_outfits} outfits"))
    
    # Check scenes
    scene_file = os.path.join(project_path, "prompts", f"{os.path.basename(project_path)}_scene_descriptions.json")
    if os.path.exists(scene_file):
        status_items.append(("🎬 Scene Descriptions", "✅", "Generated"))
    
    # Check scene images
    scene_images_dir = os.path.join(project_path, "scene_images")
    if os.path.exists(scene_images_dir) and os.listdir(scene_images_dir):
        num_scenes = len([f for f in os.listdir(scene_images_dir) if f.endswith('.png')])
        status_items.append((f"🖼️ Scene Images", "✅", f"{num_scenes} images"))
    
    # Display status
    cols = st.columns(min(len(status_items), 3))
    for i, (name, status, detail) in enumerate(status_items):
        with cols[i % 3]:
            st.metric(name, detail)
