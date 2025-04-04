import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
import requests
from io import BytesIO
from datetime import datetime

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
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "claude-3-sonnet-20240229"
if 'df' not in st.session_state:
    st.session_state.df = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []
if 'api_response' not in st.session_state:
    st.session_state.api_response = None
if 'excluded_terms' not in st.session_state:
    st.session_state.excluded_terms = []
if 'example_copies' not in st.session_state:
    st.session_state.example_copies = []
if 'batch_size' not in st.session_state:
    st.session_state.batch_size = 5
if 'api_delay' not in st.session_state:
    st.session_state.api_delay = 1

# Function to add debug information
def add_debug(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_info.append(f"[{timestamp}] {message}")
    if len(st.session_state.debug_info) > 20:  # Keep only the last 20 messages
        st.session_state.debug_info = st.session_state.debug_info[-20:]

# Generate high-quality office space content for a property
def generate_mock_content(property_data):
    """Generate sample shorter content without API for testing"""
    property_name = property_data.get('Property Name', 'Premium Office Space')
    city = property_data.get('City', 'Major City')
    neighborhood = property_data.get('Neighborhood', 'Business District')
    address = property_data.get('Address', '123 Main Street')
    zip_code = property_data.get('Zip Code', '12345')
    property_type = property_data.get('Property Type', 'Executive Office Space')
    key_features = property_data.get('Key Features', 'Modern amenities')
    
    content = f"""# {property_name} | Premium Workspace in {city}

Located at {address} in {neighborhood}, {property_name} offers prestigious {property_type} in a prime {city} location. This professional environment provides an ideal setting for businesses seeking visibility and convenience.

Featuring {key_features}, our workspace solutions include private offices, meeting facilities, and flexible administrative support tailored to executive needs.

Key amenities include:
* High-speed connectivity and modern technology
* Professional reception and business services
* Premium meeting spaces with state-of-the-art equipment
* Convenient access to major transportation routes

Contact us to schedule your exclusive tour and discover why {property_name} is the preferred choice for discerning executives in {city}.
"""
    return content

# Function to make direct HTTP request to Anthropic API
def call_anthropic_api(prompt, api_key, model="claude-3-sonnet-20240229"):
    """Make a direct HTTP request to the Anthropic API instead of using the SDK"""
    add_debug(f"Making direct HTTP request to Anthropic API using model: {model}")
    
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": model,
        "max_tokens": 1500,
        "temperature": 0.7,
        "system": "You are a professional content writer specializing in premium commercial real estate descriptions for executive audiences.",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        # Save full response for debugging
        st.session_state.api_response = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.text
        }
        
        if response.status_code != 200:
            add_debug(f"API Error: Status {response.status_code}, Response: {response.text[:200]}...")
            return f"API Error: Status {response.status_code}. Please check the debug log for details."
        
        response_data = response.json()
        
        if "content" in response_data and len(response_data["content"]) > 0:
            content_list = response_data["content"]
            all_content = ""
            for content_item in content_list:
                if content_item.get("type") == "text":
                    all_content += content_item.get("text", "")
            
            add_debug(f"Successfully extracted content of length: {len(all_content)}")
            return all_content
        else:
            add_debug(f"Empty or invalid response structure: {str(response_data)[:200]}...")
            return "Error: Empty or invalid API response structure. Please check the debug log."
            
    except Exception as e:
        add_debug(f"Request error: {str(e)}")
        return f"API request error: {str(e)}"

