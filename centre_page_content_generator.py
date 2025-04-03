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
    
    # Initialize excluded_terms if not exists
    if 'excluded_terms' not in st.session_state:
        st.session_state.excluded_terms = []
    
    # Add term input
    new_term = st.text_input("Add term or phrase to exclude:")
    if st.button("Add Term") and new_term.strip():
        term = new_term.strip()
        if term not in st.session_state.excluded_terms:
            st.session_state.excluded_terms.append(term)
            add_debug(f"Added excluded term: '{term}'")
            st.success(f"Added: '{term}'")
            st.experimental_rerun()
    
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
                    st.experimental_rerun()
    
    # Add horizontal line
    st.markdown("---")
    
    # Example Content section
    st.subheader("Example Content")
    
    # Initialize example_copies if not exists
    if 'example_copies' not in st.session_state:
        st.session_state.example_copies = []
    
    # Upload example copy file
    uploaded_example = st.file_uploader("Upload Example Copy", type=['txt'])
    if uploaded_example is not None:
        try:
            content = uploaded_example.getvalue().decode("utf-8")
            if content and content.strip():
                st.session_state.example_copies.append(content.strip())
                add_debug(f"Added example from file: {uploaded_example.name} ({len(content)} chars)")
                st.success(f"Added example from: {uploaded_example.name}")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error loading example file: {str(e)}")
            add_debug(f"Error loading example file: {str(e)}")
    
    # Example copy text area
    example_text = st.text_area("Or paste example copy here:", height=150)
    if st.button("Add Example") and example_text.strip():
        st.session_state.example_copies.append(example_text.strip())
        add_debug(f"Added example copy ({len(example_text)} chars)")
        st.success("Example added!")
        st.experimental_rerun()
    
    # Display existing examples
    if st.session_state.example_copies:
        st.write(f"{len(st.session_state.example_copies)} examples loaded")
        with st.expander("View/Edit Examples"):
            for i, example in enumerate(st.session_state.example_copies):
                st.text(f"Example #{i+1} ({len(example)} chars)")
                if st.button("Remove", key=f"del_example_{i}"):
                    st.session_state.example_copies.pop(i)
                    add_debug(f"Removed example #{i+1}")
                    st.experimental_rerun()
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
    if 'df' in st.session_state and st.session_state.df is not None:
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
                st.experimental_rerun()
        
        if 'generated_content' in st.session_state and st.session_state.generated_content:
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
