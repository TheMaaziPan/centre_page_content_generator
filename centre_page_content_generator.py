import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from io import BytesIO
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Office Space Content Generator",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'selected_property' not in st.session_state:
    st.session_state.selected_property = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# Function to generate property description
# This is a mock function that will be replaced with actual AI implementation
def generate_property_description(property_data):
    """Generate property description using a template approach"""
    try:
        # Extract key properties with fallbacks to prevent errors
        property_name = property_data.get('Property Name', 'Office Space')
        city = property_data.get('City', 'City')
        zip_code = property_data.get('Zip Code', '')
        neighborhood = property_data.get('Neighborhood', 'Business District')
        property_type = property_data.get('Property Type', 'Commercial Space')
        size_range = property_data.get('Size Range', 'Flexible square footage')
        building_desc = property_data.get('Building Description', 'Modern building')
        key_features = property_data.get('Key Features', 'Multiple amenities')
        nearby = property_data.get('Nearby Businesses', 'Local businesses')
        transport = property_data.get('Transport Access', 'Convenient access')
        tech = property_data.get('Technology Features', 'Modern technology')
        meeting_rooms = property_data.get('Meeting Rooms', 'Conference facilities')
        common_areas = property_data.get('Common Areas', 'Shared spaces')
        business_services = property_data.get('Business Services', 'Support services')
        security = property_data.get('Security Features', 'Secure access')
        wellness = property_data.get('Wellness Amenities', 'Wellness options')
        configurations = property_data.get('Office Configurations', 'Flexible layouts')
        lease_options = property_data.get('Lease Options', 'Various terms available')
        contact = property_data.get('Contact Information', 'Contact our team')
        
        # Template-based content generation
        content = f"""# {property_name} | Premium Workspace in {neighborhood}, {city}

## Executive Summary
Elevate your business operations at {property_name}, a prestigious {property_type} workspace strategically located in {neighborhood}. Offering {size_range} of premium office space, this {building_desc} provides the ideal environment for companies seeking exceptional workspace solutions in {city}'s thriving business district. With {key_features}, {property_name} delivers an unparalleled professional experience designed for business leaders who demand excellence.

## Prime Location Advantage
Positioned in {zip_code}, {property_name} offers exceptional accessibility in one of {city}'s most sought-after business districts. Your team and clients will appreciate the convenient {transport}, while being surrounded by {nearby}. The area features premium amenities including upscale dining options and hotels, ensuring all your business hospitality needs are seamlessly accommodated.

## Executive Amenities & Services
{property_name} features a comprehensive suite of premium amenities tailored to executive needs:

* **State-of-the-Art Technology**: {tech} ensuring seamless connectivity and performance
* **Professional Meeting Spaces**: {meeting_rooms} equipped with modern presentation tools
* **Exceptional Common Areas**: {common_areas}
* **Business Support Services**: {business_services}
* **Security & Access**: {security}
* **Wellness Facilities**: {wellness} promoting executive well-being

## Flexible Workspace Solutions
Whether your organization requires intimate team spaces or expansive headquarters, {property_name} offers customizable configurations to match your precise requirements:

* **Private Offices**: Premium private workspaces
* **Executive Suites**: {configurations}
* **Team Workspaces**: Collaborative environments designed for productivity and engagement
* **Flexible Terms**: {lease_options}

## Secure Your Premium {city} Workspace
Join the distinguished community of business leaders who have established their operations at {property_name}. Contact our dedicated team at {contact} to arrange your exclusive tour and discover why {property_name} is the preferred choice for discerning executives in {city}.
"""
        return content
    
    except Exception as e:
        return f"Error generating content: {str(e)}"

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
st.title("Office Space Content Generator")

# Content generation in progress
if st.session_state.is_generating and st.session_state.df is not None:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_properties = len(st.session_state.df)
    
    for i, (idx, row) in enumerate(st.session_state.df.iterrows()):
        # Update progress
        progress = int((i / total_properties) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Generating description for {row.get('Property Name', f'Property #{idx}')}... ({i+1}/{total_properties})")
        
        # Generate content if not already generated
        if idx not in st.session_state.generated_content:
            property_data = row.to_dict()
            content = generate_property_description(property_data)
            st.session_state.generated_content[idx] = content
            st.session_state.df.at[idx, 'Generated Content'] = content
        
        # Simulate processing time (remove in production)
        time.sleep(0.1)
    
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
            st.info(f"**Property:** {property_data.get('Property Name', 'N/A')}\n\n**Location:** {property_data.get('City', 'N/A')}, {property_data.get('Zip Code', 'N/A')}")
            
            # Display or generate content for selected property
            if idx in st.session_state.generated_content:
                content = st.session_state.generated_content[idx]
                st.markdown(content)
                
                # Edit content
                if st.button("Regenerate", key=f"regen_{idx}"):
                    with st.spinner("Regenerating content..."):
                        new_content = generate_property_description(property_data)
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
                    with st.spinner("Generating content..."):
                        content = generate_property_description(property_data)
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
st.caption("Office Space Content Generator | Developed by Your Company © 2025")

# Add notes about integrating with AI services
with st.expander("Integration Notes"):
    st.markdown("""
    ## AI Integration Options
    
    This demo uses a template-based approach for content generation. In production, you would integrate with an AI service:
    
    1. **OpenAI API**: Use GPT models for text generation
    2. **Anthropic API**: Use Claude models for nuanced business writing
    3. **Cohere or AI21**: Alternative enterprise-focused AI providers
    
    ### Implementation Steps
    
    1. Add your chosen AI provider's SDK to requirements.txt
    2. Replace the `generate_property_description()` function with API calls
    3. Add appropriate API key management and rate limiting
    4. Consider batch processing for large datasets
    
    ### Example Integration Code
    
    ```python
    # Example OpenAI integration
    from openai import OpenAI
    
    def generate_with_openai(property_data, api_key):
        client = OpenAI(api_key=api_key)
        
        prompt = f"Write a premium office space description for {property_data['Property Name']}..."
        
        response = client.completions.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].text
    ```
    """)
