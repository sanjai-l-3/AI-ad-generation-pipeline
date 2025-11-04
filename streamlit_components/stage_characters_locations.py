"""
Stage 2: Characters & Locations Generation Component
Modern UI with dropdowns, image views, and regeneration capabilities
"""

import streamlit as st
import os
import json
from PIL import Image
from services.character_generation.character_generator import CharacterGenerator, FullCharacter
from services.location_generation.location_generator import LocationGenerator, FullLocation
from services.script_generation.script_generator import ShotScript


def display_characters_locations_ui(project_id, project_path):
    """Display characters and locations generation stage with modern UI"""
    
    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">👥📍 Characters & Locations</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Generate and manage character and location assets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load script to get characters and locations info
    script_file = os.path.join(project_path, "scripts", f"{project_id}_shot_script.json")
    
    if not os.path.exists(script_file):
        st.error("❌ Please generate the shot script first!")
        return
    
    with open(script_file, 'r') as f:
        script_data = json.load(f)
        shot_script = ShotScript(**script_data)
    
    # Create tabs for Characters and Locations
    tab1, tab2 = st.tabs(["👥 Characters Generation", "📍 Locations Generation"])
    
    with tab1:
        display_characters_section(shot_script.characters_info, project_path)
    
    with tab2:
        display_locations_section(shot_script.location_info, project_path)


