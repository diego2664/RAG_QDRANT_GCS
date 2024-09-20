from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

"""def get_embedding_function():
    embeddings = BedrockEmbeddings(
        credentials_profile_name="default", region_name="us-east-1"
    )
    # embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings"""

load_dotenv()


def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY") , model="text-embedding-3-large"
    )
    return embeddings