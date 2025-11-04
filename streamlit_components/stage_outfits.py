"""
Stage 3: Outfits & Character-Outfit Mapping Component
Modern UI with regeneration capabilities
"""

import streamlit as st
import os
import json
from PIL import Image
from services.outfit_generation.outfit_generator import OutfitGenerator, FullOutfit
from services.character_outfit_generation.character_outfit_generator import CharacterOutfitGenerator, CharacterOutfitImage
from services.script_generation.script_generator import ShotScript


def display_outfits_ui(project_id, project_path):
    """Display outfits and character-outfit mapping generation stage"""
    
    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">👕 Outfits & Character-Outfit Mapping</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Generate outfits and character-outfit combinations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load script
    script_file = os.path.join(project_path, "scripts", f"{project_id}_shot_script.json")
    
    if not os.path.exists(script_file):
        st.error("❌ Please generate the shot script first!")
        return
    
    with open(script_file, 'r') as f:
        script_data = json.load(f)
        shot_script = ShotScript(**script_data)
    
    # Create tabs
    tab1, tab2 = st.tabs(["👕 Outfit Generation", "🤝 Character-Outfit Mapping"])
    
    with tab1:
        display_outfits_section(shot_script.character_outfit_info, project_path)
    
    with tab2:
        display_character_outfit_mapping(project_path)


