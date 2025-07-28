import logging
from fastapi import HTTPException, status
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.clients import azure_llm, azure_embedder
from app.core.config import settings
from app.schemas.chat import ChatResponse, Source

class RAGService:
    def __init__(self):
        self.llm = azure_llm
        self.embedder = azure_embedder
        self.index_name = settings.AZURE_AI_SEARCH_INDEX_NAME
        
        try:
            self.vector_store = AzureSearch(
                azure_search_endpoint=settings.AZURE_AI_SEARCH_ENDPOINT,
                azure_search_key=settings.AZURE_AI_SEARCH_KEY,
                index_name=self.index_name,
                embedding_function=self.embedder.embed_query,
            )
            self.retriever = self.vector_store.as_retriever(k=8) # Optimized k value
            logging.info("Successfully connected to Azure AI Search.")
        except Exception as e:
            logging.error(f"Could not connect to Azure AI Search. Error: {e}")
            self.vector_store = None
            self.retriever = None
        
        self.rag_chain = self._build_rag_chain()

    def _build_rag_chain(self):
        """Builds the RAG chain with a unified prompt."""
        template = """
        Anda adalah asisten AI untuk Universitas Hamzanwadi.
        Tugas Anda adalah menjawab pertanyaan HANYA berdasarkan 'Konteks' yang diberikan.

        ATURAN:
        1.  Jika pertanyaan relevan dengan konteks, berikan jawaban yang informatif dan akurat dari sumber yang disediakan.
        2.  Jika pertanyaan TIDAK relevan (misalnya, tentang ibu kota Prancis, mengerjakan PR), tolak dengan sopan dan arahkan kembali pengguna untuk bertanya tentang Universitas Hamzanwadi. Jangan menjawab pertanyaan di luar topik.
        3.  Selalu jawab dalam Bahasa Indonesia.
        4.  Jika konteks tidak berisi jawaban, katakan Anda tidak dapat menemukan informasinya.
        5.  Jika sesuai, arahkan percakapan untuk membahas Fakultas Teknik.

        Konteks:
        {context}

        Pertanyaan:
        {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        return (
            prompt
            | self.llm
            | StrOutputParser()
        )

    def ingest_data(self, file_paths: list[str] = None, urls: list[str] = None):
        """Ingests data from PDF files and URLs, creates embeddings, and adds them to Azure AI Search."""
        if not self.vector_store:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure AI Search is not available. Please check the configuration."
            )

        if not file_paths and not urls:
            raise ValueError("Either file_paths or urls must be provided.")

        docs = []
        if file_paths:
            for path in file_paths:
                loader = PyPDFLoader(path)
                docs.extend(loader.load())
        
        if urls:
            loader = WebBaseLoader(urls)
            docs.extend(loader.load())

        if not docs:
            logging.info("No documents loaded. Ingestion skipped.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)

        logging.info(f"Ingesting {len(split_docs)} document chunks into Azure AI Search...")
        
        self.vector_store.add_documents(documents=split_docs)
        
        logging.info("Ingestion complete.")

    def _format_docs(self, docs):
        if not docs:
            return "Tidak ada konteks yang relevan ditemukan."
        formatted_docs = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown Source').split('/')[-1]
            page = doc.metadata.get('page_label', doc.metadata.get('page', 'Unknown Page'))
            formatted_docs.append(f"Content from {source} (Page {page}):\n{doc.page_content}")
        return "\n\n".join(formatted_docs)

    def get_answer(self, query: str) -> ChatResponse:
        logging.info(f"get_answer method called with query: {query}")
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not available. Please check configuration and ingest data."
            )

        relevant_docs = self.retriever.get_relevant_documents(query)
        context_string = self._format_docs(relevant_docs)

        answer = self.rag_chain.invoke({"context": context_string, "question": query})

        sources = [
            Source(
                source=doc.metadata.get('source', 'Unknown'),
                content=doc.page_content
            ) for doc in relevant_docs
        ]

        debug_info = {
            "relevant_docs": [doc.dict() for doc in relevant_docs],
            "context_string": context_string
        }

        return ChatResponse(answer=answer, sources=sources, debug_info=debug_info)

# --- Singleton Instance ---
# Create a single, reusable instance of the RAGService.
# This is more efficient than creating a new instance for every request.
rag_service_instance = RAGService()
