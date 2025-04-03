import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
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
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'df' not in st.session_state:
    st.session_state.df = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []

# Function to add debug information
def add_debug(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_info.append(f"[{timestamp}] {message}")
    if len(st.session_state.debug_info) > 20:  # Keep only the last 20 messages
        st.session_state.debug_info = st.session_state.debug_info[-20:]

# Mock Anthropic API for testing
def mock_anthropic_api(prompt, api_key):
    """Mock function to simulate Anthropic API response"""
    add_debug("Using mock Anthropic API (for testing only)")
    
    # Extract property name from prompt
    property_name = "Office Space"
    for line in prompt.split('\n'):
        if "Property Name:" in line:
            property_name = line.split("Property Name:")[1].strip()
            if property_name == "N/A":
                property_name = "Premium Office Space"
    
    # Create a sample response
    sample_response = f"""# {property_name} | Premium Executive Workspace

## Executive Summary
{property_name} offers a prestigious workspace experience tailored to the discerning needs of executives and business leaders. This premium office environment seamlessly blends sophistication with functionality, providing an inspiring setting that fosters innovation, collaboration, and success.

## Location Advantages
Strategically situated in a vibrant business district, {property_name} enjoys excellent accessibility and prestigious surroundings. The prime location puts you at the center of business activity with convenient access to major transportation routes, dining options, and business services.

## Premium Amenities
* **Furnished Private Offices**: Meticulously designed workspaces with premium furnishings
* **State-of-the-Art Technology**: High-speed internet and advanced telecommunications
* **Elegant Meeting Rooms**: Professional spaces for client meetings and team collaboration
* **Business Support Services**: Reception, mail handling, and administrative assistance
* **Security Features**: 24/7 secure access for peace of mind

## Workspace Options
Choose from a variety of flexible workspace solutions including private offices, executive suites, and collaborative areas. Each space is designed to accommodate your specific requirements and can be customized to reflect your brand and operational needs.

## Call to Action
Elevate your business presence by securing your space at {property_name}. Contact our dedicated team today to schedule a personalized tour and discover how our exceptional workspace can propel your success.
"""
    
    return sample_response

# Function to generate property description (with option to use real or mock API)
def generate_property_description(property_data, api_key, use_mock=False):
    """Generate property description using Anthropic API or mock for testing"""
    try:
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
        
        IMPORTANT: Format the content with proper markdown headings (# for main heading, ## for subheadings) and bullet points where appropriate.
        Do NOT include escape characters like \\n in your response - use actual line breaks instead.
        Do NOT escape markdown symbols - write # not \\#.
        Structure the content clearly with sections for Executive Summary, Location Advantages, Premium Amenities, Workspace Options, and Call to Action.
        """
        
        # For debugging, add the prompt to debug info
        add_debug(f"Generated prompt with {len(prompt)} characters")
        
        # Use mock API for testing or when real API key is not available
        if use_mock or not api_key:
            add_debug("API Key empty or mock mode enabled - using mock API")
            return mock_anthropic_api(prompt, api_key)
            
        # Use real Anthropic API
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            add_debug("Initialized Anthropic client")
            
            # Make API call to Anthropic's Claude
            add_debug("Sending request to Anthropic API...")
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
            add_debug(f"Received response from API with content length: {len(message.content)}")
            return message.content
            
        except ImportError:
            add_debug("Anthropic module not installed - using mock API")
            return mock_anthropic_api(prompt, api_key)
        except Exception as e:
            add_debug(f"API Error: {str(e)}")
            # Fall back to mock API on error
            return mock_anthropic_api(prompt, api_key)
    
    except Exception as e:
        add_debug(f"Error in generate_property_description: {str(e)}")
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
    
    # API Key input
    api_key = st.text_input("Enter Anthropic API Key:", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
        add_debug("API key set (hidden for security)")
    
    # Testing mode toggle
    use_mock_api = st.checkbox("Test Mode (No API Key Required)", value=not bool(api_key))
    if use_mock_api:
        st.info("Running in test mode - will use sample content instead of real API")
        add_debug("Test mode enabled")
    
    st.divider()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Property Data", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                add_debug(f"Loaded CSV file: {uploaded_file.name}")
            else:
                df = pd.read_excel(uploaded_file)
                add_debug(f"Loaded Excel file: {uploaded_file.name}")
                
            st.session_state.df = df
            st.success(f"Loaded {len(df)} properties")
            
            # Display data fields for verification
            if st.checkbox("Show data fields"):
                st.write("Detected columns:")
                columns = df.columns.tolist()
                st.write(", ".join(columns))
                add_debug(f"Detected {len(columns)} columns: {', '.join(columns[:5])}...")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            add_debug(f"Error loading file: {str(e)}")
    
    st.divider()
    
    # Generation controls
    if st.session_state.df is not None:
        if st.button("Generate All Descriptions"):
            if not st.session_state.api_key and not use_mock_api:
                st.error("Please enter Anthropic API key first or enable Test Mode")
                add_debug("Generation failed - no API key and test mode disabled")
            else:
                st.session_state.is_generating = True
                st.session_state.progress = 0
                add_debug("Starting batch generation")
                
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
                add_debug(f"Exported data as {export_format}")

# Main content area
st.title("Office Space Content Generator")

# API key validation
if not st.session_state.api_key and not use_mock_api and 'api_status' not in st.session_state:
    st.warning("⚠️ Please enter your Anthropic API key in the sidebar to use AI-generated content. Without an API key, enable Test Mode to use sample content.")
    st.session_state.api_status = "warned"

# Content generation in progress
if st.session_state.is_generating and st.session_state.df is not None:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_properties = len(st.session_state.df)
    add_debug(f"Beginning generation for {total_properties} properties")
    
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
                    add_debug(f"Generating content for {property_name}")
                    # Pass use_mock flag based on checkbox
                    content = generate_property_description(
                        property_data, 
                        st.session_state.api_key,
                        use_mock=use_mock_api
                    )
                    st.session_state.generated_content[idx] = content
                    st.session_state.df.at[idx, 'Generated Content'] = content
                    add_debug(f"Generated {len(content) if content else 0} characters for {property_name}")
                except Exception as e:
                    error_msg = f"Error generating content for {property_name}: {str(e)}"
                    st.error(error_msg)
                    add_debug(error_msg)
    
    progress_bar.progress(100)
    status_text.text(f"Generated descriptions for {total_properties} properties!")
    st.session_state.is_generating = False
    add_debug(f"Completed batch generation of {total_properties} properties")

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
                add_debug(f"Selected property: {property_name}")
    
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
                
                # Safety check to ensure content is a string
                if content is not None and isinstance(content, str) and content.strip():
                    # Clean up the content to ensure proper markdown rendering
                    # Remove any '\n' escape sequences that might be in the text
                    cleaned_content = content.replace('\\n', '\n')
                    # Remove any extra backslashes before markdown characters
                    cleaned_content = cleaned_content.replace('\\#', '#').replace('\\*', '*').replace('\\-', '-')
                    # Display using markdown
                    st.markdown(cleaned_content)
                    add_debug(f"Displayed content for {property_name} ({len(cleaned_content)} chars)")
                else:
                    st.error("Content appears to be empty or invalid. Please try regenerating.")
                    add_debug(f"Empty or invalid content for {property_name}")
                    content = ""  # Set a default empty string
                
                # Regenerate button
                if st.button("Regenerate", key=f"regen_{idx}"):
                    if not st.session_state.api_key and not use_mock_api:
                        st.error("Please enter Anthropic API key first or enable Test Mode")
                    else:
                        with st.spinner("Regenerating content..."):
                            try:
                                add_debug(f"Regenerating content for {property_name}")
                                new_content = generate_property_description(
                                    property_data, 
                                    st.session_state.api_key,
                                    use_mock=use_mock_api
                                )
                                st.session_state.generated_content[idx] = new_content
                                st.session_state.df.at[idx, 'Generated Content'] = new_content
                                st.success("Content regenerated successfully!")
                                add_debug(f"Regenerated content for {property_name} successfully")
                                
                                # Display new content
                                if new_content is not None and isinstance(new_content, str) and new_content.strip():
                                    cleaned_new_content = new_content.replace('\\n', '\n')
                                    cleaned_new_content = cleaned_new_content.replace('\\#', '#').replace('\\*', '*').replace('\\-', '-')
                                    st.markdown("### New Content:")
                                    st.markdown(cleaned_new_content)
                                else:
                                    st.error("Regenerated content is empty or invalid.")
                                    add_debug("Regenerated content is empty or invalid")
                            except Exception as e:
                                st.error(f"Error regenerating content: {str(e)}")
                                add_debug(f"Error during regeneration: {str(e)}")
                
                # Use cleaned content for editing
                if content is not None and isinstance(content, str):
                    cleaned_content = content.replace('\\n', '\n')
                    cleaned_content = cleaned_content.replace('\\#', '#').replace('\\*', '*').replace('\\-', '-')
                    edited_content = st.text_area("Edit Content", value=cleaned_content, height=400)
                else:
                    edited_content = st.text_area("Edit Content", value="", height=400)
                
                if edited_content != (cleaned_content if isinstance(content, str) else ""):
                    if st.button("Save Edits", key=f"save_{idx}"):
                        st.session_state.generated_content[idx] = edited_content
                        st.session_state.df.at[idx, 'Generated Content'] = edited_content
                        st.success("Changes saved!")
                        add_debug(f"Saved edited content for {property_name}")
                        
            else:
                st.info("No content generated yet. Click the button below to generate content.")
                
                if st.button("Generate Description", key=f"gen_{idx}"):
                    if not st.session_state.api_key and not use_mock_api:
                        st.error("Please enter Anthropic API key first or enable Test Mode")
                        add_debug("Generation failed - no API key and test mode disabled")
                    else:
                        with st.spinner("Generating content..."):
                            try:
                                add_debug(f"Generating content for {property_name}")
                                content = generate_property_description(
                                    property_data, 
                                    st.session_state.api_key,
                                    use_mock=use_mock_api
                                )
                                st.session_state.generated_content[idx] = content
                                st.session_state.df.at[idx, 'Generated Content'] = content
                                st.success("Content generated successfully!")
                                add_debug(f"Generated content for {property_name} successfully")
                                
                                # Display the newly generated content
                                if content is not None and isinstance(content, str) and content.strip():
                                    cleaned_content = content.replace('\\n', '\n')
                                    cleaned_content = cleaned_content.replace('\\#', '#').replace('\\*', '*').replace('\\-', '-')
                                    st.markdown(cleaned_content)
                                else:
                                    st.error("Generated content is empty or invalid.")
                                    add_debug("Generated content is empty or invalid")
                            except Exception as e:
                                st.error(f"Error generating content: {str(e)}")
                                add_debug(f"Error during generation: {str(e)}")
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

# Debug information (expandable section)
with st.expander("Debug Information"):
    st.subheader("Debug Log")
    for log in st.session_state.debug_info:
        st.text(log)
    
    if st.button("Clear Debug Log"):
        st.session_state.debug_info = []
        st.experimental_rerun()
    
    st.subheader("Session State")
    # Show non-sensitive session state info
    safe_state = {
        "selected_property": st.session_state.selected_property,
        "is_generating": st.session_state.is_generating,
        "progress": st.session_state.progress,
        "has_api_key": bool(st.session_state.api_key),
        "content_count": len(st.session_state.generated_content),
        "has_dataframe": st.session_state.df is not None,
    }
    
    if st.session_state.df is not None:
        safe_state["dataframe_shape"] = st.session_state.df.shape
        safe_state["dataframe_columns"] = list(st.session_state.df.columns)
    
    st.json(safe_state)

# Footer
st.divider()
st.caption("Office Space Content Generator | Developed by Your Company © 2025")