def display_characters_section(characters_info, project_path):
    """Display characters generation section"""
    
    # Check if characters already generated
    char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    
    if os.path.exists(char_file):
        st.success("✅ Characters have been generated!")
        
        with open(char_file, 'r') as f:
            char_data = json.load(f)
            characters = char_data.get("characters", [])
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Characters", len(characters))
        with col2:
            st.metric("Images Generated", len([c for c in characters if c.get("image_path")]))
        with col3:
            if st.button("🔄 Regenerate All Characters", use_container_width=True):
                regenerate_all_characters(characters_info, project_path)
                st.rerun()
        
        st.markdown("---")
        
        # Display each character
        st.subheader("📋 Character Gallery")
        
        for i, char in enumerate(characters, 1):
            with st.expander(
                f"👤 {char.get('name', 'Unknown').title()} | Age: {char.get('age', 'N/A')} | Role: {char.get('role', 'N/A')}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    if char.get('image_path') and os.path.exists(char['image_path']):
                        st.image(char['image_path'], caption=f"{char.get('name', 'Character')}", use_container_width=True)
                        
                        col_regen, col_edit, col_view = st.columns(3)
                        with col_regen:
                            if st.button(f"🔄 Regenerate", key=f"regen_char_{i}"):
                                with st.spinner("Regenerating character with same prompt..."):
                                    regenerate_single_character(char, char, project_path)
                                st.rerun()
                        with col_edit:
                            if st.button(f"📝 Edit Prompt", key=f"edit_char_{i}"):
                                st.session_state[f"editing_char_{i}"] = True
                        with col_view:
                            if st.button(f"👁️ View Full", key=f"view_char_{i}"):
                                st.session_state[f"view_char_{i}"] = True
                        
                        # Show prompt editor if editing
                        if st.session_state.get(f"editing_char_{i}", False):
                            st.markdown("**Edit Prompt for Regeneration:**")
                            # Get the default prompt
                            generator = CharacterGenerator(output_dir=os.path.join(project_path, "character_images"))
                            default_prompt = generator.create_front_facing_prompt(char)
                            
                            custom_prompt = st.text_area(
                                "Custom Prompt:",
                                value=default_prompt,
                                height=150,
                                key=f"prompt_char_{i}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button(f"✨ Regenerate with Custom Prompt", key=f"save_char_{i}", type="primary"):
                                    regenerate_single_character_with_prompt(char, custom_prompt, project_path)
                                    st.session_state[f"editing_char_{i}"] = False
                                    st.rerun()
                            with col_cancel:
                                if st.button(f"❌ Cancel", key=f"cancel_char_{i}"):
                                    st.session_state[f"editing_char_{i}"] = False
                                    st.rerun()
                    else:
                        st.info("No image generated yet")
                        if st.button(f"🎨 Generate Image", key=f"gen_char_{i}"):
                            with st.spinner("Generating character image..."):
                                generate_single_character(char, project_path)
                            st.rerun()
                
                with col2:
                    st.markdown(f"**Name:** {char.get('name', 'N/A')}")
                    st.markdown(f"**Age:** {char.get('age', 'N/A')}")
                    st.markdown(f"**Gender:** {char.get('gender', 'N/A')}")
                    st.markdown(f"**Role:** {char.get('role', 'N/A')}")
                    
                    st.markdown("**Description:**")
                    st.text_area("", value=char.get('overall_description', 'N/A'), height=100, key=f"desc_char_{i}", disabled=True)
                    
                    if char.get('reference_description'):
                        st.markdown("**Reference Description:**")
                        st.info(char['reference_description'])
    
    else:
        # Generate characters
        st.info(f"Ready to generate {len(characters_info)} character(s)")
        
        st.markdown("### Character List")
        for i, char in enumerate(characters_info, 1):
            st.text(f"{i}. {char.name.title()} - {char.role}")
        
        st.markdown("---")
        
        if st.button("🚀 Generate All Characters", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating character images... This may take a few minutes."):
                generate_all_characters(characters_info, project_path)
                st.rerun()


def display_locations_section(locations_info, project_path):
    """Display locations generation section"""
    
    # Check if locations already generated
    loc_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
    
    if os.path.exists(loc_file):
        st.success("✅ Locations have been generated!")
        
        with open(loc_file, 'r') as f:
            loc_data = json.load(f)
            locations = loc_data.get("locations", [])
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Locations", len(locations))
        with col2:
            st.metric("Images Generated", len([l for l in locations if l.get("image_path")]))
        with col3:
            if st.button("🔄 Regenerate All Locations", use_container_width=True):
                with st.spinner("Regenerating all locations..."):
                    regenerate_all_locations(locations_info, project_path)
                st.rerun()
        
        st.markdown("---")
        
        # Display in a grid
        cols = st.columns(2)
        for i, loc in enumerate(locations):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"### 📍 {loc.get('name', 'Location').title()}")
                    
                    if loc.get('image_path') and os.path.exists(loc['image_path']):
                        st.image(loc['image_path'], use_container_width=True)
                        
                        col_regen, col_edit, col_view = st.columns(3)
                        with col_regen:
                            if st.button(f"🔄 Regenerate", key=f"regen_loc_{i}"):
                                with st.spinner("Regenerating location with same prompt..."):
                                    regenerate_single_location(loc, project_path)
                                st.rerun()
                        with col_edit:
                            if st.button(f"📝 Edit Prompt", key=f"edit_loc_{i}"):
                                st.session_state[f"editing_loc_{i}"] = True
                        with col_view:
                            pass
                        
                        # Show prompt editor if editing
                        if st.session_state.get(f"editing_loc_{i}", False):
                            st.markdown("**Edit Prompt for Regeneration:**")
                            # Get the default prompt
                            generator = LocationGenerator(output_dir=os.path.join(project_path, "location_images"))
                            default_prompt = generator.create_location_prompt(loc)
                            
                            custom_prompt = st.text_area(
                                "Custom Prompt:",
                                value=default_prompt,
                                height=150,
                                key=f"prompt_loc_{i}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button(f"✨ Regenerate with Custom Prompt", key=f"save_loc_{i}", type="primary"):
                                    regenerate_single_location_with_prompt(loc, custom_prompt, project_path)
                                    st.session_state[f"editing_loc_{i}"] = False
                                    st.rerun()
                            with col_cancel:
                                if st.button(f"❌ Cancel", key=f"cancel_loc_{i}"):
                                    st.session_state[f"editing_loc_{i}"] = False
                                    st.rerun()
                    else:
                        st.info("No image generated yet")
                        if st.button(f"🎨 Generate Image", key=f"gen_loc_{i}"):
                            with st.spinner("Generating location image..."):
                                generate_single_location(loc, project_path)
                            st.rerun()
                    
                    with st.expander("View Details"):
                        st.text_area("Description", value=loc.get('overall_description', 'N/A'), height=100, key=f"desc_loc_{i}", disabled=True)
    
    else:
        # Generate locations
        st.info(f"Ready to generate {len(locations_info)} location(s)")
        
        st.markdown("### Location List")
        for i, loc in enumerate(locations_info, 1):
            st.text(f"{i}. {loc.name.title()}")
        
        st.markdown("---")
        
        if st.button("🚀 Generate All Locations", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating location images... This may take a few minutes."):
                generate_all_locations(locations_info, project_path)
                st.rerun()


def generate_all_characters(characters_info, project_path):
    """Generate all character images"""
    char_images_dir = os.path.join(project_path, "character_images")
    
    # Convert to FullCharacter format
    full_characters = [FullCharacter(
        name=char.name,
        age=char.age,
        role=char.role,
        gender=char.gender,
        overall_description=char.overall_description
    ) for char in characters_info]
    
    generator = CharacterGenerator(output_dir=char_images_dir)
    characters_with_images = generator.generate_images_for_all_characters(full_characters)
    
    # Save to file
    char_json_path = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    generator.save_characters_with_images(characters_with_images, char_json_path)


def regenerate_all_characters(characters_info, project_path):
    """Regenerate all characters"""
    generate_all_characters(characters_info, project_path)


def regenerate_single_character(char, original_char, project_path):
    """Regenerate a single character"""
    generator = CharacterGenerator(output_dir=os.path.join(project_path, "character_images"))
    
    # Use the SAME prompt path: call single-character generation without custom prompt
    image_path = generator.generate_single_character_image(original_char)
    
    if not image_path:
        return
    
    # Update the character file with new image_path
    char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    with open(char_file, 'r') as f:
        char_data = json.load(f)
    
    for c in char_data['characters']:
        if c['name'] == char['name']:
            c['image_path'] = image_path
    
    with open(char_file, 'w') as f:
        json.dump(char_data, f, indent=2)


def regenerate_single_character_with_prompt(char, custom_prompt, project_path):
    """Regenerate a single character with custom prompt"""
    generator = CharacterGenerator(output_dir=os.path.join(project_path, "character_images"))
    
    # Use the new single character image generation method
    image_path = generator.generate_single_character_image(char, custom_prompt=custom_prompt)
    
    if image_path:
        # Update character with new image
        char['image_path'] = image_path
        
        # Update the character file
        char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
        with open(char_file, 'r') as f:
            char_data = json.load(f)
        
        for c in char_data['characters']:
            if c['name'] == char['name']:
                c['image_path'] = image_path
                break
        
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)


def generate_single_character(char, project_path):
    """Generate a single character"""
    generator = CharacterGenerator(output_dir=os.path.join(project_path, "character_images"))
    
    # Generate using default prompt
    image_path = generator.generate_single_character_image(char)
    if not image_path:
        return
    
    # Update or create the character file
    char_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_characters.json")
    
    if os.path.exists(char_file):
        with open(char_file, 'r') as f:
            char_data = json.load(f)
        
        found = False
        for c in char_data['characters']:
            if c['name'] == char['name']:
                c['image_path'] = image_path
                found = True
                break
        
        if not found:
            # Append minimal character info with image
            char_data['characters'].append({
                'name': char.get('name'),
                'age': char.get('age'),
                'role': char.get('role'),
                'gender': char.get('gender'),
                'overall_description': char.get('overall_description'),
                'image_path': image_path
            })
    else:
        char_data = {"characters": [{
            'name': char.get('name'),
            'age': char.get('age'),
            'role': char.get('role'),
            'gender': char.get('gender'),
            'overall_description': char.get('overall_description'),
            'image_path': image_path
        }]}
    
    with open(char_file, 'w') as f:
        json.dump(char_data, f, indent=2)


def generate_all_locations(locations_info, project_path):
    """Generate all location images"""
    loc_images_dir = os.path.join(project_path, "location_images")
    
    # Convert to FullLocation format
    full_locations = [FullLocation(
        name=loc.name,
        overall_description=loc.overall_description
    ) for loc in locations_info]
    
    generator = LocationGenerator(output_dir=loc_images_dir)
    locations_with_images = generator.generate_images_for_all_locations(full_locations)
    
    # Save to file
    loc_json_path = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
    generator.save_locations_with_images(locations_with_images, loc_json_path)


def regenerate_all_locations(locations_info, project_path):
    """Regenerate all locations"""
    generate_all_locations(locations_info, project_path)


def regenerate_single_location_with_prompt(loc, custom_prompt, project_path):
    """Regenerate a single location with custom prompt"""
    generator = LocationGenerator(output_dir=os.path.join(project_path, "location_images"))
    
    # Use the new single location image generation method
    image_path = generator.generate_single_location_image(loc, custom_prompt=custom_prompt)
    
    if image_path:
        # Update location with new image
        loc['image_path'] = image_path
        
        # Update the location file
        loc_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
        with open(loc_file, 'r') as f:
            loc_data = json.load(f)
        
        for l in loc_data['locations']:
            if l['name'] == loc['name']:
                l['image_path'] = image_path
                break
        
        with open(loc_file, 'w') as f:
            json.dump(loc_data, f, indent=2)


def regenerate_single_location(loc, project_path):
    """Regenerate a single location"""
    generator = LocationGenerator(output_dir=os.path.join(project_path, "location_images"))
    
    # Use the SAME prompt path: call single-location generation without custom prompt
    image_path = generator.generate_single_location_image(loc)
    if not image_path:
        return
    
    # Update the location file with new image path
    loc_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
    with open(loc_file, 'r') as f:
        loc_data = json.load(f)
    
    for l in loc_data['locations']:
        if l['name'] == loc['name']:
            l['image_path'] = image_path
    
    with open(loc_file, 'w') as f:
        json.dump(loc_data, f, indent=2)


def generate_single_location(loc, project_path):
    """Generate a single location"""
    generator = LocationGenerator(output_dir=os.path.join(project_path, "location_images"))
    
    # Generate using default prompt
    image_path = generator.generate_single_location_image(loc)
    if not image_path:
        return
    
    # Update or create the location file
    loc_file = os.path.join(project_path, "scripts", f"{os.path.basename(project_path)}_locations.json")
    
    if os.path.exists(loc_file):
        with open(loc_file, 'r') as f:
            loc_data = json.load(f)
        
        found = False
        for l in loc_data['locations']:
            if l['name'] == loc['name']:
                l['image_path'] = image_path
                found = True
                break
        
        if not found:
            loc_data['locations'].append({
                'name': loc.get('name'),
                'overall_description': loc.get('overall_description'),
                'image_path': image_path
            })
    else:
        loc_data = {"locations": [{
            'name': loc.get('name'),
            'overall_description': loc.get('overall_description'),
            'image_path': image_path
        }]}
    
    with open(loc_file, 'w') as f:
        json.dump(loc_data, f, indent=2) 