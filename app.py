import streamlit as st
import os
from markitdown import MarkItDown
from io import BytesIO

# Initialize MarkItDown Engine
mid = MarkItDown()

# Page Configuration
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄")

st.title("📄 Universal Document Reader")
st.markdown("Convert Office docs, PDFs, and HTML into clean Markdown instantly.")

# [2] Upload Area (Supports multiple files)
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'txt'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        try:
            # MarkItDown requires a file path or a stream
            # We save to a temporary location to ensure full compatibility
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # [1] The Engine Processing
            # [3] Resilience: Implementation of timeout logic handled by MarkItDown internally 
            # for web-based HTML docs.
            result = mid.convert(uploaded_file.name)
            md_content = result.text_content

            # [2] Instant Preview
            with st.expander(f"👁️ Preview: {uploaded_file.name}", expanded=True):
                st.text_area("Content", value=md_content, height=300, key=f"text_{uploaded_file.name}")
                
                # [2] Download Options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="Download as .md",
                        data=md_content,
                        file_name=f"{base_name}_converted.md",
                        mime="text/markdown",
                        key=f"md_{uploaded_file.name}"
                    )
                
                with col2:
                    st.download_button(
                        label="Download as .txt",
                        data=md_content,
                        file_name=f"{base_name}_converted.txt",
                        mime="text/plain",
                        key=f"txt_{uploaded_file.name}"
                    )

            # Cleanup temp file
            os.remove(uploaded_file.name)

        except Exception as e:
            # [3] Error Handling
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
            # Optional: Log the specific error for debugging
            # st.write(f"Debug Info: {e}")

st.divider()
st.caption("Powered by Microsoft MarkItDown & Streamlit")
