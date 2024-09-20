import io
from PyPDF2 import PdfReader
from gcs_utils import storage_client
import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables
GCS_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_PROJECT_NAME = os.getenv("GCP_PROJECT_NAME")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION')
VERTEX_AI_INDEX_ID = os.getenv('VERTEX_AI_INDEX_ID')


def extract_text_from_pdf(gcs_file_path):
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_file_path)

    pdf_content = blob.download_as_bytes()
    pdf_file = io.BytesIO(pdf_content)

    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return text

def chunk_text(text, chunk_size=500):
    text_chunks = []
    for i in range(0, len(text), chunk_size):
        text_chunks.append(text[i:i + chunk_size])
    return text_chunks
