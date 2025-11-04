"""
Ad Production Pipeline - Main Streamlit Application
Complete stage-wise pipeline with editing and regeneration capabilities
"""

import streamlit as st
import os
import json
from streamlit_components.project_manager import project_selection_ui, list_existing_projects
from streamlit_components.brand_info_collector import collect_brand_info
from streamlit_components.ad_concept_selector import generate_and_select_ad_concepts
from streamlit_components.stage_script_generation import display_script_generation_ui
from streamlit_components.stage_characters_locations import display_characters_locations_ui
from streamlit_components.stage_outfits import display_outfits_ui
from streamlit_components.stage_scene_generation import display_scene_generation_ui
from streamlit_components.stage_video_generation import display_video_generation_ui

# Page Configuration
st.set_page_config(
    page_title="Ad Production Pipeline",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stage-header {
        background: linear-gradient(90deg, #1f77b4 0%, #ff6b6b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎬 AI Ads Generation</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Stage-wise Pipeline with Editing & Regeneration</p>', unsafe_allow_html=True)
    
    # Check if project is selected
    if "project_id" not in st.session_state:
        project_selection_ui()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Pipeline Stages")
        
        stages = [
            ("1️⃣", "Brand Info & Ad Concept", "concept"),
            ("2️⃣", "Script Generation", "script"),
            ("3️⃣", "Characters & Locations", "characters_locations"),
            ("4️⃣", "Outfits", "outfits"),
            ("5️⃣", "Scene Generation", "scene_description"),
            ("6️⃣", "Video Generation", "video")
        ]
        
        if "current_stage" not in st.session_state:
            st.session_state["current_stage"] = "concept"
        
        current_stage = st.session_state["current_stage"]
        
        for icon, name, stage_key in stages:
            if stage_key == current_stage:
                st.markdown(f"### {icon} {name} ✓")
            else:
                if st.button(f"{icon} {name}", use_container_width=True, key=f"nav_{stage_key}"):
                    st.session_state["current_stage"] = stage_key
                    st.rerun()
        
        st.markdown("---")
        
        # Project Info
        if "project_id" in st.session_state:
            st.markdown("### 📁 Project")
            st.info(st.session_state["project_id"])
            
            # Show completed stages
            project_path = st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
            
            completed_stages = []
            
            # Check brand info
            if os.path.exists(os.path.join(project_path, "scripts", "brand_info.json")):
                completed_stages.append("Brand Info")
            
            # Check selected concept
            if os.path.exists(os.path.join(project_path, "scripts", "selected_concept.json")):
                completed_stages.append("Ad Concept")
            
            # Check script
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_shot_script.json")):
                completed_stages.append("Script")
            
            # Check characters
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_characters.json")):
                completed_stages.append("Characters")
            
            # Check locations
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_locations.json")):
                completed_stages.append("Locations")
            
            # Check outfits
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_outfits.json")):
                completed_stages.append("Outfits")
            
            # Check character-outfits
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_character_outfits.json")):
                completed_stages.append("Character-Outfits")
            
            # Check scene descriptions
            if os.path.exists(os.path.join(project_path, "prompts", f"{st.session_state['project_id']}_scene_descriptions.json")):
                completed_stages.append("Scene Descriptions")
            
            # Check scene images
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_scene_generation_report.json")):
                completed_stages.append("Scene Images")
            
            # Check video descriptions
            if os.path.exists(os.path.join(project_path, "prompts", f"{st.session_state['project_id']}_video_descriptions.json")):
                completed_stages.append("Video Descriptions")
            
            # Check videos
            if os.path.exists(os.path.join(project_path, "scripts", f"{st.session_state['project_id']}_video_generation_report.json")):
                completed_stages.append("Videos")
            
            if completed_stages:
                st.markdown("### ✅ Completed Stages")
                for stage in completed_stages:
                    st.success(f"✓ {stage}")
        
        st.markdown("---")
        
        st.markdown("---")
        st.markdown("**Project Info:**")
        if "project_id" in st.session_state:
            st.code(st.session_state["project_id"])
        
        if st.button("🔄 Reset & Select New Project", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Render current stage
    render_current_stage(current_stage)


def render_current_stage(current_stage):
    """Render the current pipeline stage"""
    
    if current_stage == "concept":
        render_concept_stage()
    elif current_stage == "script":
        render_script_stage()
    elif current_stage == "characters_locations":
        render_characters_locations_stage()
    elif current_stage == "outfits":
        render_outfits_stage()
    elif current_stage == "scene_description":
        render_scene_stage()
    elif current_stage == "video":
        render_video_stage()


def render_concept_stage():
    """Stage 0: Brand Info & Ad Concept"""
    
    # Brand Information
    if "brand_info" not in st.session_state:
        st.header("📝 Brand Information")
        
        # Check if brand info already exists and load it
        project_path = st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
        brand_info_file = os.path.join(project_path, "scripts", "brand_info.json")
        
        if os.path.exists(brand_info_file):
            st.success("✅ Brand information already exists!")
            
            with open(brand_info_file, 'r') as f:
                st.session_state["brand_info"] = json.load(f)
            
            # Show current brand info
            with st.expander("📋 View Current Brand Information", expanded=False):
                st.json(st.session_state["brand_info"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit Brand Information", use_container_width=True):
                    os.remove(brand_info_file)
                    if "brand_info" in st.session_state:
                        del st.session_state["brand_info"]
                    st.rerun()
            
            with col2:
                if st.button("➡️ Continue to Ad Concepts", type="primary", use_container_width=True):
                    st.rerun()
        
        else:
            # Collect brand info
            brand_info = collect_brand_info()
            
            if brand_info:
                # Save brand info to project
                os.makedirs(os.path.dirname(brand_info_file), exist_ok=True)
                
                with open(brand_info_file, 'w') as f:
                    json.dump(brand_info, f, indent=2)
                
                st.session_state["brand_info"] = brand_info
                st.rerun()
    
    # Ad Concept
    elif "selected_concept" not in st.session_state or not st.session_state.get("ad_concept_selected", False):
        st.header("🎨 Ad Concept Generation")
        
        # Check if concept already selected
        project_path = st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
        concept_file = os.path.join(project_path, "scripts", "selected_concept.json")
        concepts_file = os.path.join(project_path, "ad_concepts.json")
        
        # Load saved generated concepts if they exist
        if os.path.exists(concepts_file):
            if "generated_concepts" not in st.session_state or len(st.session_state.get("generated_concepts", [])) == 0:
                with open(concepts_file, 'r') as f:
                    concepts_data = json.load(f)
                    st.session_state["generated_concepts"] = concepts_data.get("ad_concepts", [])
                    st.session_state["concepts_generated"] = True
                    st.session_state["ad_concept_selected"] = False
        
        if os.path.exists(concept_file):
            st.success("✅ Ad concept already selected!")
            
            with open(concept_file, 'r') as f:
                st.session_state["selected_concept"] = json.load(f)
            
            # Show current concept
            with st.expander("📋 View Selected Concept", expanded=False):
                concept = st.session_state["selected_concept"]
                st.markdown(f"**Title:** {concept.get('title', 'N/A')}")
                st.markdown(f"**Tagline:** {concept.get('tagline', 'N/A')}")
                st.markdown(f"**Tone:** {concept.get('tone', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Select Different Concept", use_container_width=True):
                    os.remove(concept_file)
                    if "selected_concept" in st.session_state:
                        del st.session_state["selected_concept"]
                    if "ad_concept_selected" in st.session_state:
                        del st.session_state["ad_concept_selected"]
                    # Keep concepts_generated=True so user can select from saved concepts
                    st.rerun()
            
            with col2:
                if st.button("➡️ Continue to Pipeline", type="primary", use_container_width=True):
                    st.rerun()
        
        else:
            # Generate and select concept
            brand_info = st.session_state["brand_info"]
            selected_concept = generate_and_select_ad_concepts(brand_info, duration=st.session_state.get("duration", 30))
            
            # The selected concept is already saved in ad_concept_selector.py
            # We just need to check if we can proceed to next stage
            if selected_concept and st.session_state.get("ad_concept_selected", False):
                # File is already saved, just rerun to update UI
                st.rerun()
    
    # Ready to continue
    elif "selected_concept" in st.session_state and st.session_state.get("ad_concept_selected", False):
        st.success("✅ All prerequisites complete!")
        
        st.markdown("### Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Project:**\n`{st.session_state['project_id']}`")
        with col2:
            st.info(f"**Brand:**\n{st.session_state['brand_info']['brand_name']}")
        with col3:
            st.info(f"**Concept:**\n{st.session_state['selected_concept']['title']}")
        
        st.markdown("---")
        st.markdown("### Next Steps")
        st.info("👈 Use the sidebar navigation to move to pipeline stages. Start with **Script Generation**.")
        
        if st.button("➡️ Go to Script Generation", type="primary", use_container_width=True):
            st.session_state["current_stage"] = "script"
            st.rerun()


def render_script_stage():
    """Stage 1: Script Generation"""
    
    if "brand_info" not in st.session_state or "selected_concept" not in st.session_state:
        st.error("❌ Please complete brand info and ad concept first!")
        st.button("⬅️ Back", on_click=lambda: setattr(st.session_state, "current_stage", "concept"))
        return
    
    display_script_generation_ui(
        st.session_state["brand_info"],
        st.session_state["selected_concept"],
        st.session_state["project_id"]
    )


def render_characters_locations_stage():
    """Stage 2: Characters & Locations"""
    
    # Check if script exists
    script_file = os.path.join(st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}"), 
                               "scripts", f"{st.session_state['project_id']}_shot_script.json")
    
    if not os.path.exists(script_file):
        st.error("❌ Please generate the shot script first!")
        if st.button("⬅️ Back to Script Generation"):
            st.session_state["current_stage"] = "script"
            st.rerun()
        return
    
    display_characters_locations_ui(
        st.session_state["project_id"],
        st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
    )


def render_outfits_stage():
    """Stage 3: Outfits & Character-Outfit Mapping"""
    
    # Check prerequisites
    char_file = os.path.join(st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}"), 
                            "scripts", f"{st.session_state['project_id']}_characters.json")
    
    if not os.path.exists(char_file):
        st.error("❌ Please generate characters and locations first!")
        if st.button("⬅️ Back to Characters & Locations"):
            st.session_state["current_stage"] = "characters_locations"
            st.rerun()
        return
    
    display_outfits_ui(
        st.session_state["project_id"],
        st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
    )


def render_scene_stage():
    """Stage 4: Scene Description & Image Generation"""
    
    # Check prerequisites
    char_outfit_file = os.path.join(st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}"), 
                                   "scripts", f"{st.session_state['project_id']}_character_outfits.json")
    
    if not os.path.exists(char_outfit_file):
        st.error("❌ Please generate character-outfit combinations first!")
        if st.button("⬅️ Back to Outfits"):
            st.session_state["current_stage"] = "outfits"
            st.rerun()
        return
    
    display_scene_generation_ui(
        st.session_state["project_id"],
        st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
    )


def render_video_stage():
    """Stage 5: Video Description & Generation"""
    
    # Check prerequisites
    scene_report_file = os.path.join(st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}"), 
                                     "scripts", f"{st.session_state['project_id']}_scene_generation_report.json")
    
    if not os.path.exists(scene_report_file):
        st.error("❌ Please generate scene images first!")
        if st.button("⬅️ Back to Scene Generation"):
            st.session_state["current_stage"] = "scene"
            st.rerun()
        return
    
    display_video_generation_ui(
        st.session_state["project_id"],
        st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
    )


if __name__ == "__main__":
    main() 