# Function to generate property description
def generate_property_description(property_data, api_key, model=None, use_mock=False):
    """Generate property description using direct API call or mock for testing"""
    try:
        if model is None:
            model = st.session_state.selected_model
        
        # Get excluded terms
        excluded_terms = st.session_state.excluded_terms
        excluded_terms_text = ""
        if excluded_terms:
            excluded_terms_text = "IMPORTANT: Do NOT use the following terms or phrases in your content:\n"
            for i, term in enumerate(excluded_terms):
                excluded_terms_text += f"{i+1}. \"{term}\"\n"
        
        # Get example copies
        example_copies = st.session_state.example_copies
        example_copies_text = ""
        if example_copies:
            example_copies_text = "\nHere are examples of good copy that you should emulate in style and tone:\n\n"
            for i, example in enumerate(example_copies):
                example_copies_text += f"EXAMPLE {i+1}:\n{example}\n\n"
            
        # Construct prompt from property data
        prompt = f"""You are a professional content writer for a luxury office space provider.
Write a concise office space description for executives and business leaders based on the following details:

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

The content MUST:
- Be SHORT - approximately 20 lines or less
- Have a brief headline, followed by 3-4 concise paragraphs
- Focus only on the most important selling points
- Use professional, upscale language appropriate for C-suite executives
- Include location advantages and the top 3-4 amenities

Format the content with:
- A main heading using # for the property name
- Very minimal formatting - use plain text for most content
- At most ONE bullet list with no more than 4 items

IMPORTANT: Be extremely concise. Remove all unnecessary adjectives and descriptions.
Prioritize brevity above all else while maintaining a professional tone.

{excluded_terms_text}
{example_copies_text}
"""
        
        # For debugging, add the prompt to debug info
        add_debug(f"Generated prompt with {len(prompt)} characters, including {len(excluded_terms)} excluded terms and {len(example_copies)} example copies")
        
        # Use mock content for testing or when API key is not available
        if use_mock or not api_key:
            add_debug("Using mock content generator (Test Mode)")
            return generate_mock_content(property_data)
            
        # Use direct API call with selected model
        return call_anthropic_api(prompt, api_key, model)
    
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
        index=list(model_options.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
    )
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        add_debug(f"Model changed to: {selected_model}")
    
    # Testing mode toggle
    use_mock_api = st.checkbox("Test Mode (No API Key Required)", value=not bool(api_key))
    if use_mock_api:
        st.info("Running in test mode - will use sample content instead of real API")
        add_debug("Test mode enabled")
    
    # Add horizontal line
    st.markdown("---")
    
    # Excluded Terms Setup
    st.subheader("Terms to Avoid")
    
    # Add term input
    new_term = st.text_input("Add term or phrase to exclude:")
    if st.button("Add Term") and new_term.strip():
        term = new_term.strip()
        if term not in st.session_state.excluded_terms:
            st.session_state.excluded_terms.append(term)
            add_debug(f"Added excluded term: '{term}'")
            st.success(f"Added: '{term}'")
            st.rerun()
    
    # Display current terms
    if st.session_state.excluded_terms:
        st.write("Current excluded terms:")
        for i, term in enumerate(st.session_state.excluded_terms):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(term)
            with col2:
                if st.button("🗑️", key=f"del_term_{i}"):
                    st.session_state.excluded_terms.pop(i)
                    add_debug(f"Removed excluded term: '{term}'")
                    st.rerun()
    
    # Add horizontal line
    st.markdown("---")
    
    # Example Content section
    st.subheader("Example Content")
    
    # Upload example copy file
    uploaded_example = st.file_uploader("Upload Example Copy", type=['txt'])
    if uploaded_example is not None:
        try:
            content = uploaded_example.getvalue().decode("utf-8")
            if content and content.strip():
                st.session_state.example_copies.append(content.strip())
                add_debug(f"Added example from file: {uploaded_example.name} ({len(content)} chars)")
                st.success(f"Added example from: {uploaded_example.name}")
                st.rerun()
        except Exception as e:
            st.error(f"Error loading example file: {str(e)}")
            add_debug(f"Error loading example file: {str(e)}")
    
    # Example copy text area
    example_text = st.text_area("Or paste example copy here:", height=150)
    if st.button("Add Example") and example_text.strip():
        st.session_state.example_copies.append(example_text.strip())
        add_debug(f"Added example copy ({len(example_text)} chars)")
        st.success("Example added!")
        st.rerun()
    
    # Display existing examples
    if st.session_state.example_copies:
        st.write(f"{len(st.session_state.example_copies)} examples loaded")
        with st.expander("View/Edit Examples"):
            for i, example in enumerate(st.session_state.example_copies):
                st.text(f"Example #{i+1} ({len(example)} chars)")
                if st.button("Remove", key=f"del_example_{i}"):
                    st.session_state.example_copies.pop(i)
                    add_debug(f"Removed example #{i+1}")
                    st.rerun()
                st.text_area(f"Example content", value=example, height=100, key=f"example_{i}")
    
    # Add horizontal line
    st.markdown("---")
    
    # File uploader
    st.subheader("Property Data")
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
                st.rerun()
        
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
st.title("Centre Page Content Generator")

