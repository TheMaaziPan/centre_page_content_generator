import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from io import BytesIO
from datetime import datetime
import anthropic  # Anthropic API client

# Set page config
st.set_page_config(
    page_title="Centre Page Content Generator",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'selected_property' not in st.session_state:
    st.session_state.selected_property = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'df' not in st.session_state:
    st.session_state.df = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# Function to generate property description using Anthropic API
def generate_property_description(property_data, api_key):
    """Generate property description using Anthropic API"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Construct prompt from property data
        prompt = f"""You are a professional content writer for a luxury office space provider.
        Write a premium office space description for executives and business leaders based on the following details:
        
        Property Name: {property_data.get('Property Name', 'N/A')}
        Address: {property_data.get('Address', 'N/A')}
        City: {property_data.get('City', 'N/A')}
        Zip Code: {property_data.get('Zip Code', 'N/A')}
        Neighborhood: {property_data.get('Neighborhood', 'N/A')}
        Property Type: {property_data.get('Property Type', 'N/A')}
        Size Range: {property_data.get('Size Range', 'N/A')}
        Building Description: {property_data.get('Building Description', 'N/A')}
        Key Features: {property_data.get('Key Features', 'N/A')}
        Nearby Businesses: {property_data.get('Nearby Businesses', 'N/A')}
        Transport Access: {property_data.get('Transport Access', 'N/A')}
        Technology Features: {property_data.get('Technology Features', 'N/A')}
        Meeting Rooms: {property_data.get('Meeting Rooms', 'N/A')}
        Common Areas: {property_data.get('Common Areas', 'N/A')}
        Business Services: {property_data.get('Business Services', 'N/A')}
        Security Features: {property_data.get('Security Features', 'N/A')}
        Wellness Amenities: {property_data.get('Wellness Amenities', 'N/A')}
        Office Configurations: {property_data.get('Office Configurations', 'N/A')}
        Lease Options: {property_data.get('Lease Options', 'N/A')}
        Contact Information: {property_data.get('Contact Information', 'N/A')}
        
        The content should:
        - Be between 500-750 words
        - Have an executive summary, location advantages, amenities section, workspace options, and call to action
        - Use professional, upscale language appropriate for C-suite executives and their assistants
        - Highlight the premium aspects and unique selling points of the space
        - Include specific details about the neighborhood and local amenities
        
        Format the content with markdown headings and bullet points where appropriate.
        """
        
        # Make API call to Anthropic's Claude
        message = client.messages.create(
            model="claude-3-sonnet-20240229",  # Use the appropriate model version
            max_tokens=1500,
            temperature=0.7,
            system="You are a professional content writer specializing in premium commercial real estate descriptions for executive audiences.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated content from the response
        return message.content
    
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        # Fallback to template-based generation if API fails
        return generate_template_description(property_data)

# Fallback template-based generation function
def generate_template_description(property_data):
    """Fallback function using templates when API is unavailable"""
    property_name = property_data.get('Property Name', 'Office Space')
    city = property_data.get('City', 'City')
    zip_code = property_data.get('Zip Code', '')
    neighborhood = property_data.get('Neighborhood', 'Business District')
    property_type = property_data.get('Property Type', 'Commercial Space')
    size_range = property_data.get('Size Range', 'Flexible square footage')
    building_desc = property_data.get('Building Description', 'Modern building')
    key_features = property_data.get('Key Features', 'Multiple amenities')
    
    content = f"""# {property_name} | Premium Workspace in {neighborhood}, {city}

## Executive Summary
Elevate your business operations at {property_name}, a prestigious {property_type} workspace strategically located in {neighborhood}. Offering {size_range} of premium office space, this {building_desc} provides the ideal environment for companies seeking exceptional workspace solutions in {city}'s thriving business district. With {key_features}, {property_name} delivers an unparalleled professional experience designed for business leaders who demand excellence.

[Template-based content - Please configure your Anthropic API key for AI-generated content]
"""
    return content

# Function to export data with generated content
def export_data(df, format_type):
    """Export dataframe with generated content"""
    if format_type == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format_type == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Property Descriptions', index=False)
        return output.getvalue()
    else:
        return None

# Sidebar - Configuration
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Office+Space", width=200)
    st.title("Content Generator")
    
    # API Key input
    api_key = st.text_input("Enter Anthropic API Key:", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
    
    # Model selection
    model_options = {
        "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
        "claude-3-opus-20240229": "Claude 3 Opus (Highest quality)",
        "claude-3-haiku-20240307": "Claude 3 Haiku (Fastest)"
    }
    selected_model = st.selectbox(
        "Select Claude Model:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    st.session_state.selected_model = selected_model
    
    st.divider()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Property Data", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.session_state.df = df
            st.success(f"Loaded {len(df)} properties")
            
            # Display data fields for verification
            if st.checkbox("Show data fields"):
                st.write("Detected columns:")
                st.write(", ".join(df.columns.tolist()))
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    st.divider()
    
    # Generation controls
    if st.session_state.df is not None:
        if st.button("Generate All Descriptions"):
            if not st.session_state.api_key:
                st.error("Please enter Anthropic API key first")
            else:
                st.session_state.is_generating = True
                st.session_state.progress = 0
                
                # Add content column if it doesn't exist
                if 'Generated Content' not in st.session_state.df:
                    st.session_state.df['Generated Content'] = np.nan
                    
                # Clear existing generated content
                st.session_state.generated_content = {}
        
        if st.session_state.generated_content:
            # Export options
            st.subheader("Export Data")
            export_format = st.radio("Select format:", ("CSV", "Excel"))
            
            if st.download_button(
                label=f"Download {export_format}",
                data=export_data(st.session_state.df, export_format.lower()),
                file_name=f"office_descriptions_{datetime.now().strftime('%Y%m%d_%H%M')}.{export_format.lower()}",
                mime="application/octet-stream"
            ):
                st.success(f"Downloaded {export_format} file!")

# Main content area
st.title("Centre Page Content Generator")

# API key validation
if not st.session_state.api_key and 'api_status' not in st.session_state:
    st.warning("⚠️ Please enter your Anthropic API key in the sidebar to use AI-generated content. Without an API key, the app will use basic templates.")
    st.session_state.api_status = "warned"

# Content generation in progress
if st.session_state.is_generating and st.session_state.df is not None:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_properties = len(st.session_state.df)
    
    for i, (idx, row) in enumerate(st.session_state.df.iterrows()):
        # Update progress
        progress = int((i / total_properties) * 100)
        progress_bar.progress(progress)
        property_name = row.get('Property Name', f'Property #{idx}')
        status_text.text(f"Generating description for {property_name}... ({i+1}/{total_properties})")
        
        # Generate content if not already generated
        if idx not in st.session_state.generated_content:
            property_data = row.to_dict()
            
            with st.spinner(f"Generating content for {property_name}..."):
                try:
                    content = generate_property_description(
                        property_data, 
                        st.session_state.api_key
                    )
                    st.session_state.generated_content[idx] = content
                    st.session_state.df.at[idx, 'Generated Content'] = content
                except Exception as e:
                    st.error(f"Error generating content for {property_name}: {str(e)}")
    
    progress_bar.progress(100)
    status_text.text(f"Generated descriptions for {total_properties} properties!")
    st.session_state.is_generating = False

# Display properties and generated content
if st.session_state.df is not None:
    st.subheader("Property Descriptions")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Properties")
        # Select property to display
        for idx, row in st.session_state.df.iterrows():
            property_name = row.get('Property Name', f'Property #{idx}')
            if st.button(property_name, key=f"prop_{idx}"):
                st.session_state.selected_property = idx
    
    with col2:
        st.subheader("Generated Content")
        if st.session_state.selected_property is not None:
            idx = st.session_state.selected_property
            
            # Display property details
            property_data = st.session_state.df.iloc[idx].to_dict()
            property_name = property_data.get('Property Name', 'N/A')
            city = property_data.get('City', 'N/A')
            zip_code = property_data.get('Zip Code', 'N/A')
            
            st.info(f"**Property:** {property_name}\n\n**Location:** {city}, {zip_code}")
            
            # Display or generate content for selected property
            if idx in st.session_state.generated_content:
                content = st.session_state.generated_content[idx]
                st.markdown(content)
                
                # Edit content
                if st.button("Regenerate", key=f"regen_{idx}"):
                    if not st.session_state.api_key:
                        st.error("Please enter Anthropic API key first")
                    else:
                        with st.spinner("Regenerating content..."):
                            new_content = generate_property_description(
                                property_data, 
                                st.session_state.api_key
                            )
                            st.session_state.generated_content[idx] = new_content
                            st.session_state.df.at[idx, 'Generated Content'] = new_content
                            st.experimental_rerun()
                
                edited_content = st.text_area("Edit Content", value=content, height=400)
                if edited_content != content:
                    if st.button("Save Edits", key=f"save_{idx}"):
                        st.session_state.generated_content[idx] = edited_content
                        st.session_state.df.at[idx, 'Generated Content'] = edited_content
                        st.success("Changes saved!")
                        
            else:
                if st.button("Generate Description", key=f"gen_{idx}"):
                    if not st.session_state.api_key:
                        st.error("Please enter Anthropic API key first")
                    else:
                        with st.spinner("Generating content..."):
                            content = generate_property_description(
                                property_data, 
                                st.session_state.api_key
                            )
                            st.session_state.generated_content[idx] = content
                            st.session_state.df.at[idx, 'Generated Content'] = content
                            st.experimental_rerun()
else:
    st.info("Please upload a CSV or Excel file containing property data.")
    
    # Sample data structure
    st.subheader("Expected Data Structure")
    sample_data = {
        "Property Name": ["SkyTower Offices", "Riverfront Executive Center"],
        "Address": ["123 Main St", "456 Water Ave"],
        "City": ["New York", "Chicago"],
        "Zip Code": ["10001", "60611"],
        "Neighborhood": ["Midtown", "River North"],
        "Property Type": ["Class A High-Rise", "Boutique Office Building"],
        "Size Range": ["5,000-50,000 sq ft", "2,000-15,000 sq ft"],
        "Key Features": ["Floor-to-ceiling windows, 24/7 security", "Rooftop terrace, Private parking"],
        "Nearby Businesses": ["JP Morgan, Deloitte", "Google, Boeing HQ"]
    }
    st.dataframe(pd.DataFrame(sample_data))
    
    # Download sample template
    sample_df = pd.DataFrame(sample_data)
    st.download_button(
        label="Download Sample Template",
        data=export_data(sample_df, "excel"),
        file_name="sample_property_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.divider()
st.caption("Centre Page Content Generator | Developed by MediaVision & Metis")


