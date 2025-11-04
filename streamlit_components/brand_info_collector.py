"""
Brand Information Collector Component
"""

import streamlit as st
from PIL import Image
import os


def collect_brand_info():
    """Collect brand information through UI"""

    st.markdown("Please provide details about your brand and product below.")
    
    brand_info = {}
    
    # Basic Brand Information
    st.subheader("🏢 Basic Brand Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_info["brand_name"] = st.text_input(
            "Brand Name *", 
            value="Deconstruct",
            help="Enter your brand name"
        )
        
    with col2:
        brand_info["product_name"] = st.text_input(
            "Product Name *",
            value="Gel Sunscreen SPF 55",
            help="Enter the name of your product"
        )
    
    brand_info["product_description"] = st.text_area(
        "Product Description *",
        value="Lightweight, matte finish sunscreen with high SPF protection",
        help="Provide a detailed description of your product",
        height=100
    )
    
    # Key Features
    st.subheader("✨ Key Features")
    st.markdown("List the key features of your product.")
    
    if "key_features" not in st.session_state:
        st.session_state.key_features = [
            "SPF 55 protection",
            "Matte finish - no white cast",
            "Sweat-resistant",
            "Non-greasy formula"
        ]
    
    for i, feature in enumerate(st.session_state.key_features):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.session_state.key_features[i] = st.text_input(
                f"Feature {i+1}",
                value=feature,
                key=f"feature_{i}",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.key_features.pop(i)
                st.rerun()
    
    if st.button("➕ Add Another Feature"):
        st.session_state.key_features.append("")
        st.rerun()
    
    brand_info["key_features"] = [f for f in st.session_state.key_features if f.strip()]
    
    # Target Audience
    st.subheader("🎯 Target Audience")
    brand_info["target_audience"] = st.text_input(
        "Target Audience *",
        value="Active individuals, sports enthusiasts, ages 25-45",
        help="Describe your target audience"
    )
    
    # Brand Values
    st.subheader("💎 Brand Values")
    brand_info["brand_values"] = st.multiselect(
        "Select Brand Values",
        options=[
            "Performance", "Quality", "Trust", "Innovation",
            "Authenticity", "Sustainability", "Affordability", "Luxury",
            "Health", "Beauty", "Youth", "Experience"
        ],
        default=["Performance", "Quality", "Trust", "Innovation"],
        help="Select values that represent your brand"
    )
    
    # Tone Preferences
    st.subheader("🎭 Tone & Style")
    col1, col2 = st.columns(2)
    
    with col1:
        brand_info["tone_preferences"] = st.selectbox(
            "Tone *",
            options=[
                "Confident, aspirational, authentic",
                "Humorous and light-hearted",
                "Emotional and inspiring",
                "Professional and trustworthy",
                "Energetic and dynamic",
                "Calm and serene"
            ],
            index=0
        )
    
    with col2:
        brand_info["reference_style"] = st.text_input(
            "Reference Style",
            value="Documentary-style, authentic moments",
            help="Describe the visual style you prefer"
        )
    
    # Campaign Objective
    st.subheader("🎯 Campaign Objective")
    brand_info["campaign_objective"] = st.text_area(
        "Campaign Objective *",
        value="Increase brand awareness and position as premium sunscreen choice",
        help="What are you trying to achieve with this campaign?",
        height=80
    )
    
    # Celebrity Endorser (Optional)
    st.subheader("⭐ Celebrity Endorser (Optional)")
    brand_info["celebrity_endorser"] = st.text_input(
        "Celebrity Name",
        value="",
        help="If applicable, mention the celebrity endorser"
    )
    
    # Product Image Upload
    st.subheader("🖼️ Product Image")
    
    product_image = st.file_uploader(
        "Upload Product Image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image of your product"
    )
    
    # Get project path if exists
    project_path = st.session_state.get("project_path")
    
    if product_image is not None:
        image = Image.open(product_image)
        st.image(image, caption="Product Image", width=300)
        
        # Save to project directory if project exists
        if project_path:
            product_images_dir = os.path.join(project_path, "product_images")
            os.makedirs(product_images_dir, exist_ok=True)
            image_path = os.path.join(product_images_dir, product_image.name)
            image.save(image_path)
            brand_info["product_image_path"] = image_path
        else:
            # Fallback to temp
            if not os.path.exists("temp_uploads"):
                os.makedirs("temp_uploads")
            image_path = os.path.join("temp_uploads", product_image.name)
            image.save(image_path)
            brand_info["product_image_path"] = image_path
    
    st.markdown("---")
    
    # Validation
    required_fields = [
        brand_info.get("brand_name"),
        brand_info.get("product_name"),
        brand_info.get("product_description"),
        brand_info.get("key_features"),
        brand_info.get("target_audience"),
        brand_info.get("campaign_objective")
    ]
    
    all_fields_filled = all(required_fields)
    
    if st.button("✅ Save Brand Information", type="primary", use_container_width=True, disabled=not all_fields_filled):
        if all_fields_filled:
            st.session_state["brand_info"] = brand_info
            st.success("✅ Brand information saved successfully!")
            st.balloons()
            return brand_info
        else:
            st.error("Please fill in all required fields (marked with *)")
            return None
    
    return None 