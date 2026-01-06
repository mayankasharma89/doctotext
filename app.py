import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# Initialize Engine
mid = MarkItDown()

def format_size(bytes_size):
    """Convert bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

st.set_page_config(page_title="Universal Doc Converter", page_icon="📄")
st.title("📄 Universal Document Reader")

uploaded_files = st.file_uploader(
    "Upload Word, Excel, PPTX, PDF, or HTML", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'txt'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1]
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # Get Original Size
        original_size = uploaded_file.size
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            # Process the file
            result = mid.convert(tmp_path)
            md_content = result.text_content
            
            # Calculate Converted Size
            converted_size = len(md_content.encode('utf-8'))
            
            # Calculate Reduction Percentage
            if original_size > 0:
                reduction = ((original_size - converted_size) / original_size) * 100
            else:
                reduction = 0

            st.write(f"### File: {uploaded_file.name}")
            
            # Create Tabs
            tab1, tab2 = st.tabs(["📄 Preview & Download", "📊 File Size Comparison"])

            with tab1:
                st.text_area("Content", value=md_content, height=300, key=f"text_{uploaded_file.name}")
                c1, c2 = st.columns(2)
                c1.download_button("Download .md", md_content, f"{base_name}.md", "text/markdown", key=f"m_{uploaded_file.name}")
                c2.download_button("Download .txt", md_content, f"{base_name}.txt", "text/plain", key=f"t_{uploaded_file.name}")

            with tab2:
                # Create the comparison table
                data = {
                    "Metric": ["Original File Size", "Converted Text Size"],
                    "Size": [format_size(original_size), format_size(converted_size)]
                }
                st.table(data)
                
                # Show percentage highlight
                if reduction > 0:
                    st.success(f"✨ Text version is **{reduction:.1f}% smaller** than the original.")
                else:
                    st.info("The text version is roughly the same size as the original.")

            # Cleanup
            os.remove(tmp_path)

        except Exception as e:
            st.error(f"⚠️ Could not read {uploaded_file.name}. Error: {str(e)}")

st.caption("Powered by MarkItDown[all]")