def display_outfits_section(outfits_info, project_path):
    """Display outfit generation section"""
    
    outfit_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    
    if os.path.exists(outfit_file):
        st.success("✅ Outfits have been generated!")
        
        with open(outfit_file, 'r') as f:
            outfit_data = json.load(f)
            outfits = outfit_data.get("outfits", [])
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Outfits", len(outfits))
        with col2:
            st.metric("Images Generated", len([o for o in outfits if o.get("image_path")]))
        with col3:
            if st.button("🔄 Regenerate All Outfits", use_container_width=True):
                regenerate_all_outfits(outfits_info, project_path)
                st.rerun()
        
        st.markdown("---")
        
        # Display outfits in a grid
        cols = st.columns(2)
        for i, outfit in enumerate(outfits):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"### 👕 {outfit.get('outfit', 'Outfit').title()}")
                    
                    if outfit.get('image_path') and os.path.exists(outfit['image_path']):
                        st.image(outfit['image_path'], use_container_width=True)
                        
                        col_regen, col_desc = st.columns(2)
                        with col_regen:
                            if st.button(f"🔄 Regenerate", key=f"regen_outfit_{i}"):
                                regenerate_single_outfit(outfit, project_path)
                                st.rerun()
                        with col_desc:
                            with st.expander("Description"):
                                st.text_area("", value=outfit.get('outfit_description', 'N/A'), 
                                            height=100, key=f"desc_outfit_{i}", disabled=True)
                    else:
                        st.info("No image generated yet")
                        if st.button(f"🎨 Generate Image", key=f"gen_outfit_{i}"):
                            generate_single_outfit(outfit, project_path)
                            st.rerun()
    
    else:
        st.info(f"Ready to generate {len(outfits_info)} outfit(s)")
        
        st.markdown("### Outfit List")
        for i, outfit in enumerate(outfits_info, 1):
            st.text(f"{i}. {outfit.outfit.title()}")
        
        st.markdown("---")
        
        if st.button("🚀 Generate All Outfits", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating outfit images... This may take a few minutes."):
                generate_all_outfits(outfits_info, project_path)
                st.rerun()


def display_character_outfit_mapping(project_path):
    """Display character-outfit mapping section"""
    
    mapping_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_character_outfits.json")
    
    # Load characters and outfits
    char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    outfit_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    
    if not os.path.exists(char_file) or not os.path.exists(outfit_file):
        st.error("❌ Please generate characters and outfits first!")
        return
    
    with open(char_file, 'r') as f:
        char_data = json.load(f)
        characters = char_data.get("characters", [])
    
    with open(outfit_file, 'r') as f:
        outfit_data = json.load(f)
        outfits = outfit_data.get("outfits", [])
    
    # Check if mapping file exists
    mapping_file_exists = os.path.exists(mapping_file)
    
    if mapping_file_exists:
        with open(mapping_file, 'r') as f:
            mapping_data = json.load(f)
            combinations = mapping_data.get("character_outfits", [])
            
        if len(combinations) > 0:
            st.success(f"✅ Character-outfit combinations have been generated! ({len(combinations)} combinations)")
            
            st.markdown("---")
            
            # Display combinations
            for i, combo in enumerate(combinations, 1):
                char_name = combo.get('character_name', 'Unknown')
                outfit_name = combo.get('outfit_name', 'Unknown')
                
                with st.expander(f"🤝 {char_name.title()} wearing {outfit_name.title()}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if combo.get('image_path') and os.path.exists(combo['image_path']):
                            st.image(combo['image_path'], caption=f"{char_name} - {outfit_name}", use_container_width=True)
                            
                            if st.button(f"🔄 Regenerate", key=f"regen_combo_{i}"):
                                regenerate_single_combination(combo, project_path, characters, outfits)
                                st.rerun()
                        else:
                            st.info("No image generated yet")
                    
                    with col2:
                        # Find character and outfit details
                        char = next((c for c in characters if c.get('name', '').lower() == char_name.lower()), None)
                        outfit = next((o for o in outfits if o.get('outfit', '').lower() == outfit_name.lower()), None)
                        
                        if char:
                            st.markdown(f"**Character:** {char_name.title()}")
                            st.markdown(f"**Age:** {char.get('age', 'N/A')}")
                            st.markdown(f"**Role:** {char.get('role', 'N/A')}")
                        
                        if outfit:
                            st.markdown(f"**Outfit:** {outfit_name.title()}")
                            st.markdown("**Description:**")
                            st.text_area("", value=outfit.get('outfit_description', 'N/A')[:200], 
                                        height=100, key=f"outfit_desc_{i}", disabled=True)
        
        else:
            # File exists but is empty - prompt to regenerate
            st.warning("⚠️ Character-outfit mapping file exists but is empty. Please regenerate.")
            if st.button("🔄 Regenerate Character-Outfit Combinations", type="primary", use_container_width=True):
                # Delete empty file
                os.remove(mapping_file)
                # Generate again
                with st.spinner("🎨 Generating character-outfit combinations... This may take several minutes."):
                    generate_all_combinations(project_path, characters, outfits)
                st.rerun()
    
    else:
        st.info("Ready to generate character-outfit combinations")
        st.markdown("### Available Characters & Outfits")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Characters:**")
            for char in characters:
                st.text(f"• {char.get('name', 'Unknown').title()}")
        
        with col2:
            st.markdown("**Outfits:**")
            for outfit in outfits:
                st.text(f"• {outfit.get('outfit', 'Unknown').title()}")
        
        st.markdown("---")
        
        if st.button("🚀 Generate All Combinations", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating character-outfit combinations... This may take several minutes."):
                generate_all_combinations(project_path, characters, outfits)
                st.rerun()


def generate_all_outfits(outfits_info, project_path):
    """Generate all outfit images"""
    outfit_images_dir = os.path.join(project_path, "outfit_images")
    
    full_outfits = [FullOutfit(
        outfit=outfit.outfit,
        outfit_description=outfit.outfit_description
    ) for outfit in outfits_info]
    
    generator = OutfitGenerator(output_dir=outfit_images_dir)
    outfits_with_images = generator.generate_images_for_all_outfits(full_outfits)
    
    # Save to file
    outfit_json_path = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    generator.save_outfits_with_images(outfits_with_images, outfit_json_path)


def regenerate_all_outfits(outfits_info, project_path):
    """Regenerate all outfits"""
    generate_all_outfits(outfits_info, project_path)


def regenerate_single_outfit(outfit, project_path):
    """Regenerate a single outfit"""
    generator = OutfitGenerator(output_dir=os.path.join(project_path, "outfit_images"))
    
    full_outfit = FullOutfit(
        outfit=outfit.get('outfit'),
        outfit_description=outfit.get('outfit_description')
    )
    
    result = generator.generate_image_for_outfit(full_outfit)
    
    # Update the outfit file
    outfit_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    with open(outfit_file, 'r') as f:
        outfit_data = json.load(f)
    
    for o in outfit_data['outfits']:
        if o['outfit'] == outfit['outfit']:
            o.update(result)
    
    with open(outfit_file, 'w') as f:
        json.dump(outfit_data, f, indent=2)


def generate_single_outfit(outfit, project_path):
    """Generate a single outfit"""
    generator = OutfitGenerator(output_dir=os.path.join(project_path, "outfit_images"))
    
    full_outfit = FullOutfit(
        outfit=outfit.get('outfit'),
        outfit_description=outfit.get('outfit_description')
    )
    
    result = generator.generate_image_for_outfit(full_outfit)
    
    # Update or create the outfit file
    outfit_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_outfits.json")
    
    if os.path.exists(outfit_file):
        with open(outfit_file, 'r') as f:
            outfit_data = json.load(f)
        
        found = False
        for o in outfit_data['outfits']:
            if o['outfit'] == outfit['outfit']:
                o.update(result)
                found = True
                break
        
        if not found:
            outfit_data['outfits'].append(result)
    else:
        outfit_data = {"outfits": [result]}
    
    with open(outfit_file, 'w') as f:
        json.dump(outfit_data, f, indent=2)


def generate_all_combinations(project_path, characters, outfits):
    """Generate all character-outfit combinations"""
    # Load script to get shots info
    script_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_shot_script.json")
    
    shots_info = []
    if os.path.exists(script_file):
        with open(script_file, 'r') as f:
            script_data = json.load(f)
            shots_info = script_data.get('shots', [])
    
    char_outfit_gen = CharacterOutfitGenerator(
        output_dir=os.path.join(project_path, "character_outfit_images")
    )
    
    # Generate combinations
    character_outfit_images = char_outfit_gen.generate_all_character_outfits(
        characters_info=characters,
        outfits_info=outfits,
        shots_info=shots_info
    )
    
    # Save mapping
    char_outfit_json = char_outfit_gen.save_character_outfit_mapping(
        character_outfit_images,
        f"{os.path.basename(project_path)}_character_outfits.json",
        os.path.join(project_path, "scripts")
    )


def regenerate_single_combination(combo, project_path, characters, outfits):
    """Regenerate a single character-outfit combination"""
    char_name = combo.get('character_name')
    outfit_name = combo.get('outfit_name')
    
    char = next((c for c in characters if c.get('name', '').lower() == char_name.lower()), None)
    outfit = next((o for o in outfits if o.get('outfit', '').lower() == outfit_name.lower()), None)
    
    if not char or not outfit:
        st.error("Character or outfit not found!")
        return
    
    char_image_path = char.get('image_path')
    if not char_image_path or not os.path.exists(char_image_path):
        st.error("Character image not found!")
        return
    
    generator = CharacterOutfitGenerator(
        output_dir=os.path.join(project_path, "character_outfit_images")
    )
    
    result = generator.generate_character_in_outfit(
        character_image_path=char_image_path,
        character_info=char,
        outfit_info=outfit
    )
    
    if result:
        # Update the mapping file
        mapping_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_character_outfits.json")
        with open(mapping_file, 'r') as f:
            mapping_data = json.load(f)
        
        for c in mapping_data['character_outfits']:
            if c['character_name'] == char_name and c['outfit_name'] == outfit_name:
                c.update(result.model_dump())
        
        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2) 