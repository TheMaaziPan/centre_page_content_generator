# Example Copies section for sidebar
st.divider()
st.subheader("Example Content")

# Initialize example_copies if not exists
if 'example_copies' not in st.session_state:
    st.session_state.example_copies = []

# Upload example copy file
uploaded_example = st.file_uploader("Upload Example Copy", type=['txt'], key="example_upload")
if uploaded_example is not None:
    try:
        content = uploaded_example.getvalue().decode("utf-8")
        if content and content.strip():
            st.session_state.example_copies.append(content.strip())
            add_debug(f"Added example from file: {uploaded_example.name} ({len(content)} chars)")
            st.success(f"Added example from: {uploaded_example.name}")
    except Exception as e:
        st.error(f"Error loading example file: {str(e)}")
        add_debug(f"Error loading example file: {str(e)}")

# Example copy text area
st.text_area("Or paste example copy here:", key="new_example_copy", height=150)

# Add example button - we use this approach instead of on_change
if st.button("Add Example"):
    if 'new_example_copy' in st.session_state and st.session_state.new_example_copy.strip():
        example = st.session_state.new_example_copy.strip()
        st.session_state.example_copies.append(example)
        add_debug(f"Added example copy ({len(example)} chars)")
        st.session_state.new_example_copy = ""
        st.success("Example added successfully!")
        st.experimental_rerun()

# Display existing examples
if st.session_state.example_copies:
    st.write(f"{len(st.session_state.example_copies)} examples loaded")
    show_examples = st.expander("View/Edit Examples")
    with show_examples:
        for i, example in enumerate(st.session_state.example_copies):
            st.text(f"Example #{i+1} ({len(example)} chars)")
            if st.button("Remove", key=f"del_example_{i}"):
                if i < len(st.session_state.example_copies):
                    st.session_state.example_copies.pop(i)
                    add_debug(f"Removed example #{i+1}")
                    st.experimental_rerun()
            st.text_area(f"Example #{i+1}", value=example, height=100, key=f"example_{i}")
