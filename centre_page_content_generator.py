# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    st.subheader("Batch Processing Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batch_size = st.slider("Batch Size", min_value=1, max_value=20, value=st.session_state.batch_size, 
                              help="Number of properties to process at once")
    
    with col2:
        delay = st.slider("API Delay (seconds)", min_value=0, max_value=10, value=st.session_state.api_delay, 
                         help="Delay between API calls to avoid rate limits")
    
    if st.button("Save Settings"):
        st.session_state.batch_size = batch_size
        st.session_state.api_delay = delay
        st.success("Settings saved!")
        add_debug(f"Updated settings: batch_size={batch_size}, delay={delay}s")
    
    # Scraped Data Editor
    if st.session_state.scraped_properties:
        st.markdown("---")
        st.subheader("✏️ Edit Scraped Data")
        
        # Select property to edit
        property_names = [p.get('Property Name', f'Property {i+1}') for i, p in enumerate(st.session_state.scraped_properties)]
        selected_prop_idx = st.selectbox("Select property to edit:", range(len(property_names)), format_func=lambda x: property_names[x])
        
        if selected_prop_idx is not None:
            prop = st.session_state.scraped_properties[selected_prop_idx]
            
            # Create editable fields
            st.markdown("#### Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                prop['Property Name'] = st.text_input("Property Name", value=prop.get('Property Name', ''), key=f"edit_name_{selected_prop_idx}")
                prop['Address'] = st.text_input("Address", value=prop.get('Address', ''), key=f"edit_addr_{selected_prop_idx}")
                prop['City'] = st.text_input("City", value=prop.get('City', ''), key=f"edit_city_{selected_prop_idx}")
                prop['State'] = st.text_input("State", value=prop.get('State', ''), key=f"edit_state_{selected_prop_idx}")
            
            with col2:
                prop['Zip Code'] = st.text_input("Zip Code", value=prop.get('Zip Code', ''), key=f"edit_zip_{selected_prop_idx}")
                prop['Neighborhood'] = st.text_input("Neighborhood", value=prop.get('Neighborhood', ''), key=f"edit_neighborhood_{selected_prop_idx}")
                prop['Property Type'] = st.text_input("Property Type", value=prop.get('Property Type', 'Office Space'), key=f"edit_import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
import requests
from io import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# Set page config
st.set_page_config(
    page_title="Centre Page Content Generator - SEO Enhanced",
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
if 'target_keywords' not in st.session_state:
    st.session_state.target_keywords = ['office space', 'executive office', 'workspace']
if 'scraped_properties' not in st.session_state:
    st.session_state.scraped_properties = []
if 'scraping_in_progress' not in st.session_state:
    st.session_state.scraping_in_progress = False

# Function to add debug information
def add_debug(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_info.append(f"[{timestamp}] {message}")
    if len(st.session_state.debug_info) > 20:  # Keep only the last 20 messages
        st.session_state.debug_info = st.session_state.debug_info[-20:]

# SEO Analysis Functions
def analyze_seo_quality(content, property_data):
    """Analyze content for SEO best practices"""
    if not content:
        return {}
    
    analysis = {
        "word_count": len(content.split()),
        "has_address": property_data.get('Address', '') in content if property_data.get('Address') else False,
        "location_mentions": content.lower().count(property_data.get('City', '').lower()) if property_data.get('City') else 0,
        "keyword_density": {},
        "readability_score": None,
        "has_cta": any(cta in content.lower() for cta in ['contact', 'schedule', 'book', 'visit', 'tour', 'call']),
        "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
        "has_h1": content.strip().startswith('#'),
        "seo_score": 0
    }
    
    # Calculate keyword density for important terms
    keywords = st.session_state.target_keywords + ['meeting room', 'business', property_data.get('City', ''), property_data.get('Neighborhood', '')]
    for keyword in keywords:
        if keyword:
            count = content.lower().count(keyword.lower())
            density = (count / len(content.split())) * 100 if content else 0
            analysis["keyword_density"][keyword] = {
                "count": count,
                "density": f"{density:.1f}%"
            }
    
    # Simple readability check (average sentence length)
    sentences = [s for s in content.split('.') if s.strip()]
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    analysis["avg_sentence_length"] = round(avg_sentence_length, 1)
    analysis["readability_score"] = "Good" if avg_sentence_length < 20 else "Complex"
    
    # Calculate SEO score
    score = 0
    if 150 <= analysis['word_count'] <= 300:
        score += 20
    if analysis['has_address']:
        score += 20
    if analysis['location_mentions'] >= 2:
        score += 20
    if analysis['has_cta']:
        score += 20
    if analysis['has_h1']:
        score += 10
    if analysis['readability_score'] == 'Good':
        score += 10
    
    analysis['seo_score'] = score
    
    return analysis

def generate_meta_description(property_data, content):
    """Generate SEO-friendly meta description"""
    property_name = property_data.get('Property Name', 'Office Space')
    city = property_data.get('City', '')
    neighborhood = property_data.get('Neighborhood', '')
    
    # Extract key features from content
    features = []
    feature_keywords = {
        'meeting': 'meeting rooms',
        'parking': 'parking',
        '24/7': '24/7 access',
        'security': 'secure access',
        'wifi': 'high-speed internet',
        'furnished': 'furnished offices',
        'flexible': 'flexible terms'
    }
    
    for keyword, feature in feature_keywords.items():
        if keyword in content.lower():
            features.append(feature)
    
    features_text = ', '.join(features[:2]) if features else 'premium amenities'
    
    # Build meta description
    if neighborhood and city:
        meta = f"{property_name} in {neighborhood}, {city}. Professional office space with {features_text}. Schedule your tour today."
    elif city:
        meta = f"{property_name} in {city}. Executive office space featuring {features_text}. Contact us for availability."
    else:
        meta = f"{property_name} - Premium office space with {features_text}. Book your viewing today."
    
    # Ensure it's under 160 characters
    if len(meta) > 160:
        meta = meta[:157] + "..."
    
    return meta

def generate_schema_markup(property_data):
    """Generate Schema.org structured data for local SEO"""
    schema = {
        "@context": "https://schema.org",
        "@type": "OfficeSpace",
        "name": property_data.get('Property Name', ''),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": property_data.get('Address', ''),
            "addressLocality": property_data.get('City', ''),
            "postalCode": property_data.get('Zip Code', ''),
            "addressRegion": property_data.get('State', ''),
            "addressCountry": "US"
        },
        "description": property_data.get('Building Description', ''),
        "amenityFeature": []
    }
    
    # Add geo coordinates if available
    if property_data.get('Latitude') and property_data.get('Longitude'):
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": property_data.get('Latitude', ''),
            "longitude": property_data.get('Longitude', '')
        }
    
    # Add amenities
    amenities = property_data.get('Key Features', '').split(',')
    for amenity in amenities:
        if amenity.strip():
            schema["amenityFeature"].append({
                "@type": "LocationFeatureSpecification",
                "name": amenity.strip()
            })
    
    return json.dumps(schema, indent=2)

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
    
    content = f"""# {property_name} - Office Space in {city}

Located at {address} in the heart of {neighborhood}, {property_name} offers premium {property_type} for businesses seeking a prestigious {city} location. This professional workspace combines convenience with sophisticated amenities.

Our {neighborhood} office space features {key_features}, including private offices, modern meeting rooms, and flexible workspace solutions. With high-speed connectivity and professional support services, your business will thrive in this dynamic environment.

Key benefits of this {city} office space include convenient parking, 24/7 secure access, and proximity to major transportation routes. The building offers stunning views and natural light throughout.

Schedule your tour of {property_name} today and discover why leading businesses choose our {neighborhood} location. Contact us now to explore available office space options."""
    
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
        "system": "You are an SEO content specialist writing optimized commercial real estate descriptions that rank well on Google.",
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
            excluded_terms_text = "\n\nIMPORTANT: Do NOT use the following terms or phrases in your content:\n"
            for i, term in enumerate(excluded_terms):
                excluded_terms_text += f"{i+1}. \"{term}\"\n"
        
        # Get example copies
        example_copies = st.session_state.example_copies
        example_copies_text = ""
        if example_copies:
            example_copies_text = "\n\nHere are examples of good copy that you should emulate in style and tone:\n\n"
            for i, example in enumerate(example_copies):
                example_copies_text += f"EXAMPLE {i+1}:\n{example}\n\n"
        
        # Get target keywords
        target_keywords = ', '.join(st.session_state.target_keywords) if st.session_state.target_keywords else 'office space, executive office'
            
        # Enhanced SEO-focused prompt
        prompt = f"""You are an SEO content specialist writing for a luxury office space provider.
Create a Google-optimized office space description that will rank well in search results.

Property Details:
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

Target Keywords: {target_keywords}

SEO Requirements:
1. Start with a compelling H1 title that includes the property name, "Office Space" and location
2. Include the full address naturally in the first paragraph
3. Use location-based keywords (city, neighborhood) 2-3 times naturally throughout
4. Include "office space" or "executive office" variations 2-3 times
5. Mention specific amenities and features using semantic keywords
6. Keep content between 150-300 words for optimal engagement
7. Use short paragraphs (2-3 sentences max) for readability
8. Include a clear call-to-action in the final paragraph
9. Write in active voice and present tense
10. Focus on benefits rather than just features
11. Include local landmarks or nearby businesses if relevant

Content Structure:
- H1 Title using # (include property name + "Office Space" + location)
- Opening paragraph with address and main value proposition
- 2-3 short paragraphs highlighting key features and benefits
- Closing paragraph with clear CTA (Schedule tour, Contact us, etc.)

Write naturally for humans first, search engines second. Avoid:
- Keyword stuffing or unnatural repetition
- Generic phrases like "state-of-the-art" or "premier location"
- Long, complex sentences
- Passive voice
- Overly promotional language
- More than 4 bullet points if using a list

{excluded_terms_text}
{example_copies_text}

Write the SEO-optimized content now:"""
        
        # For debugging, add the prompt to debug info
        add_debug(f"Generated SEO-enhanced prompt with {len(prompt)} characters")
        
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
def export_data(df, format_type, include_seo=False):
    """Export dataframe with generated content and optional SEO data"""
    export_df = df.copy()
    
    if include_seo and 'Generated Content' in df.columns:
        # Add SEO columns
        export_df['Meta Description'] = ''
        export_df['Word Count'] = ''
        export_df['SEO Score'] = ''
        export_df['Has CTA'] = ''
        export_df['Location Mentions'] = ''
        
        for idx, row in df.iterrows():
            content = row.get('Generated Content', '')
            if content and isinstance(content, str):
                # Generate meta description
                meta_desc = generate_meta_description(row.to_dict(), content)
                export_df.at[idx, 'Meta Description'] = meta_desc
                
                # SEO analysis
                seo_analysis = analyze_seo_quality(content, row.to_dict())
                export_df.at[idx, 'Word Count'] = seo_analysis.get('word_count', 0)
                export_df.at[idx, 'SEO Score'] = f"{seo_analysis.get('seo_score', 0)}%"
                export_df.at[idx, 'Has CTA'] = 'Yes' if seo_analysis.get('has_cta', False) else 'No'
                export_df.at[idx, 'Location Mentions'] = seo_analysis.get('location_mentions', 0)
    
    if format_type == 'csv':
        return export_df.to_csv(index=False).encode('utf-8')
    elif format_type == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, sheet_name='Property Descriptions', index=False)
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
    
    # SEO Settings
    st.subheader("🎯 SEO Settings")
    
    # Target keywords
    keywords_text = st.text_area(
        "Target Keywords (one per line):",
        value='\n'.join(st.session_state.target_keywords),
        height=100,
        help="These keywords will be naturally incorporated into the content"
    )
    if keywords_text:
        new_keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
        if new_keywords != st.session_state.target_keywords:
            st.session_state.target_keywords = new_keywords
            add_debug(f"Updated target keywords: {len(new_keywords)} keywords")
    
    # SEO Tips
    with st.expander("📚 SEO Best Practices"):
        st.markdown("""
        **Google-Friendly Content Tips:**
        - ✅ Include full address early
        - ✅ Use location 2-3 times naturally
        - ✅ Keep content 150-300 words
        - ✅ Short paragraphs (2-3 sentences)
        - ✅ Clear call-to-action
        - ✅ Specific amenities mentioned
        - ✅ Local landmarks if relevant
        - ✅ Active voice throughout
        - ✅ Focus on user benefits
        - ❌ Avoid keyword stuffing
        - ❌ No generic phrases
        - ❌ No complex sentences
        """)
    
    # Add horizontal line
    st.markdown("---")
    
    # Excluded Terms Setup
    st.subheader("🚫 Terms to Avoid")
    
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
    st.subheader("📄 Example Content")
    
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
                st.text_area(f"Example content", value=example, height=100, key=f"example_{i}", disabled=True)
    
    # Add horizontal line
    st.markdown("---")
    
    # File uploader
    st.subheader("📊 Property Data")
    
    # Add tabs for different input methods
    data_tab1, data_tab2 = st.tabs(["Upload File", "Scrape from URL"])
    
    with data_tab1:
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
    
    with data_tab2:
        st.markdown("### 🔗 Scrape Property Data")
        st.caption("Extract property information from website URLs")
        
        # URL input
        url_input = st.text_input("Enter property URL:", placeholder="https://example.com/property-page")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Scrape URL", use_container_width=True):
                if url_input:
                    with st.spinner("Scraping property data..."):
                        property_data = scrape_property_data(url_input)
                        if property_data:
                            st.session_state.scraped_properties.append(property_data)
                            st.success("✅ Property data extracted!")
                            add_debug(f"Added scraped property: {property_data.get('Property Name', 'Unknown')}")
                        else:
                            st.error("Failed to extract data. Please check the URL.")
                else:
                    st.warning("Please enter a URL")
        
        with col2:
            if st.button("🗑️ Clear Scraped", use_container_width=True):
                st.session_state.scraped_properties = []
                st.success("Cleared scraped properties")
                st.rerun()
        
        # Bulk URL input
        with st.expander("📋 Bulk URL Import"):
            urls_text = st.text_area(
                "Paste multiple URLs (one per line):",
                height=150,
                placeholder="https://example.com/property1\nhttps://example.com/property2\nhttps://example.com/property3"
            )
            
            if st.button("🔍 Scrape All URLs"):
                if urls_text:
                    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
                    if urls:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, url in enumerate(urls):
                            status_text.text(f"Scraping {i+1}/{len(urls)}: {url[:50]}...")
                            progress_bar.progress((i + 1) / len(urls))
                            
                            property_data = scrape_property_data(url)
                            if property_data:
                                st.session_state.scraped_properties.append(property_data)
                                add_debug(f"Scraped: {property_data.get('Property Name', 'Unknown')}")
                            
                            # Small delay to avoid overwhelming servers
                            time.sleep(1)
                        
                        status_text.text(f"✅ Scraped {len(st.session_state.scraped_properties)} properties")
                        st.success(f"Completed scraping {len(urls)} URLs")
                else:
                    st.warning("Please enter at least one URL")
        
        # Display scraped properties
        if st.session_state.scraped_properties:
            st.markdown(f"### Scraped Properties ({len(st.session_state.scraped_properties)})")
            
            # Show summary of scraped data
            for i, prop in enumerate(st.session_state.scraped_properties):
                with st.expander(f"{prop.get('Property Name', f'Property {i+1}')} - {prop.get('City', 'Unknown')}"):
                    # Display key fields
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text(f"Address: {prop.get('Address', 'N/A')}")
                        st.text(f"City: {prop.get('City', 'N/A')}")
                        st.text(f"Zip: {prop.get('Zip Code', 'N/A')}")
                    with col2:
                        st.text(f"Features: {len(prop.get('Key Features', '').split(',')) if prop.get('Key Features') else 0} items")
                        st.text(f"Source: {prop.get('Source URL', 'N/A')[:30]}...")
                    
                    # Option to remove
                    if st.button(f"Remove", key=f"remove_scraped_{i}"):
                        st.session_state.scraped_properties.pop(i)
                        st.rerun()
            
            # Convert to DataFrame
            if st.button("📊 Use Scraped Data", type="primary", use_container_width=True):
                df = create_dataframe_from_scraped_data(st.session_state.scraped_properties)
                if df is not None:
                    st.session_state.df = df
                    st.success(f"Created dataset with {len(df)} properties")
                    add_debug(f"Converted {len(df)} scraped properties to DataFrame")
                    st.rerun()
                else:
                    st.error("No data to convert")
        
        # Tips for scraping
        with st.expander("💡 Scraping Tips"):
            st.markdown("""
            **Best practices for URL scraping:**
            - Use property detail pages, not listing pages
            - Ensure URLs are publicly accessible
            - Some sites may block automated access
            - Data extraction quality varies by site structure
            
            **What we look for:**
            - Property name and address
            - Location details (city, state, zip)
            - Features and amenities lists
            - Building descriptions
            - Contact information
            - Transportation access
            
            **Note:** Scraped data may need manual review and editing.
            """)
    
    # Show current data status
    if st.session_state.df is not None:
        st.markdown("---")
        st.success(f"✅ {len(st.session_state.df)} properties loaded")
        
        # Option to append scraped data to existing
        if st.session_state.scraped_properties:
            if st.button("➕ Add Scraped to Existing Data"):
                new_df = create_dataframe_from_scraped_data(st.session_state.scraped_properties)
                if new_df is not None:
                    st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                    st.session_state.scraped_properties = []
                    st.success(f"Added {len(new_df)} properties to existing data")
                    st.rerun()

# Main content area
st.title("🏢 Centre Page Content Generator - SEO Enhanced")

# Show configuration status
status_col1, status_col2, status_col3, status_col4 = st.columns(4)
with status_col1:
    if use_mock_api:
        st.info("🔍 TEST MODE")
    elif st.session_state.selected_model:
        st.info(f"🤖 {st.session_state.selected_model.split('-')[2].title()}")

with status_col2:
    if st.session_state.excluded_terms:
        st.info(f"🚫 {len(st.session_state.excluded_terms)} excluded")
    
with status_col3:
    if st.session_state.example_copies:
        st.info(f"📄 {len(st.session_state.example_copies)} examples")

with status_col4:
    if st.session_state.target_keywords:
        st.info(f"🎯 {len(st.session_state.target_keywords)} keywords")

# Generation controls
if st.session_state.df is not None:
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        if st.button("🚀 Generate All Descriptions", type="primary", use_container_width=True):
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
    
    with col2:
        if st.session_state.generated_content:
            # Check for excluded terms
            if st.button("🔍 Check Excluded Terms", use_container_width=True):
                found_terms = {}
                for idx, row in st.session_state.df.iterrows():
                    content = st.session_state.generated_content.get(idx, '')
                    if content and isinstance(content, str):
                        property_name = row.get('Property Name', f'Property #{idx}')
                        found_in_this_property = []
                        
                        for term in st.session_state.excluded_terms:
                            if term.lower() in content.lower():
                                found_in_this_property.append(term)
                        
                        if found_in_this_property:
                            found_terms[property_name] = found_in_this_property
                
                if found_terms:
                    st.error("Found excluded terms:")
                    for property_name, terms in found_terms.items():
                        st.markdown(f"**{property_name}**: {', '.join(terms)}")
                else:
                    st.success("✅ No excluded terms found!")
    
    with col3:
        if st.session_state.generated_content:
            # Export options
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                export_format = st.radio("Format:", ("CSV", "Excel"), horizontal=True)
            with export_col2:
                include_seo = st.checkbox("Include SEO data", value=True)
            
            if st.download_button(
                label=f"📥 Download {export_format}",
                data=export_data(st.session_state.df, export_format.lower(), include_seo),
                file_name=f"office_descriptions_seo_{datetime.now().strftime('%Y%m%d_%H%M')}.{export_format.lower()}",
                mime="application/octet-stream",
                use_container_width=True
            ):
                st.success(f"Downloaded {export_format} file!")
                add_debug(f"Exported data as {export_format} with SEO: {include_seo}")

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
                        
                        # Generate and store meta description
                        meta_desc = generate_meta_description(property_data, content)
                        st.session_state.meta_descriptions[idx] = meta_desc
                        
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
    status_text.text(f"✅ Generated descriptions for {total_properties} properties!")
    st.session_state.is_generating = False
    add_debug(f"Completed batch generation of {total_properties} properties")
    st.rerun()

# Display properties and generated content
if st.session_state.df is not None:
    st.subheader("Property Descriptions")
    
    # Add tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Content Editor", "📊 SEO Overview", "🔧 Schema Generator"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Properties")
            # Search filter
            search_term = st.text_input("🔍 Search properties:", "")
            
            # Filter and display properties
            for idx, row in st.session_state.df.iterrows():
                property_name = row.get('Property Name', f'Property #{idx}')
                if search_term.lower() in property_name.lower() or not search_term:
                    button_type = "primary" if idx == st.session_state.selected_property else "secondary"
                    if st.button(property_name, key=f"prop_{idx}", type=button_type):
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
                neighborhood = property_data.get('Neighborhood', 'N/A')
                zip_code = property_data.get('Zip Code', 'N/A')
                
                # Property info card
                with st.container():
                    st.info(f"**Property:** {property_name}\n\n**Location:** {neighborhood}, {city} {zip_code}")
                
                # Display or generate content for selected property
                if idx in st.session_state.generated_content:
                    content = st.session_state.generated_content[idx]
                    
                    # Safety check to ensure content is a string
                    if content is not None and isinstance(content, str) and content.strip():
                        # Clean up the content to ensure proper markdown rendering
                        cleaned_content = content.replace('\\n', '\n').replace('\\#', '#').replace('\\*', '*').replace('\\-', '-')
                        
                        # Display content with SEO score
                        seo_analysis = analyze_seo_quality(cleaned_content, property_data)
                        
                        score_col1, score_col2, score_col3 = st.columns([1, 1, 2])
                        with score_col1:
                            score_color = "🟢" if seo_analysis['seo_score'] >= 80 else "🟡" if seo_analysis['seo_score'] >= 60 else "🔴"
                            st.metric("SEO Score", f"{score_color} {seo_analysis['seo_score']}%")
                        with score_col2:
                            wc_color = "🟢" if 150 <= seo_analysis['word_count'] <= 300 else "🟡"
                            st.metric("Word Count", f"{wc_color} {seo_analysis['word_count']}")
                        
                        # Display content
                        st.markdown("### Preview")
                        st.markdown(cleaned_content)
                        
                        # SEO Analysis Expander
                        with st.expander("📊 SEO Analysis", expanded=False):
                            anal_col1, anal_col2 = st.columns(2)
                            
                            with anal_col1:
                                st.markdown("**Content Checks:**")
                                checks = {
                                    "Has H1 Title": "✅" if seo_analysis['has_h1'] else "❌",
                                    "Includes Address": "✅" if seo_analysis['has_address'] else "❌",
                                    "Has Call-to-Action": "✅" if seo_analysis['has_cta'] else "❌",
                                    "Readability": f"{'✅' if seo_analysis['readability_score'] == 'Good' else '⚠️'} {seo_analysis['readability_score']}",
                                    "Location Mentions": f"{'✅' if seo_analysis['location_mentions'] >= 2 else '⚠️'} {seo_analysis['location_mentions']} times"
                                }
                                for check, result in checks.items():
                                    st.text(f"{check}: {result}")
                            
                            with anal_col2:
                                st.markdown("**Keyword Density:**")
                                for keyword, data in seo_analysis['keyword_density'].items():
                                    if data['count'] > 0 and keyword:
                                        st.text(f"{keyword}: {data['count']}x ({data['density']})")
                            
                            # Meta description
                            st.markdown("**Meta Description:**")
                            meta_desc = st.session_state.meta_descriptions.get(idx, generate_meta_description(property_data, cleaned_content))
                            meta_text = st.text_area("", value=meta_desc, height=80, key=f"meta_{idx}")
                            st.caption(f"Length: {len(meta_text)}/160 characters {'✅' if len(meta_text) <= 160 else '⚠️'}")
                            
                            if meta_text != meta_desc:
                                if st.button("Save Meta Description", key=f"save_meta_{idx}"):
                                    st.session_state.meta_descriptions[idx] = meta_text
                                    st.success("Meta description saved!")
                        
                        # Action buttons
                        act_col1, act_col2 = st.columns(2)
                        with act_col1:
                            if st.button("🔄 Regenerate", key=f"regen_{idx}", use_container_width=True):
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
                                            
                                            # Regenerate meta description
                                            meta_desc = generate_meta_description(property_data, new_content)
                                            st.session_state.meta_descriptions[idx] = meta_desc
                                            
                                            st.success("Content regenerated successfully!")
                                            add_debug(f"Regenerated content for {property_name} successfully")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error regenerating content: {str(e)}")
                                            add_debug(f"Error during regeneration: {str(e)}")
                        
                        with act_col2:
                            # Copy to clipboard functionality
                            if st.button("📋 Copy Content", key=f"copy_{idx}", use_container_width=True):
                                st.info("Content copied to editor below")
                        
                        # Edit content
                        st.markdown("### Edit Content")
                        edited_content = st.text_area("", value=cleaned_content, height=400, key=f"edit_{idx}")
                        
                        if edited_content != cleaned_content:
                            if st.button("💾 Save Edits", key=f"save_{idx}", type="primary", use_container_width=True):
                                st.session_state.generated_content[idx] = edited_content
                                st.session_state.df.at[idx, 'Generated Content'] = edited_content
                                # Update meta description
                                meta_desc = generate_meta_description(property_data, edited_content)
                                st.session_state.meta_descriptions[idx] = meta_desc
                                st.success("Changes saved!")
                                add_debug(f"Saved edited content for {property_name}")
                                st.rerun()
                    else:
                        st.error("Content appears to be empty or invalid. Please try regenerating.")
                        add_debug(f"Empty or invalid content for {property_name}")
                        
                else:
                    st.info("No content generated yet. Click the button below to generate content.")
                    
                    if st.button("✨ Generate Description", key=f"gen_{idx}", type="primary", use_container_width=True):
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
                                    
                                    # Generate meta description
                                    meta_desc = generate_meta_description(property_data, content)
                                    st.session_state.meta_descriptions[idx] = meta_desc
                                    
                                    st.success("Content generated successfully!")
                                    add_debug(f"Generated content for {property_name} successfully")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error generating content: {str(e)}")
                                    add_debug(f"Error during generation: {str(e)}")
    
    with tab2:
        st.subheader("SEO Overview")
        
        if st.session_state.generated_content:
            # Calculate overall statistics
            total_generated = len(st.session_state.generated_content)
            seo_scores = []
            word_counts = []
            has_cta_count = 0
            has_address_count = 0
            
            for idx, content in st.session_state.generated_content.items():
                if content and isinstance(content, str):
                    property_data = st.session_state.df.iloc[idx].to_dict()
                    analysis = analyze_seo_quality(content, property_data)
                    seo_scores.append(analysis['seo_score'])
                    word_counts.append(analysis['word_count'])
                    if analysis['has_cta']:
                        has_cta_count += 1
                    if analysis['has_address']:
                        has_address_count += 1
            
            # Display overview metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                avg_seo_score = sum(seo_scores) / len(seo_scores) if seo_scores else 0
                st.metric("Average SEO Score", f"{avg_seo_score:.0f}%")
            
            with metric_col2:
                avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
                st.metric("Average Word Count", f"{avg_word_count:.0f}")
            
            with metric_col3:
                cta_percentage = (has_cta_count / total_generated * 100) if total_generated > 0 else 0
                st.metric("Has Call-to-Action", f"{cta_percentage:.0f}%")
            
            with metric_col4:
                address_percentage = (has_address_count / total_generated * 100) if total_generated > 0 else 0
                st.metric("Includes Address", f"{address_percentage:.0f}%")
            
            # Detailed table
            st.markdown("### Property SEO Scores")
            
            # Create summary dataframe
            summary_data = []
            for idx, row in st.session_state.df.iterrows():
                if idx in st.session_state.generated_content:
                    content = st.session_state.generated_content[idx]
                    if content and isinstance(content, str):
                        property_data = row.to_dict()
                        analysis = analyze_seo_quality(content, property_data)
                        
                        summary_data.append({
                            'Property': property_data.get('Property Name', f'Property #{idx}'),
                            'City': property_data.get('City', 'N/A'),
                            'SEO Score': f"{analysis['seo_score']}%",
                            'Words': analysis['word_count'],
                            'Location Mentions': analysis['location_mentions'],
                            'Has CTA': '✅' if analysis['has_cta'] else '❌',
                            'Has Address': '✅' if analysis['has_address'] else '❌',
                            'Readability': analysis['readability_score']
                        })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Download summary
                csv = summary_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download SEO Summary",
                    csv,
                    "seo_summary.csv",
                    "text/csv",
                    key='download-seo-summary'
                )
        else:
            st.info("Generate content first to see SEO overview")
    
    with tab3:
        st.subheader("Schema.org Structured Data Generator")
        
        if st.session_state.selected_property is not None:
            property_data = st.session_state.df.iloc[st.session_state.selected_property].to_dict()
            
            st.info(f"Generating schema for: **{property_data.get('Property Name', 'N/A')}**")
            
            # Generate schema
            schema = generate_schema_markup(property_data)
            
            # Display schema
            st.markdown("### Generated Schema Markup")
            st.code(schema, language='json')
            
            # Copy button
            if st.button("📋 Copy Schema", key="copy_schema"):
                st.success("Schema copied! Paste this into your website's <head> section wrapped in <script type='application/ld+json'> tags")
            
            # Instructions
            with st.expander("📚 How to Use Schema Markup"):
                st.markdown("""
                **What is Schema Markup?**
                Schema markup is structured data that helps search engines understand your content better, potentially leading to rich snippets in search results.
                
                **How to implement:**
                1. Copy the generated JSON-LD code above
                2. Paste it into your webpage's HTML
                3. Wrap it in script tags: `<script type="application/ld+json">{...}</script>`
                4. Place it in the <head> section of your HTML
                
                **Benefits:**
                - Enhanced search results with rich snippets
                - Better local SEO performance
                - Improved click-through rates
                - Clear information for search engines
                
                **Testing:**
                Use Google's Rich Results Test tool to validate your schema markup.
                """)
        else:
            st.info("Select a property to generate schema markup")

