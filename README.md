# Multipage Streamlit RAG App using LangChain

This is a multipage Streamlit application that demonstrates Retrieval-Augmented Generation (RAG) using LangChain. The app has two main functionalities:

1. PDF Chat: Upload a PDF and ask questions about its content.
2. Qdrant Q&A: Ask questions using a pre-populated Qdrant vector database.

## Prerequisites

- Python 3.7+
- Qdrant running locally or accessible via network
- OpenAI API key

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Ensure Qdrant is running and accessible (default: localhost:6333)

## Running the Application

To run the Streamlit app, use the following command:

```
streamlit run ST_app_multipage.py
```

The application will open in your default web browser.

## Using the Application

### PDF Chat

1. Navigate to the "PDF Chat" page using the sidebar.
2. Upload a PDF file using the file uploader.
3. Once the PDF is processed, you can ask questions about its content in the text input field.
4. The app will display the answer based on the content of the PDF.

### Qdrant Q&A

1. Navigate to the "Qdrant Q&A" page using the sidebar.
2. Ensure that Qdrant is running and accessible.
3. If the connection is successful, you can ask questions in the text input field.
4. The app will retrieve relevant information from the Qdrant database and generate an answer.

## Note

Make sure to populate the Qdrant database with relevant documents before using the Qdrant Q&A functionality. The current implementation assumes that a collection named "my_documents" exists in the Qdrant database.

## Troubleshooting

- If you encounter any issues with OpenAI API, make sure your API key is correctly set in the `.env` file.
- If the Qdrant Q&A page shows a connection error, ensure that Qdrant is running and accessible at the specified address (default: localhost:6333).

For any other issues or questions, please refer to the documentation of the used libraries (Streamlit, LangChain, Qdrant) or create an issue in this repository.
