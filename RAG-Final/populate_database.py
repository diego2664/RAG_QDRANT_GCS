import argparse
import os
import tempfile
from google.cloud import storage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from vertex_ai_retriever import VertexAIRetriever
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()


BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")  # Replace with your actual bucket name
INDEX_ID = os.getenv('VERTEX_AI_INDEX_ID')  # Replace with your actual Vertex AI Vector Index ID
PROJECT_ID = os.getenv("GCP_PROJECT_NAME")  # Replace with your actual Google Cloud project ID
LOCATION = os.getenv("VERTEX_AI_LOCATION")  # Replace with your actual location

def main():
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_vertex(chunks)

def load_documents():
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()
    
    documents = []
    for blob in blobs:
        if blob.name.lower().endswith('.pdf'):
            print(f"Processing {blob.name}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                blob.download_to_filename(temp_file.name)
                loader = PyPDFLoader(temp_file.name)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = blob.name  # Set the source to the GCS blob name
                documents.extend(docs)
            os.unlink(temp_file.name)  # Delete the temporary file
    
    return documents

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_vertex(chunks: list[Document]):
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=LOCATION)

    # Create a VertexAIRetriever instance
    retriever = VertexAIRetriever(
        project_id=PROJECT_ID,
        location=LOCATION,
        index_id=INDEX_ID
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents
    print(f"Adding/Updating documents in Vertex AI Vector Index")
    
    for chunk in chunks_with_ids:
        # Convert the chunk to the format expected by Vertex AI
        vertex_document = {
            "id": chunk.metadata["id"],
            "content": chunk.page_content,
            "metadata": chunk.metadata
        }
        
        # Upsert the document to the Vertex AI Vector Index
        retriever.upsert_document(vertex_document)

    print("✅ Documents added/updated in Vertex AI Vector Index")

def calculate_chunk_ids(chunks):
    # This will create IDs like "gs://bucket-name/file.pdf:6:2"
    # GCS Object : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"gs://{BUCKET_NAME}/{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database():
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=LOCATION)

    # Create a VertexAIRetriever instance
    retriever = VertexAIRetriever(
        project_id=PROJECT_ID,
        location=LOCATION,
        index_id=INDEX_ID
    )

    # Clear all documents from the index
    retriever.clear_index()
    print("✅ Vertex AI Vector Index cleared")

if __name__ == "__main__":
    main()