# Show configuration status
status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    if use_mock_api:
        st.info("🔍 TEST MODE: Using sample content generator")
    elif st.session_state.selected_model:
        st.info(f"Using {model_options.get(st.session_state.selected_model, st.session_state.selected_model)}")

with status_col2:
    if st.session_state.excluded_terms:
        st.info(f"🚫 {len(st.session_state.excluded_terms)} terms excluded")
    
with status_col3:
    if st.session_state.example_copies:
        st.info(f"📄 {len(st.session_state.example_copies)} example copies loaded")

# Content generation in progress
if st.session_state.is_generating and st.session_state.df is not None:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_properties = len(st.session_state.df)
    add_debug(f"Beginning generation for {total_properties} properties")
    
    batch_size = st.session_state.batch_size
    delay = st.session_state.api_delay
    
    # Process in batches to avoid overwhelming the API
    for batch_start in range(0, total_properties, batch_size):
        batch_end = min(batch_start + batch_size, total_properties)
        
        for i in range(batch_start, batch_end):
            # Calculate overall progress
            progress = int((i / total_properties) * 100)
            progress_bar.progress(progress)
            
            idx = i
            row = st.session_state.df.iloc[idx]
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
                            st.session_state.selected_model,
                            use_mock=use_mock_api
                        )
                        st.session_state.generated_content[idx] = content
                        st.session_state.df.at[idx, 'Generated Content'] = content
                        add_debug(f"Generated {len(content) if content else 0} characters for {property_name}")
                    except Exception as e:
                        error_msg = f"Error generating content for {property_name}: {str(e)}"
                        st.error(error_msg)
                        add_debug(error_msg)
        
        # Add delay between batches if there are more to process
        if batch_end < total_properties and delay > 0 and not use_mock_api:
            add_debug(f"Pausing for {delay}s between batches")
            time.sleep(delay)
    
    progress_bar.progress(100)
    status_text.text(f"Generated descriptions for {total_properties} properties!")
    st.session_state.is_generating = False
    add_debug(f"Completed batch generation of {total_properties} properties")
    st.rerun()

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
                st.rerun()
    
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
                                    st.session_state.selected_model,
                                    use_mock=use_mock_api
                                )
                                st.session_state.generated_content[idx] = new_content
                                st.session_state.df.at[idx, 'Generated Content'] = new_content
                                st.success("Content regenerated successfully!")
                                add_debug(f"Regenerated content for {property_name} successfully")
                                st.rerun()
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
                        st.rerun()
                        
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
                                    st.session_state.selected_model,
                                    use_mock=use_mock_api
                                )
                                st.session_state.generated_content[idx] = content
                                st.session_state.df.at[idx, 'Generated Content'] = content
                                st.success("Content generated successfully!")
                                add_debug(f"Generated content for {property_name} successfully")
                                st.rerun()
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

# Advanced settings
with st.expander("Advanced Content Settings"):
    st.subheader("Content Analysis")
    
    # Analyze content for excluded terms
    if st.session_state.df is not None and 'Generated Content' in st.session_state.df.columns:
        if st.button("Check for Excluded Terms in All Content"):
            found_terms = {}
            for idx, row in st.session_state.df.iterrows():
                content = row.get('Generated Content', '')
                if content and isinstance(content, str):
                    property_name = row.get('Property Name', f'Property #{idx}')
                    found_in_this_property = []
                    
                    for term in st.session_state.excluded_terms:
                        if term.lower() in content.lower():
                            found_in_this_property.append(term)
                    
                    if found_in_this_property:
                        found_terms[property_name] = found_in_this_property
            
            if found_terms:
                st.error("Found excluded terms in content:")
                for property_name, terms in found_terms.items():
                    st.markdown(f"**{property_name}**: {', '.join(terms)}")
                add_debug(f"Found excluded terms in {len(found_terms)} properties")
            else:
                st.success("No excluded terms found in content!")
                add_debug("No excluded terms found in content")
    
    # Batch settings
    st.subheader("Batch Processing Settings")
    
    batch_size = st.slider("Batch Size", min_value=1, max_value=20, value=st.session_state.batch_size, 
                          help="Number of properties to process at once")
    
    delay = st.slider("Delay Between API Calls (seconds)", min_value=0, max_value=10, value=st.session_state.api_delay, 
                     help="Add delay between API calls to avoid rate limits")
    
    # Save settings to session state
    if st.button("Save Batch Settings"):
        st.session_state.batch_size = batch_size
        st.session_state.api_delay = delay
        st.success("Batch settings saved!")
        add_debug(f"Batch settings updated: size={batch_size}, delay={delay}s")
    
    # Export/Import excluded terms
    st.subheader("Export/Import Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Excluded Terms"):
            excluded_terms_data = "\n".join(st.session_state.excluded_terms)
            st.download_button(
                label="Download Excluded Terms",
                data=excluded_terms_data,
                file_name="excluded_terms.txt",
                mime="text/plain"
            )
    
    with col2:
        terms_file = st.file_uploader("Import Excluded Terms", type=['txt'], key="terms_upload")
        if terms_file is not None:
            try:
                content = terms_file.getvalue().decode("utf-8").strip()
                terms = [line.strip() for line in content.split("\n") if line.strip()]
                
                new_terms = [term for term in terms if term not in st.session_state.excluded_terms]
                if new_terms:
                    st.session_state.excluded_terms.extend(new_terms)
                    st.success(f"Added {len(new_terms)} new terms from file")
                    add_debug(f"Imported {len(new_terms)} excluded terms from file")
                else:
                    st.info("No new terms found in file")
            except Exception as e:
                st.error(f"Error importing terms: {str(e)}")

