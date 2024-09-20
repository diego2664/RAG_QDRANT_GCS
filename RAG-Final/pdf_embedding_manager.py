import os
from google.cloud import storage
from gcs_utils import GCS_BUCKET_NAME, get_file_info
from pdf_utils import extract_text_from_pdf
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

# Function to get the current list of PDF files in the bucket
def get_pdf_files_in_bucket():
    files = get_file_info(GCS_BUCKET_NAME)
    return [file['name'] for file in files if file['name'].lower().endswith('.pdf')]

# Function to load the list of processed files
def load_processed_files():
    try:
        with open('processed_files.txt', 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

# Function to save the list of processed files
def save_processed_files(processed_files):
    with open('processed_files.txt', 'w') as f:
        for file in processed_files:
            f.write(f"{file}\n")

# Main function to process PDF files and update the vector database
def update_pdf_embeddings():
    # Get current PDF files in the bucket
    current_files = set(get_pdf_files_in_bucket())
    
    # Load previously processed files
    processed_files = load_processed_files()
    
    # Identify new and deleted files
    new_files = current_files - processed_files
    deleted_files = processed_files - current_files
    
    try:
        # Initialize LangChain embedding model
        embeddings = OpenAIEmbeddings()
        
        # Initialize or load FAISS index
        if os.path.exists("faiss_index"):
            vector_store = FAISS.load_local("faiss_index", embeddings)
        else:
            vector_store = FAISS.from_texts([""], embeddings)
        
        # Process new files
        for file in new_files:
            # Download PDF file from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(file)
            pdf_content = blob.download_as_bytes()
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_content)
            
            # Split text into chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            chunks = text_splitter.split_text(text)
            
            # Add chunks to vector store
            vector_store.add_texts(chunks, metadatas=[{"file_name": file} for _ in chunks])
            
            processed_files.add(file)
        
        # Remove deleted files from the vector store
        for file in deleted_files:
            # Note: FAISS doesn't support direct deletion, so we'll need to rebuild the index
            # This is a simplification and might not be efficient for large datasets
            docs = vector_store.similarity_search("", filter={"file_name": {"$ne": file}})
            vector_store = FAISS.from_documents(docs, embeddings)
            processed_files.remove(file)
        
        # Save updated FAISS index
        vector_store.save_local("faiss_index")
        
        # Save updated list of processed files
        save_processed_files(processed_files)
        
        return len(new_files), len(deleted_files)
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

if __name__ == "__main__":
    new_count, deleted_count = update_pdf_embeddings()
    print(f"Processed {new_count} new files and removed {deleted_count} deleted files.")