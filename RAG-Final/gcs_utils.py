from google.cloud import storage
import os
from dotenv import load_dotenv
import PyPDF2
import io

load_dotenv()

# Environment variables
GCS_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_PROJECT_NAME = os.getenv("GCP_PROJECT_NAME")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION')
VERTEX_AI_INDEX_ID = os.getenv('VERTEX_AI_INDEX_ID')

# Initialize GCS client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCS_CREDENTIALS
storage_client = storage.Client(project=GCP_PROJECT_NAME)

def get_gcs_client():
    """Get the Google Cloud Storage client, assuming credentials are set in the environment."""
    return storage.Client()

def upload_to_gcs(bucket_name, file, file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(file)
    return f"gs://{bucket_name}/{file_name}"

def list_gcs_files(bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs]

def list_files_in_bucket(bucket_name):
    """List all files in the specified GCS bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob for blob in blobs]

def delete_file_from_gcs(bucket_name, file_name):
    """Delete a file from Google Cloud Storage."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.delete()
    print(f"Deleted {file_name} from {bucket_name}")

def get_file_size(blob):
    """Get the size of a file in GCS."""
    return blob.size

def get_pdf_pages(blob):
    """Get the number of pages in a PDF file stored in GCS."""
    if blob.name.lower().endswith('.pdf'):
        content = blob.download_as_bytes()
        pdf_file = io.BytesIO(content)
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return len(pdf_reader.pages)
        except:
            return "N/A"
    return "N/A"

def get_file_info(bucket_name):
    """Get information about all files in the bucket."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    
    file_info = []
    for blob in blobs:
        info = {
            "name": blob.name,
            "size": get_file_size(blob),
            "pages": get_pdf_pages(blob)
        }
        file_info.append(info)
    
    return file_info

def download_file_from_gcs(bucket_name, file_name):
    """Download a file from Google Cloud Storage."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.download_as_bytes()

def rename_file_in_gcs(bucket_name, old_name, new_name):
    """Rename a file in Google Cloud Storage."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(old_name)
    new_blob = bucket.rename_blob(blob, new_name)
    return f"File {old_name} renamed to {new_name}"