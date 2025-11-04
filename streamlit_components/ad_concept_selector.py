"""
Ad Concept Selector Component
"""

import streamlit as st
import os
import json
from services.ads_concept_generation.ads_concept_generator import AdConceptGenerator


def display_ad_concept(concept, index):
    """Display a single ad concept in an expandable card"""
    
    with st.expander(f"💡 Concept {index}: {concept.get('title', 'Untitled')}", expanded=False):
        st.markdown(f"## {concept.get('title', 'No Title')}")
        st.markdown(f"**Summary:** {concept.get('one_line_summary', 'N/A')}")
        
        st.markdown("---")
        st.markdown("**Story:**")
        st.markdown(f"{concept.get('story', 'N/A')}")
        
        visual_flow = concept.get('visual_flow', {})
        if visual_flow:
            st.markdown("**Visual Flow:**")
            if isinstance(visual_flow, dict):
                for key, value in visual_flow.items():
                    st.markdown(f"- **{key}:** {value}")
        
        st.markdown(f"**Tagline:** \"{concept.get('tagline', 'N/A')}\"")
        st.markdown(f"**Key Message:** {concept.get('key_message', 'N/A')}")
        
        features = concept.get('key_features', [])
        if features:
            st.markdown("**Key Features:**")
            for feature in features:
                st.markdown(f"- {feature}")
        
        st.markdown(f"**Tone:** {concept.get('tone', 'N/A')}")
        
        voice_over = concept.get('voice_over')
        if voice_over:
            st.markdown(f"**Voice Over:** _{voice_over}_")


def generate_and_select_ad_concepts(brand_info, duration=30):
    """Generate ad concepts and allow user to select one"""
    

    
    col1, col2 = st.columns(2)
    
    with col1:
        num_concepts = st.slider(
            "Number of Concepts",
            min_value=3,
            max_value=6,
            value=5,
            help="How many concept variations would you like?"
        )
    
    with col2:
        duration = st.selectbox(
            "Ad Duration",
            options=["15", "30", "45", "60"],
            index=1,
            help="Duration of the final ad in seconds"
        )
    
    st.markdown("---")
    
    if st.button("🚀 Generate Ad Concepts", type="primary", use_container_width=True):
        with st.spinner("🎨 Generating creative ad concepts... This may take a minute."):
            try:
                generator = AdConceptGenerator()
                concepts = generator.generate_ad_concepts(
                    brand_info=brand_info,
                    num_concepts=num_concepts,
                    duration=int(duration)
                )
                
                concepts_dict = [concept.model_dump() for concept in concepts]
                
                st.session_state["generated_concepts"] = concepts_dict
                st.session_state["concepts_generated"] = True
                st.session_state["ad_concept_selected"] = False
                
                # Save generated concepts to project
                project_path = st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
                concepts_file = os.path.join(project_path, "ad_concepts.json")
                os.makedirs(project_path, exist_ok=True)
                
                with open(concepts_file, 'w') as f:
                    json.dump({"ad_concepts": concepts_dict, "total_concepts": len(concepts)}, f, indent=2)
                
                st.success(f"✅ Generated {len(concepts)} ad concepts!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating concepts: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                st.session_state["concepts_generated"] = False
                return None
    
    # Check if concepts were generated and not yet selected
    concepts_generated = st.session_state.get("concepts_generated", False)
    generated_concepts = st.session_state.get("generated_concepts", [])
    
    if concepts_generated and len(generated_concepts) > 0 and not st.session_state.get("ad_concept_selected", False):
        st.markdown("---")
        
        concepts = generated_concepts
        
        st.success(f"✅ {len(concepts)} concept(s) generated! Review and select one:")
        
        st.markdown("---")
        
        # Display each concept
        for i, concept in enumerate(concepts, 1):
            display_ad_concept(concept, i)
        
        st.markdown("---")
        st.subheader("✅ Select Your Concept")
        
        concept_titles = [f"{i+1}. {c.get('title', 'Untitled')}" for i, c in enumerate(concepts)]
        
        selected_index = st.selectbox(
            "Choose a concept to proceed with:",
            options=range(len(concepts)),
            format_func=lambda x: concept_titles[x],
            key="concept_selector"
        )
        
        selected_concept = concepts[selected_index]
        
        st.markdown("### 📌 Selected Concept Preview")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Title", selected_concept.get('title', 'N/A'))
            st.metric("Tagline", selected_concept.get('tagline', 'N/A'))
        with col2:
            st.metric("Tone", selected_concept.get('tone', 'N/A'))
            st.metric("Duration", f"{duration}s")
        
        st.markdown("**Story:**")
        st.info(selected_concept.get('story', 'N/A'))
        
        if st.button("✓ Confirm Selection & Continue", type="primary", use_container_width=True):
            st.session_state["selected_concept"] = selected_concept
            st.session_state["selected_concept_index"] = selected_index
            st.session_state["ad_duration"] = duration
            st.session_state["ad_concept_selected"] = True
            
            # Save selected concept to project
            project_path = st.session_state.get("project_path", f"projects_data/{st.session_state['project_id']}")
            concept_file = os.path.join(project_path, "scripts", "selected_concept.json")
            os.makedirs(os.path.dirname(concept_file), exist_ok=True)
            
            with open(concept_file, 'w') as f:
                json.dump(selected_concept, f, indent=2)
            
            st.success("✅ Concept selected and saved! You can now proceed to the next step.")
            st.rerun()
            return selected_concept
        
        return selected_concept
    
    return None 