import streamlit as st
from gcs_utils import list_files_in_bucket, upload_to_gcs, delete_file_from_gcs
from dotenv import load_dotenv
import os
from google.cloud import storage

# Load environment variables
load_dotenv()

# Environment variables
GCS_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_PROJECT_NAME = os.getenv("GCP_PROJECT_NAME")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION')
VERTEX_AI_INDEX_ID = os.getenv('VERTEX_AI_INDEX_ID')

if 'trigger' not in st.session_state:
    st.session_state['trigger'] = False

def update_trigger():
    st.session_state['trigger'] = not st.session_state['trigger']

# Initialize the Google Cloud Storage client
storage_client = storage.Client.from_service_account_json(GCS_CREDENTIALS)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ["File Upload", "File Manager"])

def file_upload_page():
    st.title("File Upload")
    uploaded_files = st.file_uploader("Upload new PDF files", accept_multiple_files=True, type="pdf")
    if uploaded_files:
        st.write(f"Ready to upload {len(uploaded_files)} files...")
        if st.button("Confirm Upload"):
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                upload_to_gcs(GCS_BUCKET_NAME, uploaded_file, file_name)
            st.success("Files successfully uploaded to the bucket.")
            update_trigger()  # Rerun the app to refresh the file list

def file_manager_page():
    st.title("File Manager")
    st.header("Files in Bucket")
    if 'existing_files' not in st.session_state:
        st.session_state.existing_files = list_files_in_bucket(GCS_BUCKET_NAME)

    if st.session_state.existing_files:
        for file_name in st.session_state.existing_files:
            st.write(file_name)
            # Add an option to delete files
            if st.button(f"Delete {file_name}"):
                delete_file_from_gcs(GCS_BUCKET_NAME, file_name)
                st.session_state.existing_files = list_files_in_bucket(GCS_BUCKET_NAME)  # Update the file list
                update_trigger()  # Rerun the app to refresh the file list
    else:
        st.write("No files found in the bucket.")

    # Add a button to refresh the file list manually
    if st.button("Refresh File List"):
        st.session_state.existing_files = list_files_in_bucket(GCS_BUCKET_NAME)
        update_trigger()

# Display the selected page
if page == "File Upload":
    file_upload_page()
elif page == "File Manager":
    file_manager_page()
    