import openai
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


# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# Function to generate embeddings using OpenAI API
def generate_embeddings(text_chunks):
    embeddings = []
    for chunk in text_chunks:
        response = openai.Embedding.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embeddings.append(response['data'][0]['embedding'])
    return embeddings
