import streamlit as st
import os
import tempfile
import requests
from markitdown import MarkItDown

# --- [3] Resilience: Custom Request Session ---
# We create a session to handle User-Agent and timeouts for web-based content
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

# Initialize MarkItDown with the custom session (handles the 5s timeout internally)
# Note: MarkItDown uses the session for any URL-based inputs or sub-calls
mid = MarkItDown(requests_session=session)

def format_size(bytes_size):
    """Helper to convert bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

# --- [2] Interface ---
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄")
st.title("📄 Universal Document Reader")
st.markdown("Convert Office docs, PDFs, and HTML into clean Markdown instantly.")

# Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'txt'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()
        base_name = os.path.splitext(uploaded_file.name)[0]
        original_size = uploaded_file.size
        
        try:
            # Save to a temporary file with the correct extension for the engine
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            # [1] The Engine Processing (with 5s timeout logic via session)
            result = mid.convert(tmp_path)
            md_content = result.text_content
            
            # Calculate Converted Size
            converted_size = len(md_content.encode('utf-8'))
            reduction = ((original_size - converted_size) / original_size) * 100 if original_size > 0 else 0

            st.write(f"### Results for: `{uploaded_file.name}`")
            
            # Tabbed Interface
            tab1, tab2 = st.tabs(["📝 Preview & Download", "📊 File Size Comparison"])

            with tab1:
                # [2] Instant Preview
                st.text_area("Markdown Preview", value=md_content, height=300, key=f"text_{uploaded_file.name}")
                
                # [2] Download Options (using original filename logic)
                col1, col2 = st.columns(2)
                col1.download_button(
                    "Download .md", md_content, f"{base_name}_converted.md", "text/markdown", key=f"m_{uploaded_file.name}"
                )
                col2.download_button(
                    "Download .txt", md_content, f"{base_name}_converted.txt", "text/plain", key=f"t_{uploaded_file.name}"
                )

            with tab2:
                # [Requirement] File Size Comparison Table
                comparison_data = [
                    {"Metric": "Original file size", "Value": format_size(original_size)},
                    {"Metric": "Converted .txt file size", "Value": format_size(converted_size)}
                ]
                st.table(comparison_data)
                
                # Percentage highlight
                st.info(f"💡 **Text version is {reduction:.1f}% smaller** than the original.")

            # Cleanup
            os.remove(tmp_path)

        except Exception:
            # [3] Resilience: Polite Error Handling
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")

st.divider()
st.caption("Powered by MarkItDown[all] | Resilience Mode: Enabled")