# Debug information (expandable section)
with st.expander("Debug Information"):
    st.subheader("Debug Log")
    for log in st.session_state.debug_info:
        st.text(log)
    
    if st.button("Clear Debug Log"):
        st.session_state.debug_info = []
        st.rerun()
    
    # Display raw API response if available
    if st.session_state.api_response:
        st.subheader("Last API Response")
        st.json(st.session_state.api_response)
    
    st.subheader("Session State")
    # Show non-sensitive session state info
    safe_state = {
        "selected_property": st.session_state.selected_property,
        "is_generating": st.session_state.is_generating,
        "progress": st.session_state.progress,
        "has_api_key": bool(st.session_state.api_key),
        "selected_model": st.session_state.selected_model,
        "excluded_terms_count": len(st.session_state.excluded_terms),
        "example_copies_count": len(st.session_state.example_copies),
        "content_count": len(st.session_state.generated_content),
        "has_dataframe": st.session_state.df is not None,
        "batch_size": st.session_state.batch_size,
        "api_delay": st.session_state.api_delay
    }
    
    if st.session_state.df is not None:
        safe_state["dataframe_shape"] = st.session_state.df.shape
        safe_state["dataframe_columns"] = list(st.session_state.df.columns)
    
    st.json(safe_state)

# Help information
with st.expander("Help & Usage Guide"):
    st.markdown("""
    ## Centre Page Content Generator - Usage Guide
    
    This application generates professional descriptions for office space properties using AI.
    
    ### Main Features
    
    1. **Property Data Management**
       - Upload property data in CSV or Excel format
       - Each property should include name, location, amenities, etc.
    
    2. **Content Customization**
       - **Excluded Terms**: Add specific terms you want to avoid in the content
       - **Example Copies**: Upload good examples to guide the AI's style and tone
       - **Model Selection**: Choose between different Claude models based on quality/speed needs
    
    3. **Content Generation**
       - Generate descriptions for all properties at once
       - Regenerate individual descriptions as needed
       - Edit generated content directly in the application
    
    4. **Export**
       - Download all property descriptions as CSV or Excel
       - Export your excluded terms list for future use
    
    ### Using Excluded Terms
    
    The "Terms to Avoid" feature helps maintain brand consistency and avoid specific language:
    - Add terms or phrases you don't want to appear in the generated content
    - The AI will actively avoid these terms during content creation
    - Use the content analysis tool to check if any excluded terms appear in the output
    
    ### Using Example Copies
    
    The example copies feature helps the AI match your preferred style:
    - Upload or paste examples of well-written property descriptions
    - The AI will emulate the tone, structure, and style of these examples
    - More examples = better understanding of your preferred style
    
    ### Advanced Settings
    
    - **Batch Processing**: Control how many properties are processed at once
    - **API Delays**: Add time between API calls to avoid rate limits
    - **Content Analysis**: Check if generated content contains excluded terms
    """)

# Footer
st.markdown("---")
st.caption("Centre Page Content Generator | Developed by MediaVision & Metis")
