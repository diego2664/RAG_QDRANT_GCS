import streamlit as st
import pandas as pd
from gcs_utils import get_file_info, upload_to_gcs, delete_file_from_gcs, rename_file_in_gcs, download_file_from_gcs, GCS_BUCKET_NAME
from pdf_embedding_manager import update_pdf_embeddings

st.set_page_config(layout="wide")
st.title("GCS File Manager")

# Get file information
files = get_file_info(GCS_BUCKET_NAME)

# Convert file information to DataFrame
df = pd.DataFrame(files)

# Display number of documents
st.metric("Documents in Bucket", len(df))

# Display DataFrame
st.dataframe(df, use_container_width=True)

# Multiple selection widget
selected_files = st.multiselect("Select files for actions", df['name'].tolist())

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Delete Selected"):
        for file in selected_files:
            delete_file_from_gcs(GCS_BUCKET_NAME, file)
        st.success(f"Deleted {len(selected_files)} file(s)")
        st.rerun()

with col2:
    if st.button("Rename Selected"):
        for file in selected_files:
            new_name = st.text_input(f"Enter new name for {file}", value=file)
            if st.button(f"Confirm Rename for {file}"):
                rename_file_in_gcs(GCS_BUCKET_NAME, file, new_name)
                st.success(f"Renamed {file} to {new_name}")
        st.rerun()

with col3:
    if st.button("Download Selected"):
        for file in selected_files:
            file_content = download_file_from_gcs(GCS_BUCKET_NAME, file)
            st.download_button(
                label=f"Download {file}",
                data=file_content,
                file_name=file,
                mime="application/octet-stream"
            )

# Upload new file
st.header("Upload New File")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    if st.button("Upload to GCS"):
        file_path = upload_to_gcs(GCS_BUCKET_NAME, uploaded_file, uploaded_file.name)
        st.success(f"File uploaded successfully to {file_path}")
        st.rerun()

if st.button("Refresh"):
    st.rerun()

# Add button for updating PDF embeddings
st.header("Update PDF Embeddings")
if st.button("Update PDF Embeddings"):
    with st.spinner("Updating PDF embeddings..."):
        new_count, deleted_count = update_pdf_embeddings()
    st.success(f"Processed {new_count} new files and removed {deleted_count} deleted files.")

st.markdown("*Note: This app now uses `st.rerun()` instead of `st.experimental_rerun()` for better performance and compatibility with newer Streamlit versions.*")