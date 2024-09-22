import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant

load_dotenv()

def main():
    st.set_page_config(page_title="RAG Multipage App")
    st.title("RAG Multipage App")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["PDF Chat", "Qdrant Q&A"])

    if page == "PDF Chat":
        pdf_chat_page()
    elif page == "Qdrant Q&A":
        qdrant_qa_page()

def pdf_chat_page():
    st.header("Chat with your PDF 💬")
    
    # Initialize session state for knowledge base
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None

    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    
    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # create embeddings
        embeddings = OpenAIEmbeddings()
        st.session_state.knowledge_base = FAISS.from_texts(chunks, embeddings)
        
        st.success("PDF processed and ready for questions!")
    
    # show user input
    user_question = st.text_input("Ask a question about your PDF:")
    if user_question and st.session_state.knowledge_base is not None:
        docs = st.session_state.knowledge_base.similarity_search(user_question)
        
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_question)
            print(cb)
        
        st.write("Answer:", response)
    elif user_question:
        st.warning("Please upload a PDF first.")

def qdrant_qa_page():
    st.header("Qdrant-based Q&A 🗃️")
    
    # Mostrar los valores de las variables de entorno (solo para depuración)
    st.write("QDRANT_URL:", os.getenv("QDRANT_URL"))
    st.write("QDRANT_COLLECTION_NAME2:", os.getenv("QDRANT_COLLECTION_NAME2"))
    
    try:
        # Initialize Qdrant client
        qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"), 
            api_key=os.getenv("QDRANT_API_KEY"),
        )

        # Verificar si la colección existe
        collection_name = os.getenv("QDRANT_COLLECTION_NAME2")
        collections = qdrant_client.get_collections()
        if collection_name not in [c.name for c in collections.collections]:
            st.error(f"La colección '{collection_name}' no existe en Qdrant.")
            st.info("Por favor, verifica el nombre de la colección en tus variables de entorno.")
            return

        # Initialize embeddings
        embeddings = OpenAIEmbeddings()
        
        # Create Qdrant vector store
        vectorstore = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embeddings
        )
        st.success("Conectado a Qdrant exitosamente!")
        
        # User input
        user_question = st.text_input("Ask a question:")
        if user_question:
            # Perform similarity search
            docs = vectorstore.similarity_search(user_question)
            
            # Generate answer
            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=user_question)
                print(cb)
            
            st.write("Answer:", response)
    except Exception as e:
        st.error(f"Error al conectar con Qdrant: {str(e)}")
        st.info("Por favor, asegúrate de que Qdrant esté funcionando y sea accesible.")
        st.info("Verifica también que las variables de entorno QDRANT_URL y QDRANT_COLLECTION_NAME_2 estén correctamente configuradas.")

if __name__ == '__main__':
    main()