else:
    # No data loaded - show instructions
    st.info("📤 Please upload a CSV/Excel file or scrape property data from URLs in the sidebar")
    
    # Show quick start for URL scraping
    st.subheader("🚀 Quick Start: URL Scraping")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### How to use URL scraping:
        1. **Single URL**: Enter a property page URL and click "Scrape URL"
        2. **Multiple URLs**: Use bulk import for multiple properties
        3. **Review**: Check extracted data in the sidebar
        4. **Use Data**: Click "Use Scraped Data" to start generating content
        """)
    
    with col2:
        st.markdown("""
        ### Supported property data:
        - Property name and address
        - Location (city, state, zip)
        - Features and amenities
        - Building descriptions
        - Contact information
        - Transportation details
        """)
    
    # Sample data structure
    st.subheader("Expected Data Structure")
    sample_data = {
        "Property Name": ["Executive Tower", "Riverside Business Center"],
        "Address": ["100 Wall Street", "200 River Drive"],
        "City": ["New York", "Chicago"],
        "Zip Code": ["10005", "60601"],
        "Neighborhood": ["Financial District", "Loop"],
        "Property Type": ["Class A Office", "Premium Workspace"],
        "Size Range": ["1,000-25,000 sq ft", "500-10,000 sq ft"],
        "Key Features": ["24/7 access, Concierge, Fitness center", "River views, Valet parking, Rooftop deck"],
        "Building Description": ["40-story modern tower", "Boutique 10-story building"],
        "Nearby Businesses": ["NYSE, Goldman Sachs", "Boeing, United Airlines"],
        "Transport Access": ["Subway lines 4/5/6, PATH", "CTA Blue/Red lines"],
        "Meeting Rooms": ["10 conference rooms", "5 meeting rooms"],
        "Technology Features": ["Fiber internet, Smart building", "Gigabit ethernet, Video conferencing"],
        "Business Services": ["Reception, Mail handling", "Concierge, Printing center"],
        "Source URL": ["https://example.com/property1", "https://example.com/property2"]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True)
    
    # Download sample template
    st.download_button(
        label="📥 Download Sample Template",
        data=export_data(sample_df, "excel"),
        file_name="property_template_seo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    st.subheader("Batch Processing Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batch_size = st.slider("Batch Size", min_value=1, max_value=20, value=st.session_state.batch_size, 
                              help="Number of properties to process at once")
    
    with col2:
        delay = st.slider("API Delay (seconds)", min_value=0, max_value=10, value=st.session_state.api_delay, 
                         help="Delay between API calls to avoid rate limits")
    
    if st.button("Save Settings"):
        st.session_state.batch_size = batch_size
        st.session_state.api_delay = delay
        st.success("Settings saved!")
        add_debug(f"Updated settings: batch_size={batch_size}, delay={delay}s")
    
    # Export/Import settings
    st.markdown("---")
    st.subheader("Export/Import Settings")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        # Export all settings
        if st.button("📤 Export All Settings"):
            settings_data = {
                "excluded_terms": st.session_state.excluded_terms,
                "target_keywords": st.session_state.target_keywords,
                "example_copies": st.session_state.example_copies,
                "batch_size": st.session_state.batch_size,
                "api_delay": st.session_state.api_delay
            }
            settings_json = json.dumps(settings_data, indent=2)
            st.download_button(
                label="Download Settings JSON",
                data=settings_json,
                file_name="content_generator_settings.json",
                mime="application/json"
            )
    
    with settings_col2:
        # Import settings
        settings_file = st.file_uploader("Import Settings", type=['json'])
        if settings_file is not None:
            try:
                settings_data = json.loads(settings_file.getvalue())
                
                # Update session state
                if "excluded_terms" in settings_data:
                    st.session_state.excluded_terms = settings_data["excluded_terms"]
                if "target_keywords" in settings_data:
                    st.session_state.target_keywords = settings_data["target_keywords"]
                if "example_copies" in settings_data:
                    st.session_state.example_copies = settings_data["example_copies"]
                if "batch_size" in settings_data:
                    st.session_state.batch_size = settings_data["batch_size"]
                if "api_delay" in settings_data:
                    st.session_state.api_delay = settings_data["api_delay"]
                
                st.success("Settings imported successfully!")
                add_debug("Imported settings from file")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing settings: {str(e)}")

# Debug information (hidden by default)
with st.expander("🐛 Debug Information"):
    debug_col1, debug_col2 = st.columns([3, 1])
    
    with debug_col1:
        st.subheader("Debug Log")
    with debug_col2:
        if st.button("Clear Log"):
            st.session_state.debug_info = []
            st.rerun()
    
    # Display debug log
    for log in st.session_state.debug_info[-20:]:  # Show last 20 entries
        st.text(log)
    
    # Session state info
    st.subheader("Session State Summary")
    state_info = {
        "API Key Set": bool(st.session_state.api_key),
        "Model": st.session_state.selected_model,
        "Properties Loaded": len(st.session_state.df) if st.session_state.df is not None else 0,
        "Content Generated": len(st.session_state.generated_content),
        "Excluded Terms": len(st.session_state.excluded_terms),
        "Target Keywords": len(st.session_state.target_keywords),
        "Example Copies": len(st.session_state.example_copies)
    }
    
    for key, value in state_info.items():
        st.text(f"{key}: {value}")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 1])

with footer_col1:
    st.caption("🏢 Centre Page Content Generator v2.0 - SEO Enhanced")

with footer_col2:
    st.caption("Developed by MediaVision & Metis")

with footer_col3:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
